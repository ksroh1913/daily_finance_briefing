from app.services.alert_notifier import AlertNotifier


class DummyResponse:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code


def test_send_returns_false_without_webhook() -> None:
    notifier = AlertNotifier(webhook_url=None)
    assert notifier.send({"hello": "world"}) is False
