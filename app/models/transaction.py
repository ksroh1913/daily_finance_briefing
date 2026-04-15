from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(slots=True)
class AccountTransaction:
    tx_id: str
    institution_name: str
    account_num_masked: str
    tx_type: str
    amount: Decimal
    currency: str
    occurred_at: datetime
    memo: str | None = None
