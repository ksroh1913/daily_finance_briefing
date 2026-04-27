from __future__ import annotations

import json
from typing import Any

import requests


class AlertNotifier:
    def __init__(self, webhook_url: str | None = None, timeout: int = 5) -> None:
        self.webhook_url = webhook_url
        self.timeout = timeout

    def send(self, payload: dict[str, Any]) -> bool:
        if not self.webhook_url:
            return False

        response = requests.post(
            self.webhook_url,
            data=json.dumps(payload, ensure_ascii=False),
            headers={"Content-Type": "application/json"},
            timeout=self.timeout,
        )
        return 200 <= response.status_code < 300
