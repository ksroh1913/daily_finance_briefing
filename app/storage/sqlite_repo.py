from __future__ import annotations

import sqlite3
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from app.models.account import AccountSnapshot, ExternalAccount


class PortfolioRepository:
    def __init__(self, db_path: str = "reports/portfolio.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    institution_code TEXT NOT NULL,
                    institution_name TEXT NOT NULL,
                    account_num_masked TEXT NOT NULL,
                    account_holder TEXT NOT NULL,
                    account_type TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    balance TEXT NOT NULL,
                    fetched_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_at TEXT NOT NULL,
                    total_assets_krw TEXT NOT NULL,
                    account_count INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    def replace_accounts(self, accounts: list[ExternalAccount]) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM accounts")
            conn.executemany(
                """
                INSERT INTO accounts (
                    institution_code, institution_name, account_num_masked,
                    account_holder, account_type, currency, balance, fetched_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        a.institution_code,
                        a.institution_name,
                        a.account_num_masked,
                        a.account_holder,
                        a.account_type,
                        a.currency,
                        str(a.balance),
                        a.fetched_at.isoformat(),
                    )
                    for a in accounts
                ],
            )
            conn.commit()

    def insert_snapshot(self, snapshot: AccountSnapshot) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO snapshots (snapshot_at, total_assets_krw, account_count) VALUES (?, ?, ?)",
                (snapshot.snapshot_at.isoformat(), str(snapshot.total_assets_krw), snapshot.account_count),
            )
            conn.commit()

    def latest_snapshot(self) -> AccountSnapshot | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT snapshot_at, total_assets_krw, account_count FROM snapshots ORDER BY id DESC LIMIT 1"
            ).fetchone()
        if row is None:
            return None

        return AccountSnapshot(
            snapshot_at=datetime.fromisoformat(row[0]),
            total_assets_krw=Decimal(row[1]),
            account_count=int(row[2]),
        )
