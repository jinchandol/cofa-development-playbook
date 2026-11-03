"""Run unittest with measured evidence: 0=PASS, 1=FAIL, 2=INCOMPLETE.

An empty suite or a suite with no actual passing test must not pass verification.
This runner does not prove that tests cover all acceptance criteria.
"""
import argparse
import json
import sys
import unittest


class MeasuredResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed = 0

    def addSuccess(self, test):
        self.passed += 1
        super().addSuccess(test)


def run(start, pattern='test_*.py'):
    suite = unittest.defaultTestLoader.discover(start, pattern=pattern)
    loaded = suite.countTestCases()
    result = unittest.TextTestRunner(verbosity=2, resultclass=MeasuredResult).run(suite)
    if not result.wasSuccessful():
        exit_code, status = 1, 'FAIL'
    elif result.passed == 0:
        exit_code, status = 2, 'INCOMPLETE'
    else:
        exit_code, status = 0, 'PASS'
    summary = {'status': status, 'loaded': loaded, 'run': result.testsRun,
               'executed': result.testsRun - len(result.skipped),
               'passed': result.passed, 'skipped': len(result.skipped),
               'failures': len(result.failures), 'errors': len(result.errors),
               'expected_failures': len(result.expectedFailures),
               'unexpected_successes': len(result.unexpectedSuccesses),
               'exit_code': exit_code}
    return summary


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', required=True)
    parser.add_argument('--pattern', default='test_*.py')
    args = parser.parse_args()
    summary = run(args.start, args.pattern)
    print(json.dumps(summary))
    raise SystemExit(summary['exit_code'])
