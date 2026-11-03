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


def main():
    child = subprocess.Popen([sys.executable, 'app.py', '--port', '0'], cwd=BASE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                             encoding='utf-8', env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
    started = queue.Queue()
    threading.Thread(target=lambda: started.put(child.stdout.readline().strip()), daemon=True).start()
    try:
        root = started.get(timeout=10)
        if not root.startswith('http://127.0.0.1:'):
            raise RuntimeError('CLI URL이 출력되지 않았습니다: ' + root)
        observed = {}
        for path in ('/', '/app.js', '/api/routes/R1', '/api/stops/S3/routes'):
            with urlopen(root + path, timeout=3) as response:
                body = response.read()
                assert response.status == 200 and body
                observed[path] = response.status
                if path == '/api/routes/R1':
                    assert json.loads(body)['stop_count'] == 4
        print(json.dumps({'command': 'python app.py --port 0', 'http_status': observed,
                          'process_stopped_after_check': True}))
    finally:
        child.terminate()
        child.communicate(timeout=5)


if __name__ == '__main__':
    main()
