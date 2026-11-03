"""Loopback by default; --host 0.0.0.0 supports an allowed platform preview."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

from domain import RouteService, ServiceError

BASE = Path(__file__).parent


def make_server(port=8765, service=None, host='127.0.0.1'):
    service = service or RouteService(state_file=BASE / 'output' / 'state.json')

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def send(self, status, payload, content_type='application/json; charset=utf-8'):
            body = payload if isinstance(payload, bytes) else json.dumps(payload, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(body)

        def dispatch(self, patch=False):
            url = urlsplit(self.path)
            path = unquote(url.path)
            query = parse_qs(url.query, keep_blank_values=True)
            parts = path.strip('/').split('/')
            try:
                if patch:
                    if len(parts) != 3 or parts[:2] != ['api', 'routes']:
                        raise ServiceError('경로 없음', 404)
                    if self.headers.get_content_type() != 'application/json':
                        raise ServiceError('application/json 필요', 415)
                    try:
                        size = int(self.headers.get('Content-Length', '0'))
                    except ValueError:
                        raise ServiceError('Content-Length 오류')
                    if size <= 0 or size > 16384:
                        raise ServiceError('본문 크기 오류', 413)
                    try:
                        body = json.loads(self.rfile.read(size).decode('utf-8'))
                    except (ValueError, UnicodeError):
                        raise ServiceError('JSON 오류')
                    return self.send(200, service.update(parts[2], body))
                if path == '/api/routes':
                    return self.send(200, service.list_routes(query.get('q', [''])[0], query.get('active', ['all'])[0]))
                if len(parts) == 3 and parts[:2] == ['api', 'routes']:
                    return self.send(200, service.detail(parts[2]))
                if len(parts) == 4 and parts[:2] == ['api', 'stops'] and parts[3] == 'routes':
                    return self.send(200, service.reverse(parts[2]))
                if path == '/api/quality':
                    return self.send(200, service.quality())
                static = {'/': ('index.html', 'text/html; charset=utf-8'),
                          '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
                          '/style.css': ('style.css', 'text/css; charset=utf-8')}
                if path in static:
                    filename, content_type = static[path]
                    return self.send(200, (BASE / 'web' / filename).read_bytes(), content_type)
                raise ServiceError('경로 없음', 404)
            except ServiceError as e:
                self.send(e.status, {'error': str(e)})
            except OSError:
                self.send(500, {'error': '파일 처리 실패. 저장 상태를 확인하세요'})

        def do_GET(self):
            self.dispatch()

        def do_PATCH(self):
            self.dispatch(patch=True)

        def do_POST(self):
            self.send(405, {'error': '지원하지 않는 메서드'})

    return ThreadingHTTPServer((host, port), Handler)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--host', choices=('127.0.0.1', '0.0.0.0'), default='127.0.0.1')
    args = parser.parse_args()
    server = make_server(args.port, host=args.host)
    print(f'http://127.0.0.1:{server.server_port}', flush=True)
    print(json.dumps({'bind_host': server.server_address[0], 'port': server.server_port}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
