from decimal import Decimal

from app.integrations.kftc.account_info_client import KftcAccountInfoClient


def test_normalize_live_rows_maps_required_fields() -> None:
    client = KftcAccountInfoClient()
    rows = [
        {
            "bank_code_std": "097",
            "bank_name": "테스트은행",
            "account_num_masked": "123-***-***",
            "account_holder_name": "홍길동",
            "account_type_name": "입출금",
            "currency_code": "KRW",
            "balance_amt": "1200",
        }
    ]

    accounts = client._normalize_live_rows(rows)

    assert len(accounts) == 1
    assert accounts[0].institution_code == "097"
    assert accounts[0].institution_name == "테스트은행"
    assert accounts[0].balance == Decimal("1200")


def test_normalize_live_rows_defaults_when_fields_missing() -> None:
    client = KftcAccountInfoClient()
    rows = [{}]

    accounts = client._normalize_live_rows(rows)

    assert accounts[0].institution_code == "unknown"
    assert accounts[0].currency == "KRW"
    assert accounts[0].balance == Decimal("0")
