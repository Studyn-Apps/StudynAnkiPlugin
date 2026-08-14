import unittest
from io import BytesIO
from http.server import ThreadingHTTPServer
from threading import Thread
from unittest.mock import patch
from urllib.error import HTTPError

from studyn.api import ApiClient, ApiError, is_terminal_device_error
from studyn.models import DailyStats, StatsSnapshot
from tools.mock_api import HOST, PAIRINGS, TOKEN, Handler


class CapturingClient(ApiClient):
    def __init__(self):
        super().__init__("https://studyn.org/api/v1/anki")
        self.last_request = None

    def _request(self, method, path, payload=None, access_token=None):
        self.last_request = (method, path, payload, access_token)
        if path == "device-authorizations":
            return 201, {
                "deviceCode": "device-code",
                "userCode": "ABCD-EFGH",
                "verificationUri": "https://studyn.org/anki/connect",
                "expiresIn": 600,
                "interval": 5,
            }
        if path == "sync":
            return 200, {"acceptedDays": 1, "syncedAt": "2026-08-10T00:00:00Z"}
        return 200, {}


class ApiTests(unittest.TestCase):
    def test_terminal_device_errors_are_identified(self) -> None:
        self.assertTrue(is_terminal_device_error(ApiError("invalid", code="invalid_token")))
        self.assertTrue(
            is_terminal_device_error(ApiError("missing", code="device_not_found"))
        )
        self.assertFalse(is_terminal_device_error(ApiError("offline", retryable=True)))

    def test_structured_404_preserves_device_error_code(self) -> None:
        response = BytesIO(b'{"error":"device_not_found"}')
        error = HTTPError(
            "https://studyn.org/api/v1/anki/devices/missing",
            404,
            "Not Found",
            hdrs=None,
            fp=response,
        )
        client = ApiClient("https://studyn.org/api/v1/anki")

        with patch("studyn.api.urlopen", side_effect=error):
            with self.assertRaises(ApiError) as raised:
                client.revoke_device("token", "missing")

        self.assertEqual(raised.exception.code, "device_not_found")
        self.assertTrue(is_terminal_device_error(raised.exception))
        self.assertNotIn("Endpoint not found", str(raised.exception))

    def test_rejects_plain_http_outside_localhost(self) -> None:
        with self.assertRaises(ValueError):
            ApiClient("http://example.com/api")

    def test_pairing_contract(self) -> None:
        client = CapturingClient()
        session = client.begin_pairing("PC", "25.09")
        self.assertEqual(session.user_code, "ABCD-EFGH")
        self.assertEqual(client.last_request[1], "device-authorizations")

    def test_sync_payload_is_aggregate_only(self) -> None:
        client = CapturingClient()
        snapshot = StatsSnapshot(
            range_start="2026-08-10",
            range_end="2026-08-10",
            days=[DailyStats("2026-08-10", 1, 2000, 0, 0, 1, 0)],
            current_streak=1,
            lifetime_reviews=1,
            lifetime_review_time_ms=2000,
        )
        client.sync("token", snapshot, "sync-id", 4, "25.09")
        payload = client.last_request[2]
        serialized = str(payload).lower()
        self.assertNotIn("deck", serialized)
        self.assertNotIn("question", serialized)
        self.assertEqual(client.last_request[3], "token")

    def test_real_http_round_trip_against_mock_api(self) -> None:
        PAIRINGS.clear()
        server = ThreadingHTTPServer((HOST, 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            port = server.server_address[1]
            client = ApiClient(f"http://{HOST}:{port}/api/v1/anki", timeout=3)
            pairing = client.begin_pairing("Test", "test")
            PAIRINGS[pairing.device_code]["approved"] = True
            token = client.poll_for_token(pairing)
            self.assertEqual(token.access_token, TOKEN)

            snapshot = StatsSnapshot(
                range_start="2026-08-10",
                range_end="2026-08-10",
                days=[DailyStats("2026-08-10", 1, 1000, 0, 0, 1, 0)],
                current_streak=1,
                lifetime_reviews=1,
                lifetime_review_time_ms=1000,
            )
            result = client.sync(TOKEN, snapshot, "sync-id", 4, "test")
            self.assertEqual(result.accepted_days, 1)
            client.revoke_device(TOKEN, token.device_id)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
