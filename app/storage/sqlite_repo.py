from __future__ import annotations

import sqlite3
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from app.models.account import AccountSnapshot, ExternalAccount
from app.models.transaction import AccountTransaction


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
                    fetched_at TEXT NOT NULL,
                    fintech_use_num TEXT
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
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tx_id TEXT NOT NULL UNIQUE,
                    institution_name TEXT NOT NULL,
                    account_num_masked TEXT NOT NULL,
                    tx_type TEXT NOT NULL,
                    amount TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    memo TEXT
                )
                """
            )
            conn.commit()

    def _has_column(self, table: str, column: str) -> bool:
        with self._connect() as conn:
            rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
        return any(r[1] == column for r in rows)

    def _ensure_migrations(self) -> None:
        if not self._has_column("accounts", "fintech_use_num"):
            with self._connect() as conn:
                conn.execute("ALTER TABLE accounts ADD COLUMN fintech_use_num TEXT")
                conn.commit()

    def replace_accounts(self, accounts: list[ExternalAccount]) -> None:
        self._ensure_migrations()
        with self._connect() as conn:
            conn.execute("DELETE FROM accounts")
            conn.executemany(
                """
                INSERT INTO accounts (
                    institution_code, institution_name, account_num_masked,
                    account_holder, account_type, currency, balance, fetched_at, fintech_use_num
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                        a.fintech_use_num,
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

    def list_accounts(self) -> list[ExternalAccount]:
        self._ensure_migrations()
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT institution_code, institution_name, account_num_masked,
                       account_holder, account_type, currency, balance, fetched_at, fintech_use_num
                FROM accounts
                ORDER BY institution_name, account_num_masked
                """
            ).fetchall()

        return [
            ExternalAccount(
                institution_code=row[0],
                institution_name=row[1],
                account_num_masked=row[2],
                account_holder=row[3],
                account_type=row[4],
                currency=row[5],
                balance=Decimal(row[6]),
                fetched_at=datetime.fromisoformat(row[7]),
                fintech_use_num=row[8],
            )
            for row in rows
        ]

    def upsert_transactions(self, txs: list[AccountTransaction]) -> None:
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO transactions (
                    tx_id, institution_name, account_num_masked,
                    tx_type, amount, currency, occurred_at, memo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(tx_id) DO UPDATE SET
                    institution_name = excluded.institution_name,
                    account_num_masked = excluded.account_num_masked,
                    tx_type = excluded.tx_type,
                    amount = excluded.amount,
                    currency = excluded.currency,
                    occurred_at = excluded.occurred_at,
                    memo = excluded.memo
                """,
                [
                    (
                        t.tx_id,
                        t.institution_name,
                        t.account_num_masked,
                        t.tx_type,
                        str(t.amount),
                        t.currency,
                        t.occurred_at.isoformat(),
                        t.memo,
                    )
                    for t in txs
                ],
            )
            conn.commit()

    def list_transactions(self, limit: int = 50) -> list[AccountTransaction]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT tx_id, institution_name, account_num_masked,
                       tx_type, amount, currency, occurred_at, memo
                FROM transactions
                ORDER BY occurred_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            AccountTransaction(
                tx_id=row[0],
                institution_name=row[1],
                account_num_masked=row[2],
                tx_type=row[3],
                amount=Decimal(row[4]),
                currency=row[5],
                occurred_at=datetime.fromisoformat(row[6]),
                memo=row[7],
            )
            for row in rows
        ]

    def list_transactions_between(self, start: datetime, end: datetime) -> list[AccountTransaction]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT tx_id, institution_name, account_num_masked,
                       tx_type, amount, currency, occurred_at, memo
                FROM transactions
                WHERE occurred_at >= ? AND occurred_at < ?
                ORDER BY occurred_at DESC
                """,
                (start.isoformat(), end.isoformat()),
            ).fetchall()

        return [
            AccountTransaction(
                tx_id=row[0],
                institution_name=row[1],
                account_num_masked=row[2],
                tx_type=row[3],
                amount=Decimal(row[4]),
                currency=row[5],
                occurred_at=datetime.fromisoformat(row[6]),
                memo=row[7],
            )
            for row in rows
        ]
