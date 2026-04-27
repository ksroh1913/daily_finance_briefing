from week3_api_server import is_authorized


def test_is_authorized_without_api_key() -> None:
    assert is_authorized({}, None) is True


def test_is_authorized_with_api_key() -> None:
    assert is_authorized({"X-API-Key": "abc"}, "abc") is True
    assert is_authorized({"X-API-Key": "wrong"}, "abc") is False
