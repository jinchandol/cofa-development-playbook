import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import make_server
from domain import RouteService, ServiceError
from profile_data import hashes, profile


class DeveloperTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.state = Path(self.temp.name) / 'state.json'
        self.service = RouteService(state_file=self.state)

    def test_profile_and_source_immutable(self):
        before = hashes()
        data = profile()
        self.assertEqual([data['files'][f]['rows'] for f in ('routes.csv', 'stops.csv', 'route_stops.csv')], [5, 6, 16])
        self.assertEqual(data['relationships']['naive_inner_join_rows'], 18)
        self.service.update('R1', {'name': '새 이름', 'active': False})
        self.assertEqual(hashes(), before)

    def test_list_search_filter(self):
        self.assertEqual([r['route_id'] for r in self.service.list_routes()], ['R1', 'R2', 'R4'])
        self.assertEqual(len(self.service.list_routes('  순환  ')), 1)
        self.assertEqual([r['route_id'] for r in self.service.list_routes(active='false')], ['R4'])
        self.assertEqual(self.service.list_routes('없는 이름'), [])
        with self.assertRaises(ServiceError):
            self.service.list_routes(active='yes')

    def test_golden_route_and_blocked(self):
        stops = self.service.detail('R1')['stops']
        self.assertEqual([s['stop_id'] for s in stops], ['S1', 'S2', 'S1', 'S3'])
        self.assertEqual([s['sequence'] for s in stops], [1, 2, 3, 4])
        self.assertEqual(self.service.detail('R1')['stop_count'], 4)
        self.assertTrue(self.service.detail('R2')['blocked'])
        self.assertEqual(self.service.detail('R2')['stops'], [])
        self.service.update('R2', {'active': False})
        self.assertTrue(self.service.detail('R2')['blocked'])

    def test_reverse_membership(self):
        self.assertEqual([r['route_id'] for r in self.service.reverse('S3')['routes']], ['R1', 'R4'])
        self.assertEqual([r['route_id'] for r in self.service.reverse('S1')['routes']], ['R1'])
        self.assertEqual(self.service.reverse('S4')['routes'], [])
        for sid in ('S5', 'SX'):
            with self.assertRaises(ServiceError):
                self.service.reverse(sid)

    def test_edit_persists(self):
        self.service.update('R1', {'name': '  New Route  ', 'active': False})
        fresh = RouteService(state_file=self.state)
        self.assertEqual(fresh.detail('R1')['name'], 'New Route')
        self.assertFalse(fresh.detail('R1')['active'])
        self.assertEqual(len(fresh.list_routes('new route')), 1)

    def test_quality_balances(self):
        counts = self.service.quality()['counts']
        expected = {'routes.csv': (5, 3, 0, 2), 'stops.csv': (6, 4, 1, 1), 'route_stops.csv': (16, 5, 1, 10)}
        for filename, values in expected.items():
            self.assertEqual(tuple(counts[filename][k] for k in ('input', 'accepted', 'deduplicated', 'quarantined')), values)
            self.assertEqual(counts[filename]['input'], sum(counts[filename][k] for k in ('accepted', 'deduplicated', 'quarantined')))

    def test_http_end_to_end(self):
        server = make_server(0, self.service)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            root = f'http://127.0.0.1:{server.server_port}'
            for path in ('/', '/app.js', '/style.css'):
                with urlopen(root + path, timeout=3) as response:
                    self.assertEqual(response.status, 200)
                    self.assertTrue(response.read())
            with urlopen(root + '/api/routes', timeout=3) as response:
                self.assertEqual(len(json.load(response)), 3)
            request = Request(root + '/api/routes/R1', json.dumps({'name': 'HTTP 수정', 'active': False}).encode(), {'Content-Type': 'application/json'}, method='PATCH')
            with urlopen(request, timeout=3) as response:
                self.assertEqual(json.load(response)['name'], 'HTTP 수정')
            with urlopen(root + '/api/stops/S3/routes', timeout=3) as response:
                self.assertEqual(len(json.load(response)['routes']), 2)
            with urlopen(root + '/api/quality', timeout=3) as response:
                self.assertEqual(json.load(response)['counts']['route_stops.csv']['accepted'], 5)
            with self.assertRaises(HTTPError) as ctx:
                urlopen(root + '/api/routes/R3', timeout=3)
            self.assertEqual(ctx.exception.code, 404)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

    def test_platform_preview_binding(self):
        server = make_server(0, self.service, host='0.0.0.0')
        self.assertEqual(server.server_address[0], '0.0.0.0')
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with urlopen(f'http://127.0.0.1:{server.server_port}/api/routes/R1', timeout=3) as response:
                self.assertEqual(json.load(response)['stop_count'], 4)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


if __name__ == '__main__':
    unittest.main()
