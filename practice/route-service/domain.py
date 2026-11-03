"""Synthetic policy resolved in CONTRACT; source CSVs are never written."""
import csv
import json
import os
import tempfile
import threading
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).parent


class ServiceError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


class RouteService:
    def __init__(self, data_dir=None, state_file=None):
        self.data_dir = Path(data_dir) if data_dir else BASE / 'data'
        self.state_file = Path(state_file) if state_file else None
        self.lock = threading.RLock()
        self.issues, self.ledger = [], {}
        self.routes = self._entities('routes.csv', 'route_id', ('route_id', 'name', 'active'), 'route')
        self.stops = self._entities('stops.csv', 'stop_id', ('stop_id', 'name'), 'stop')
        self.blocked = set()
        self.edges = self._edges()
        self.overrides = {}
        if self.state_file and self.state_file.exists():
            state = json.loads(self.state_file.read_text(encoding='utf-8'))
            if not isinstance(state, dict) or state.get('version') != 1 or not isinstance(state.get('routes'), dict):
                raise ValueError('저장 상태 형식 오류: 덮어쓰지 않고 중단합니다')
            for rid, patch in state['routes'].items():
                if rid not in self.routes:
                    raise ValueError('저장 상태에 알 수 없는 노선: ' + rid)
                self.overrides[rid] = self._validate_patch(patch)

    def _read(self, filename, schema):
        with (self.data_dir / filename).open(encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != list(schema):
                raise ValueError(filename + ': 예상 스키마와 다릅니다')
            rows = list(reader)
        if any(None in r or any(v is None for v in r.values()) for r in rows):
            raise ValueError(filename + ': CSV 열 수 오류')
        self.ledger[filename] = [None] * len(rows)
        return [{k: v.strip() for k, v in r.items()} for r in rows]

    def _mark(self, filename, indexes, disposition, code=None, detail=''):
        for i in indexes:
            self.ledger[filename][i - 1] = {'row': i, 'disposition': disposition, 'reason': code}
        if code:
            self.issues.append({'file': filename, 'rows': sorted(indexes), 'code': code, 'detail': detail})

    def _entities(self, filename, key, schema, kind):
        groups = defaultdict(list)
        for i, row in enumerate(self._read(filename, schema), 1):
            groups[row[key]].append((i, row))
        result = {}
        for identity, group in groups.items():
            indexes = [i for i, _ in group]
            if len({tuple(row.items()) for _, row in group}) > 1:
                self._mark(filename, indexes, 'quarantined', 'conflicting_' + kind, identity)
                continue
            row = group[0][1]
            if not identity or not row['name'] or (kind == 'route' and row['active'] not in ('true', 'false')):
                self._mark(filename, indexes, 'quarantined', 'missing_' + kind, identity)
                continue
            result[identity] = dict(row)
            if kind == 'route':
                result[identity]['active'] = row['active'] == 'true'
            self._mark(filename, indexes[:1], 'accepted')
            if len(indexes) > 1:
                self._mark(filename, indexes[1:], 'deduplicated', 'duplicate_' + kind, identity)
        return result

    def _edges(self):
        filename = 'route_stops.csv'
        candidates, seen = [], set()
        for i, row in enumerate(self._read(filename, ('route_id', 'stop_id', 'sequence')), 1):
            rid, sid, seq = row['route_id'], row['stop_id'], row['sequence']
            if not rid or not sid:
                code = 'missing_reference'
            elif not seq.isascii() or not seq.isdigit() or int(seq) <= 0:
                code = 'invalid_sequence'
            elif rid not in self.routes:
                code = 'unresolved_route'
            elif sid not in self.stops:
                code = 'unresolved_stop'
            else:
                code = None
            if code:
                self._mark(filename, [i], 'quarantined', code, str(row))
                continue
            edge = (rid, sid, int(seq))
            if edge in seen:
                self._mark(filename, [i], 'deduplicated', 'duplicate_occurrence', str(edge))
                continue
            seen.add(edge)
            candidates.append((i, edge))
        slots = defaultdict(list)
        for i, (rid, sid, seq) in candidates:
            slots[rid, seq].append((i, sid))
        conflicts = set()
        for (rid, seq), items in slots.items():
            if len({sid for _, sid in items}) > 1:
                self.blocked.add(rid)
                indexes = [i for i, _ in items]
                conflicts.update(indexes)
                self._mark(filename, indexes, 'quarantined', 'sequence_conflict', f'{rid}:{seq}')
        accepted = []
        for i, (rid, sid, seq) in candidates:
            if rid in self.blocked:
                if i not in conflicts:
                    self._mark(filename, [i], 'quarantined', 'blocked_route_itinerary', rid)
            else:
                self._mark(filename, [i], 'accepted')
                accepted.append({'route_id': rid, 'stop_id': sid, 'sequence': seq})
        return sorted(accepted, key=lambda e: (e['route_id'], e['sequence']))

    def _summary(self, rid):
        return {**self.routes[rid], **self.overrides.get(rid, {}),
                'blocked': rid in self.blocked,
                'stop_count': sum(e['route_id'] == rid for e in self.edges)}

    def list_routes(self, query='', active='all'):
        if active not in ('all', 'true', 'false'):
            raise ServiceError('active 필터: all / true / false')
        with self.lock:
            rows = [self._summary(rid) for rid in sorted(self.routes)]
            return [r for r in rows if query.strip().casefold() in r['name'].casefold()
                    and (active == 'all' or r['active'] == (active == 'true'))]

    def detail(self, rid):
        with self.lock:
            if rid not in self.routes:
                raise ServiceError('노선 없음', 404)
            return {**self._summary(rid), 'stops': [
                {**self.stops[e['stop_id']], 'sequence': e['sequence']}
                for e in self.edges if e['route_id'] == rid]}

    def reverse(self, sid):
        if sid not in self.stops:
            raise ServiceError('정류장 없음', 404)
        with self.lock:
            ids = sorted({e['route_id'] for e in self.edges if e['stop_id'] == sid})
            return {'stop': self.stops[sid], 'routes': [self._summary(rid) for rid in ids]}

    @staticmethod
    def _validate_patch(patch):
        if not isinstance(patch, dict) or not patch or set(patch) - {'name', 'active'}:
            raise ServiceError('name / active 중 변경할 필드만 입력하세요')
        clean = {}
        if 'name' in patch:
            if not isinstance(patch['name'], str) or not 1 <= len(patch['name'].strip()) <= 80:
                raise ServiceError('이름은 공백 제외 1~80자')
            clean['name'] = patch['name'].strip()
        if 'active' in patch:
            if type(patch['active']) is not bool:
                raise ServiceError('active는 JSON boolean이어야 합니다')
            clean['active'] = patch['active']
        return clean

    def update(self, rid, patch):
        with self.lock:
            if rid not in self.routes:
                raise ServiceError('노선 없음', 404)
            clean = self._validate_patch(patch)
            updated = {**self.overrides, rid: {**self.overrides.get(rid, {}), **clean}}
            if self.state_file:
                self.state_file.parent.mkdir(parents=True, exist_ok=True)
                fd, temp = tempfile.mkstemp(dir=self.state_file.parent, prefix='state-', suffix='.tmp')
                try:
                    with os.fdopen(fd, 'w', encoding='utf-8') as f:
                        json.dump({'version': 1, 'routes': updated}, f, ensure_ascii=False)
                        f.flush()
                        os.fsync(f.fileno())
                    os.replace(temp, self.state_file)
                finally:
                    if os.path.exists(temp):
                        os.unlink(temp)
            self.overrides = updated
            return self.detail(rid)

    def quality(self):
        counts = {}
        for filename, ledger in self.ledger.items():
            assert all(item is not None for item in ledger), '미분류 원본 행'
            counts[filename] = {'input': len(ledger), **{state: sum(
                item['disposition'] == state for item in ledger)
                for state in ('accepted', 'deduplicated', 'quarantined')}}
        return {'counts': counts, 'issues': self.issues, 'ledger': self.ledger}
