from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(slots=True)
class ExternalAccount:
    institution_code: str
    institution_name: str
    account_num_masked: str
    account_holder: str
    account_type: str
    currency: str
    balance: Decimal
    fetched_at: datetime


@dataclass(slots=True)
class AccountSnapshot:
    snapshot_at: datetime
    total_assets_krw: Decimal
    account_count: int
