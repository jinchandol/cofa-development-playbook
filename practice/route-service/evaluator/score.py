"""Compare predeclared defect IDs/rows with observed diagnostics and execution evidence."""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from domain import RouteService
from profile_data import hashes


def score():
    truth = json.loads((Path(__file__).parent / 'defects.json').read_text(encoding='utf-8'))
    service = RouteService()
    issues = service.quality()['issues']
    detected, missed, matches = [], [], []
    for defect in truth['data_defects']:
        observed = sorted({row for item in issues if item['code'] == defect['code']
                           and item['file'] == defect['file'] for row in item['rows']})
        found = set(defect['rows']).issubset(observed)
        (detected if found else missed).append(defect['id'])
        matches.append({'id': defect['id'], 'file': defect['file'], 'code': defect['code'],
                        'expected_rows': defect['rows'], 'observed_rows_for_code': observed, 'detected': found})
    valid = {
        'loop_occurrences_preserved': [s['stop_id'] for s in service.detail('R1')['stops']] == ['S1', 'S2', 'S1', 'S3'],
        'shared_stop_inactive_route_included': [r['route_id'] for r in service.reverse('S3')['routes']] == ['R1', 'R4'],
    }
    baseline_path = BASE / 'rehearsal' / 'baseline.json'
    final_path = BASE / 'rehearsal' / 'evidence.json'
    initial = json.loads(baseline_path.read_text(encoding='utf-8')) if baseline_path.exists() else {}
    final = json.loads(final_path.read_text(encoding='utf-8')) if final_path.exists() else {}
    initial_review = next((r for r in initial.get('results', []) if r['role'] == 'reviewer'), {})
    final_review = next((r for r in final.get('results', []) if r['role'] == 'reviewer'), {})
    seeded = []
    for defect in truth['seeded_implementation_defects']:
        found = 'FAIL: ' + defect['test'] in initial_review.get('output', '')
        retested = (final_review.get('status') == 'PASS' and final_review.get('summary', {}).get('passed', 0) > 0
                    and defect['test'] in final_review.get('output', ''))
        seeded.append({'id': defect['id'], 'detected_in_baseline': found, 'retest_passed': retested})
    source_unchanged = initial.get('pre_test_sha256') == final.get('post_test_sha256') == hashes()
    results = {r['role']: r for r in final.get('results', [])}
    required_roles = {'developer', 'reviewer', 'verification_harness', 'cli_startup'}
    final_execution_passed = (final.get('stage') == 'final' and required_roles.issubset(results)
                              and all(results[role].get('status') == 'PASS' and results[role].get('exit_code') == 0
                                      for role in required_roles)
                              and all(results[role].get('summary', {}).get('passed', 0) > 0
                                      for role in ('developer', 'reviewer', 'verification_harness'))
                              and not any(r.get('status') == 'FAIL' for r in results.values()))
    result = {
        'interpretation': 'non-blind synthetic rehearsal; not exam performance',
        'data_detection': {'detected': len(detected), 'total': len(truth['data_defects']),
                           'rate': len(detected) / len(truth['data_defects']), 'missed': missed, 'matches': matches},
        'valid_case_preservation': valid,
        'seeded_implementation_detection': seeded,
        'source_unchanged_since_baseline': source_unchanged,
        'final_execution_passed': final_execution_passed,
        'suite_counts': {role: r['summary'] for role, r in results.items() if 'summary' in r},
        'unmeasured': ['blind interview discovery', 'independent reviewer effectiveness',
                      '180-minute performance', 'visual browser interaction', 'large data/concurrent processes'],
    }
    success = (not missed and all(valid.values()) and source_unchanged and final_execution_passed
               and all(r['detected_in_baseline'] and r['retest_passed'] for r in seeded))
    return result, success


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    result, success = score()
    (BASE / 'rehearsal' / 'score.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if success else 1)
