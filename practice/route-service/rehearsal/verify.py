"""Record real subprocess results. Run from route-service after resolving policies."""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from profile_data import hashes, profile


def run(stage):
    sys.stdout.reconfigure(encoding='utf-8')
    environment = {**os.environ, 'PYTHONIOENCODING': 'utf-8'}
    before = hashes()
    commands = [
        ('developer', [sys.executable, 'rehearsal/run_suite.py', '--start', 'tests']),
        ('reviewer', [sys.executable, 'rehearsal/run_suite.py', '--start', 'reviewer']),
        ('verification_harness', [sys.executable, 'rehearsal/run_suite.py', '--start', 'rehearsal', '--pattern', 'test_verification.py']),
    ]
    if stage == 'final':
        commands.append(('cli_startup', [sys.executable, 'rehearsal/cli_smoke.py']))
    if shutil.which('node'):
        commands.append(('javascript_syntax', ['node', '--check', 'web/app.js']))
    results = []
    for role, command in commands:
        result = subprocess.run(command, cwd=BASE, env=environment, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60)
        # Keep evidence portable: commands and tracebacks use relative project paths.
        output = (result.stdout + result.stderr).replace(str(BASE), '<route-service>')
        entry = {'role': role, 'command': ['python' if x == sys.executable else x for x in command],
                 'required': role != 'javascript_syntax',
                 'status': 'PASS' if result.returncode == 0 else 'INCOMPLETE' if result.returncode == 2 else 'FAIL',
                 'exit_code': result.returncode, 'output': output}
        if role in ('developer', 'reviewer', 'verification_harness'):
            summary = json.loads(result.stdout)
            entry['summary'] = summary
            if result.returncode == 0 and (summary.get('passed', 0) == 0 or summary.get('executed', 0) == 0):
                entry.update(status='INCOMPLETE', exit_code=2)
        results.append(entry)
        print(json.dumps(entry, ensure_ascii=False), flush=True)
    if not shutil.which('node'):
        skipped = {'role': 'javascript_syntax', 'required': False, 'status': 'SKIP',
                   'command': ['node', '--check', 'web/app.js'], 'exit_code': None,
                   'output': 'Node unavailable; JavaScript syntax check was not executed'}
        results.append(skipped)
        print(json.dumps(skipped), flush=True)
    evidence = {'timestamp_utc': datetime.now(timezone.utc).isoformat(),
                'stage': stage, 'python': platform.python_version(),
                'environment': {'platform': platform.system(), 'node_available': bool(shutil.which('node')),
                                'server_binding': '127.0.0.1', 'platform_browser_preview': 'not checked'},
                'review_independence': 'same author, sequential role review, non-blind',
                'raw_profile': profile(), 'pre_test_sha256': before,
                'post_test_sha256': hashes(), 'results': results,
                'browser_visual_check': 'not performed'}
    destination = Path(__file__).parent / ('baseline.json' if stage == 'baseline' else 'evidence.json')
    destination.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if before != hashes() or any(r['status'] == 'FAIL' for r in results):
        return 1
    if any(r['required'] and r['status'] != 'PASS' for r in results):
        return 2
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', choices=('baseline', 'final'), default='final')
    args = parser.parse_args()
    if args.stage == 'baseline' and (Path(__file__).parent / 'baseline.json').exists():
        parser.error('기존 baseline은 덮어쓰지 않습니다')
    raise SystemExit(run(args.stage))
