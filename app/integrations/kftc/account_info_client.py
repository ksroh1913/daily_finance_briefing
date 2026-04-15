from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import requests

from app.models.account import ExternalAccount


@dataclass(slots=True)
class KftcApiConfig:
    access_token: str
    user_seq_no: str
    auth_code: str
    api_base: str = "https://openapi.openbanking.or.kr"


class KftcAccountInfoClient:
    """KFTC 계좌통합조회 어댑터.

    - 샘플 모드: 로컬 JSON을 읽어 개발/테스트
    - 라이브 모드: 금융결제원 accountinfo/list 호출
    """

    def __init__(self, sample_path: str = "config/week1_sample_accounts.json", timeout: int = 15) -> None:
        self.sample_path = Path(sample_path)
        self.timeout = timeout

    def fetch_accounts(self, use_sample: bool = True, config: KftcApiConfig | None = None) -> list[ExternalAccount]:
        if use_sample:
            return self._load_sample_accounts()

        live_config = config or self._config_from_env()
        rows = self._fetch_account_list(live_config)
        return self._normalize_live_rows(rows)

    def _load_sample_accounts(self) -> list[ExternalAccount]:
        if not self.sample_path.exists():
            raise FileNotFoundError(f"Sample source not found: {self.sample_path}")

        payload = json.loads(self.sample_path.read_text(encoding="utf-8"))
        rows = payload.get("accounts", [])
        return self._normalize_sample_rows(rows)

    def _fetch_account_list(self, config: KftcApiConfig) -> list[dict[str, Any]]:
        url = f"{config.api_base}/v2.0/accountinfo/list"
        headers = {
            "Authorization": f"Bearer {config.access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        }
        body = {
            "bank_tran_id": self._build_bank_tran_id(),
            "user_seq_no": config.user_seq_no,
            "include_cancel_yn": "N",
            "sort_order": "D",
            "model_use_yn": "N",
            "auth_code": config.auth_code,
            "inquiry_bank_type": "1",
            "inquiry_record_cnt": "100",
        }

        response = requests.post(url, headers=headers, json=body, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()

        if payload.get("rsp_code") not in {"A0000", "000"}:
            raise RuntimeError(f"KFTC accountinfo/list error: {payload.get('rsp_code')} {payload.get('rsp_message')}")

        rows = payload.get("res_list", [])
        if not isinstance(rows, list):
            raise RuntimeError("Invalid response: res_list is not a list")
        return rows

    def _normalize_sample_rows(self, rows: list[dict[str, Any]]) -> list[ExternalAccount]:
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

    def _normalize_live_rows(self, rows: list[dict[str, Any]]) -> list[ExternalAccount]:
        fetched_at = datetime.now()
        accounts: list[ExternalAccount] = []

        for row in rows:
            accounts.append(
                ExternalAccount(
                    institution_code=str(row.get("bank_code_std") or row.get("bank_code") or "unknown"),
                    institution_name=str(row.get("bank_name") or "unknown"),
                    account_num_masked=str(row.get("account_num_masked") or "masked"),
                    account_holder=str(row.get("account_holder_name") or "unknown"),
                    account_type=str(row.get("account_type") or row.get("account_type_name") or "입출금"),
                    currency=str(row.get("currency_code") or "KRW"),
                    # accountinfo/list 응답엔 잔액이 없을 수 있어 0으로 초기화 (balance API 단계에서 업데이트)
                    balance=Decimal(str(row.get("balance_amt") or "0")),
                    fetched_at=fetched_at,
                )
            )
        return accounts

    @staticmethod
    def _build_bank_tran_id() -> str:
        # 실제 운영 시 이용기관 코드를 앞자리로 붙여야 함
        return f"M202600000U{uuid.uuid4().hex[:9]}"

    @staticmethod
    def _config_from_env() -> KftcApiConfig:
        token = os.getenv("KFTC_ACCESS_TOKEN", "")
        user_seq_no = os.getenv("KFTC_USER_SEQ_NO", "")
        auth_code = os.getenv("KFTC_AUTH_CODE", "")
        api_base = os.getenv("KFTC_API_BASE", "https://openapi.openbanking.or.kr")

        if not token or not user_seq_no or not auth_code:
            raise ValueError("KFTC env missing: KFTC_ACCESS_TOKEN, KFTC_USER_SEQ_NO, KFTC_AUTH_CODE")

        return KftcApiConfig(
            access_token=token,
            user_seq_no=user_seq_no,
            auth_code=auth_code,
            api_base=api_base,
        )
