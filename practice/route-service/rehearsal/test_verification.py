"""CLI regressions for false-positive test verification; synthetic fixtures only."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RUNNER = Path(__file__).with_name('run_suite.py')


class VerificationTests(unittest.TestCase):
    def check_fixture(self, source, expected_exit):
        with tempfile.TemporaryDirectory() as directory:
            if source:
                (Path(directory) / 'test_fixture.py').write_text(source, encoding='utf-8')
            result = subprocess.run(
                [sys.executable, str(RUNNER), '--start', directory],
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'},
                capture_output=True, text=True, encoding='utf-8', timeout=10)
            self.assertEqual(result.returncode, expected_exit, result.stdout + result.stderr)
            summary = json.loads(result.stdout)
            self.assertEqual(summary['exit_code'], expected_exit)
            return summary

    def test_no_tests_is_incomplete(self):
        summary = self.check_fixture(None, 2)
        self.assertEqual((summary['status'], summary['run'], summary['passed']), ('INCOMPLETE', 0, 0))

    def test_all_skipped_is_incomplete(self):
        summary = self.check_fixture('''import unittest
class Placeholder(unittest.TestCase):
    @unittest.skip('not implemented')
    def test_placeholder(self):
        pass
''', 2)
        self.assertEqual((summary['executed'], summary['skipped']), (0, 1))

    def test_failed_assertion_is_failure(self):
        summary = self.check_fixture('''import unittest
class Broken(unittest.TestCase):
    def test_wrong_result(self):
        self.assertEqual(1, 2)
''', 1)
        self.assertEqual((summary['status'], summary['failures']), ('FAIL', 1))

    def test_import_error_is_failure(self):
        summary = self.check_fixture('raise ImportError("synthetic missing dependency")\n', 1)
        self.assertEqual((summary['status'], summary['errors']), ('FAIL', 1))

    def test_pass_and_skip_are_counted_separately(self):
        summary = self.check_fixture('''import unittest
class Mixed(unittest.TestCase):
    def test_valid_result(self):
        self.assertEqual(sum([1, 2]), 3)
    @unittest.skip('optional environment')
    def test_unavailable(self):
        pass
''', 0)
        self.assertEqual((summary['run'], summary['executed'], summary['passed'], summary['skipped']), (2, 1, 1, 1))

    def test_expected_failure_only_is_incomplete(self):
        summary = self.check_fixture('''import unittest
class KnownGap(unittest.TestCase):
    @unittest.expectedFailure
    def test_not_ready(self):
        self.assertEqual(1, 2)
''', 2)
        self.assertEqual((summary['expected_failures'], summary['passed']), (1, 0))


if __name__ == '__main__':
    unittest.main()
