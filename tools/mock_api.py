from __future__ import annotations

import json
import secrets
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


HOST = "127.0.0.1"
PORT = 8765
PAIRINGS: dict[str, dict[str, object]] = {}
TOKEN = "local-development-token"


class Handler(BaseHTTPRequestHandler):
    server_version = "StudynMock/0.1"

    def _json_body(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8"))

    def _send_json(self, status: int, body: dict[str, object]) -> None:
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send_html(self, status: int, body: str) -> None:
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _authorized(self) -> bool:
        return self.headers.get("Authorization") == f"Bearer {TOKEN}"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/verify":
            self._send_json(404, {"error": "not_found"})
            return
        code = parse_qs(parsed.query).get("user_code", [""])[0]
        self._send_html(
            200,
            "<!doctype html><meta charset='utf-8'><title>Studyn local</title>"
            "<h1>Authorize Studyn Anki Sync</h1>"
            f"<p>Code: <strong>{code}</strong></p>"
            "<form method='post' action='/verify'>"
            f"<input type='hidden' name='user_code' value='{code}'>"
            "<button type='submit'>Authorize device</button></form>",
        )

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/verify":
            length = int(self.headers.get("Content-Length", "0"))
            form = parse_qs(self.rfile.read(length).decode("utf-8"))
            code = form.get("user_code", [""])[0]
            for pairing in PAIRINGS.values():
                if pairing["userCode"] == code:
                    pairing["approved"] = True
            self._send_html(200, "<h1>Device authorized. Return to Anki.</h1>")
            return

        body = self._json_body()
        if parsed.path == "/api/v1/anki/device-authorizations":
            device_code = secrets.token_urlsafe(24)
            user_code = secrets.token_hex(4).upper()
            PAIRINGS[device_code] = {"userCode": user_code, "approved": False}
            port = int(self.server.server_address[1])
            verification = f"http://{HOST}:{port}/verify"
            self._send_json(
                201,
                {
                    "deviceCode": device_code,
                    "userCode": user_code,
                    "verificationUri": verification,
                    "verificationUriComplete": f"{verification}?user_code={user_code}",
                    "expiresIn": 600,
                    "interval": 2,
                },
            )
            return

        if parsed.path == "/api/v1/anki/token":
            pairing = PAIRINGS.get(str(body.get("deviceCode", "")))
            if not pairing:
                self._send_json(400, {"error": "expired_token"})
            elif not pairing["approved"]:
                self._send_json(400, {"error": "authorization_pending"})
            else:
                self._send_json(
                    200,
                    {
                        "accessToken": TOKEN,
                        "deviceId": "local-device",
                        "displayName": "Local account",
                    },
                )
            return

        if parsed.path == "/api/v1/anki/sync":
            if not self._authorized():
                self._send_json(401, {"error": "invalid_token"})
                return
            print(json.dumps(body, indent=2, ensure_ascii=False))
            self._send_json(
                200,
                {
                    "acceptedDays": len(body.get("days", [])),
                    "syncedAt": datetime.now(timezone.utc).isoformat(),
                },
            )
            return

        self._send_json(404, {"error": "not_found"})

    def do_DELETE(self) -> None:
        if not self._authorized():
            self._send_json(401, {"error": "invalid_token"})
            return
        self._send_json(200, {"revoked": True})

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[{self.log_date_time_string()}] {fmt % args}")


if __name__ == "__main__":
    print(f"Studyn mock API: http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
