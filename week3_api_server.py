from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from app.services.portfolio_api_service import PortfolioApiService
from app.storage.sqlite_repo import PortfolioRepository


class PortfolioApiHandler(BaseHTTPRequestHandler):
    repo = PortfolioRepository(db_path="reports/portfolio.db")
    service = PortfolioApiService(repo)

    def _respond_json(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/dashboard":
            self._respond_json(self.service.dashboard())
            return

        if parsed.path == "/api/accounts":
            self._respond_json(self.service.accounts())
            return

        if parsed.path == "/api/transactions":
            params = parse_qs(parsed.query)
            limit = int(params.get("limit", ["50"])[0])
            self._respond_json(self.service.transactions(limit=limit))
            return

        self._respond_json({"error": "Not Found"}, status=404)


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", 8100), PortfolioApiHandler)
    print("[WEEK3] API server running: http://localhost:8100")
    print("- /api/dashboard")
    print("- /api/accounts")
    print("- /api/transactions?limit=20")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
