"""Sequential review counterexamples; not an independent reviewer context."""
import json
import shutil
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import make_server
from domain import BASE, RouteService, ServiceError


class ReviewTests(unittest.TestCase):
    def test_boolean_string_rejected(self):
        service = RouteService()
        before = service.detail('R1')
        with self.assertRaises(ServiceError):
            service.update('R1', {'active': 'false'})
        self.assertEqual(service.detail('R1'), before)

    def test_patch_boundaries(self):
        for patch in ({'active': 0}, {'active': None}, {'active': []}, {'name': ' '}, {'name': 'x' * 81}, {'name': 1}, {'route_id': 'R8'}, {}, [], None):
            with self.subTest(patch=patch), self.assertRaises(ServiceError):
                RouteService().update('R1', patch)
        service = RouteService()
        self.assertEqual(len(service.update('R1', {'name': 'x' * 80})['name']), 80)

    def test_row_order_cannot_choose_conflict_winner(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            for path in (BASE / 'data').glob('*.csv'):
                lines = path.read_text(encoding='utf-8').splitlines()
                (directory / path.name).write_text('\n'.join([lines[0]] + lines[1:][::-1]) + '\n', encoding='utf-8')
            normal, reversed_rows = RouteService(), RouteService(data_dir=directory)
            self.assertEqual(normal.list_routes(), reversed_rows.list_routes())
            self.assertEqual(normal.detail('R1'), reversed_rows.detail('R1'))
            self.assertEqual(normal.reverse('S3'), reversed_rows.reverse('S3'))

    def test_noncontiguous_sequences_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            for path in (BASE / 'data').glob('*.csv'):
                shutil.copyfile(path, directory / path.name)
            path = directory / 'route_stops.csv'
            text = path.read_text(encoding='utf-8').replace('R4,S3,1', 'R4,S3,7')
            path.write_text(text, encoding='utf-8')
            self.assertEqual(RouteService(data_dir=directory).detail('R4')['stops'][0]['sequence'], 7)

    def test_corrupt_state_fails_without_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'state.json'
            for content in ('{broken', '{"version":99,"routes":{}}', '{"version":1,"routes":{"RX":{"name":"x"}}}'):
                path.write_text(content, encoding='utf-8')
                with self.assertRaises(ValueError):
                    RouteService(state_file=path)
                self.assertEqual(path.read_text(encoding='utf-8'), content)

    def test_write_failure_does_not_change_memory(self):
        with tempfile.TemporaryDirectory() as folder:
            parent_file = Path(folder) / 'file'
            parent_file.write_text('not a directory', encoding='utf-8')
            service = RouteService(state_file=parent_file / 'state.json')
            before = service.detail('R1')
            with self.assertRaises(OSError):
                service.update('R1', {'name': 'lost update'})
            self.assertEqual(service.detail('R1'), before)

    def test_http_errors(self):
        server = make_server(0, RouteService())
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        root = f'http://127.0.0.1:{server.server_port}'
        cases = [('/api/routes?active=maybe', None, 'GET', 400),
                 ('/api/routes/unknown', None, 'GET', 404),
                 ('/../../data/routes.csv', None, 'GET', 404),
                 ('/api/routes/R1', b'{broken', 'PATCH', 400),
                 ('/api/routes/R1', b'{"active":"false"}', 'PATCH', 400),
                 ('/api/routes/R1', b'x' * 16385, 'PATCH', 413),
                 ('/api/routes/R1', b'{}', 'POST', 405)]
        try:
            for path, body, method, status in cases:
                with self.subTest(path=path, method=method, body=repr(body)[:60]):
                    request = Request(root + path, body, {'Content-Type': 'application/json'}, method=method)
                    with self.assertRaises(HTTPError) as ctx:
                        urlopen(request, timeout=3)
                    self.assertEqual(ctx.exception.code, status)
                    self.assertIn('error', json.load(ctx.exception))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


if __name__ == '__main__':
    unittest.main()
