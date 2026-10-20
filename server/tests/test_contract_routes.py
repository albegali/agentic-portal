import http.client
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests.support import make_skeleton  # noqa: E402
from portal_server import app  # noqa: E402
from portal_server.contract import CONTRACT_BUILT_FOR  # noqa: E402

TOKEN = "c" * 43
EXTRA = {("GET", "/api/data"): lambda root: {"ok": True}}


class RoutesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "web" / "dist").mkdir(parents=True)
        (self.root / "VERSION").write_text("9.9.9\n")

    def tearDown(self):
        self.tmp.cleanup()

    def start(self):
        routes = {**app.API_ROUTES, **EXTRA}
        self.server = app.create_server("127.0.0.1", 0, self.root, self.root / "web" / "dist", token=TOKEN, routes=routes)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.addCleanup(lambda: (self.server.shutdown(), self.server.server_close()))
        self.port = self.server.server_address[1]

    def req(self, method, path, auth=True):
        conn = http.client.HTTPConnection("127.0.0.1", self.port)
        headers = {"Authorization": "Bearer " + TOKEN} if auth else {}
        if method == "POST":
            headers.update({"Content-Type": "application/json", "Origin": "http://127.0.0.1:%d" % self.port})
        conn.request(method, path, body=b"{}" if method == "POST" else None, headers=headers)
        resp = conn.getresponse()
        body = json.loads(resp.read() or b"null")
        conn.close()
        return resp.status, body

    def test_compatible_skeleton_data_routes_work(self):
        make_skeleton(self.root)
        self.start()
        self.assertEqual(self.req("GET", "/api/data"), (200, {"ok": True}))
        status, body = self.req("GET", "/api/contract")
        self.assertEqual((status, body["state"], body["contract_version"], body["built_for"]), (200, "compatible", "1.0", "1.0"))
        self.assertIsNone(body["recovery"])

    def test_missing_skeleton_409_shape_and_exempt_routes(self):  # AC2
        self.start()
        status, body = self.req("GET", "/api/data")
        self.assertEqual(status, 409)
        err = body["error"]
        self.assertEqual(err["code"], "contract_incompatible")
        self.assertTrue(err["message"])
        self.assertEqual(set(err["recovery"]), {"summary", "steps", "command", "runnable"})
        self.assertIs(err["recovery"]["runnable"], False)
        self.assertEqual(self.req("GET", "/api/health")[0], 200)
        status, body = self.req("GET", "/api/contract")
        self.assertEqual((status, body["state"]), (200, "missing"))
        self.assertEqual(self.req("GET", "/api/nothing")[0], 404)  # unknown paths stay 404

    def test_major_mismatch_reported(self):  # AC2
        make_skeleton(self.root, contract="2.0")
        self.start()
        self.assertEqual(self.req("GET", "/api/data")[0], 409)
        self.assertEqual(self.req("GET", "/api/contract")[1]["state"], "incompatible")

    def test_recheck_recovers_without_restart(self):  # AC6
        make_skeleton(self.root, contract="2.0")
        self.start()
        self.assertEqual(self.req("GET", "/api/data")[0], 409)
        make_skeleton(self.root, contract="1.0")
        status, body = self.req("POST", "/api/contract/recheck")
        self.assertEqual((status, body["state"]), (200, "compatible"))
        self.assertEqual(self.req("GET", "/api/data")[0], 200)

    def test_contract_routes_need_the_token(self):
        self.start()
        self.assertEqual(self.req("GET", "/api/contract", auth=False)[0], 401)
        self.assertEqual(self.req("POST", "/api/contract/recheck", auth=False)[0], 401)

    def test_health_carries_contract_and_skeleton(self):  # AC7
        make_skeleton(self.root)
        self.start()
        body = self.req("GET", "/api/health", auth=False)[1]
        self.assertEqual(body["contract"], {"built_for": CONTRACT_BUILT_FOR, "skeleton_contract": "1.0"})
        self.assertEqual((body["skeleton"], body["skeleton_version"], body["contract_version"]), ("1.2.0", "1.2.0", "1.0"))
        self.assertEqual((body["status"], body["portal_version"]), ("ok", "9.9.9"))

    def test_health_unknown_when_skeleton_missing(self):  # AC7
        self.start()
        body = self.req("GET", "/api/health", auth=False)[1]
        self.assertEqual(body["contract"], {"built_for": CONTRACT_BUILT_FOR, "skeleton_contract": "unknown"})
        self.assertEqual((body["skeleton"], body["skeleton_version"], body["contract_version"]), ("unknown",) * 3)

    def test_new_routes_are_registered_for_the_enumeration_test(self):
        self.assertIn(("GET", "/api/contract"), app.API_ROUTES)
        self.assertIn(("POST", "/api/contract/recheck"), app.API_ROUTES)


if __name__ == "__main__":
    unittest.main()
