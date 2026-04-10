from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from app.models.account import ExternalAccount


class KftcAccountInfoClient:
    """Week-1 adapter.

    - 현재는 샘플 JSON 파일을 읽어 공통 모델로 정규화합니다.
    - 이후 금융결제원 accountinfo/list, balance API 연동 시 이 클래스를 실제 HTTP 호출로 교체하면 됩니다.
    """

    def __init__(self, sample_path: str = "config/week1_sample_accounts.json") -> None:
        self.sample_path = Path(sample_path)

    def fetch_accounts(self) -> list[ExternalAccount]:
        if not self.sample_path.exists():
            raise FileNotFoundError(f"Sample source not found: {self.sample_path}")

        payload = json.loads(self.sample_path.read_text(encoding="utf-8"))
        rows = payload.get("accounts", [])

        accounts: list[ExternalAccount] = []
        for row in rows:
            accounts.append(
                ExternalAccount(
                    institution_code=str(row["institution_code"]),
                    institution_name=str(row["institution_name"]),
                    account_num_masked=str(row["account_num_masked"]),
                    account_holder=str(row["account_holder"]),
                    account_type=str(row["account_type"]),
                    currency=str(row.get("currency", "KRW")),
                    balance=Decimal(str(row["balance"])),
                    fetched_at=datetime.fromisoformat(row["fetched_at"]),
                )
            )
        return accounts

    @staticmethod
    def to_dict(account: ExternalAccount) -> dict[str, Any]:
        data = asdict(account)
        data["balance"] = str(account.balance)
        data["fetched_at"] = account.fetched_at.isoformat()
        return data
