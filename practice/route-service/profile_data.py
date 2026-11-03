"""No business policy: raw schema, keys, relationships, join inflation and hashes."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

DATA = Path(__file__).parent / 'data'


def read(name, directory=DATA):
    with (Path(directory) / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def hashes(directory=DATA):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(directory).glob('*.csv'))}


def profile(directory=DATA):
    names = ('routes.csv', 'stops.csv', 'route_stops.csv')
    tables = {n: read(n, directory) for n in names}
    report = {'sha256': hashes(directory), 'files': {}}
    for name, rows in tables.items():
        cols = list(rows[0]) if rows else []
        tuples = Counter(tuple(r.items()) for r in rows)
        report['files'][name] = {
            'rows': len(rows), 'schema': cols,
            'observed_types': {c: sorted(set(
                'missing' if not r[c] else 'integer' if r[c].lstrip('-').isdigit()
                else 'boolean-text' if r[c] in ('true', 'false') else 'text'
                for r in rows)) for c in cols},
            'missing': {c: sum(not r[c].strip() for r in rows) for c in cols},
            'exact_duplicate_excess': sum(v - 1 for v in tuples.values()),
        }
    rc = Counter(r['route_id'] for r in tables['routes.csv'])
    sc = Counter(r['stop_id'] for r in tables['stops.csv'])
    edges = tables['route_stops.csv']
    report['keys'] = {'route_id_duplicates': {k: v for k, v in rc.items() if v > 1},
                      'stop_id_duplicates': {k: v for k, v in sc.items() if v > 1}}
    composite = Counter((r['route_id'], r['sequence']) for r in edges)
    report['relationships'] = {
        'orphan_route_rows': [i for i, r in enumerate(edges, 1) if r['route_id'] not in rc],
        'orphan_stop_rows': [i for i, r in enumerate(edges, 1) if r['stop_id'] not in sc],
        'nonpositive_or_missing_sequence_rows': [i for i, r in enumerate(edges, 1)
              if not r['sequence'].isdigit() or int(r['sequence']) <= 0],
        'route_sequence_duplicate_groups': [list(k) + [v] for k, v in composite.items() if v > 1],
        'shared_stop_routes': {s: sorted({r['route_id'] for r in edges if r['stop_id'] == s})
              for s in sorted(sc) if len({r['route_id'] for r in edges if r['stop_id'] == s}) > 1},
        'raw_edges': len(edges),
        'naive_inner_join_rows': sum(rc[r['route_id']] * sc[r['stop_id']] for r in edges),
        'unmatched_edge_rows': sum(not rc[r['route_id']] or not sc[r['stop_id']] for r in edges),
    }
    return report


if __name__ == '__main__':
    print(json.dumps(profile(), ensure_ascii=False, indent=2))
