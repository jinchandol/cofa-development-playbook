"""Start the real CLI and verify HTTP from a separate process, then stop it."""
import json
import os
import queue
import subprocess
import sys
import threading
from pathlib import Path
from urllib.request import urlopen

BASE = Path(__file__).resolve().parents[1]


def check_host(host):
    arguments = ['app.py', '--port', '0']
    if host != '127.0.0.1':
        arguments += ['--host', host]
    child = subprocess.Popen([sys.executable, *arguments], cwd=BASE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                             encoding='utf-8', env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
    started = queue.Queue()
    def read_startup():
        started.put((child.stdout.readline().strip(), child.stdout.readline().strip()))
    threading.Thread(target=read_startup, daemon=True).start()
    try:
        root, binding = started.get(timeout=10)
        if not root.startswith('http://127.0.0.1:'):
            raise RuntimeError('CLI URL이 출력되지 않았습니다: ' + root)
        binding = json.loads(binding)
        if binding['bind_host'] != host:
            raise RuntimeError('요청한 바인딩 주소가 적용되지 않았습니다')
        observed = {}
        for path in ('/', '/app.js', '/api/routes/R1', '/api/stops/S3/routes'):
            with urlopen(root + path, timeout=3) as response:
                body = response.read()
                assert response.status == 200 and body
                observed[path] = response.status
                if path == '/api/routes/R1':
                    assert json.loads(body)['stop_count'] == 4
        print(json.dumps({'command': 'python ' + ' '.join(arguments), 'bind_host': binding['bind_host'],
                          'http_status': observed,
                          'process_stopped_after_check': True}))
    finally:
        child.terminate()
        child.communicate(timeout=5)


if __name__ == '__main__':
    for host in ('127.0.0.1', '0.0.0.0'):
        check_host(host)
