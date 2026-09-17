"""Local SQLite accounts and atomic simulated payments."""

from __future__ import annotations

import sqlite3
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class PaymentResult:
    status: str
    user_id: str | None
    amount_cents: int
    balance_cents: int | None
    transaction_id: str


@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    user_id: str
    amount_cents: int
    status: str
    created_at: str


class PaymentService:
    def __init__(self, database: str | Path) -> None:
        self.database = Path(database)
        self.database.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.database, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self._lock = threading.RLock()
        self._create_schema()

    def _create_schema(self) -> None:
        with self.connection:
            self.connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL CHECK(length(trim(display_name)) > 0)
                );
                CREATE TABLE IF NOT EXISTS accounts (
                    user_id TEXT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
                    balance_cents INTEGER NOT NULL CHECK(balance_cents >= 0)
                );
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL REFERENCES users(user_id),
                    amount_cents INTEGER NOT NULL CHECK(amount_cents > 0),
                    status TEXT NOT NULL CHECK(status = 'SUCCESS'),
                    created_at TEXT NOT NULL,
                    balance_after_cents INTEGER NOT NULL CHECK(balance_after_cents >= 0)
                );
                """
            )
            columns = {
                row["name"] for row in self.connection.execute("PRAGMA table_info(transactions)")
            }
            if "balance_after_cents" not in columns:
                # Keep an older prototype database readable. Old rows cannot
                # recover their historical post-payment balance, but new rows
                # get the stable idempotency value.
                self.connection.execute(
                    "ALTER TABLE transactions ADD COLUMN balance_after_cents INTEGER"
                )

    def create_account(self, user_id: str, display_name: str, balance_cents: int) -> None:
        if isinstance(balance_cents, bool) or not isinstance(balance_cents, int) or balance_cents < 0:
            raise ValueError("balance_cents must be a non-negative integer")
        if not user_id or not display_name.strip():
            raise ValueError("user_id and display_name are required")
        with self._lock, self.connection:
            self.connection.execute(
                "INSERT INTO users(user_id, display_name) VALUES (?, ?)",
                (user_id, display_name),
            )
            self.connection.execute(
                "INSERT INTO accounts(user_id, balance_cents) VALUES (?, ?)",
                (user_id, balance_cents),
            )

    register_user = create_account

    def pay(self, user_id: str, amount_cents: int, transaction_id: str) -> PaymentResult:
        if isinstance(amount_cents, bool) or not isinstance(amount_cents, int) or amount_cents <= 0:
            return PaymentResult("INVALID_AMOUNT", user_id, amount_cents, self._balance_or_none(user_id), transaction_id)
        if not transaction_id:
            return PaymentResult("INVALID_TRANSACTION_ID", user_id, amount_cents, self._balance_or_none(user_id), transaction_id)

        with self._lock, self.connection:
            existing = self.connection.execute(
                "SELECT transaction_id, user_id, amount_cents, status, balance_after_cents FROM transactions WHERE transaction_id = ?",
                (transaction_id,),
            ).fetchone()
            if existing is not None:
                if existing["user_id"] == user_id and existing["amount_cents"] == amount_cents:
                    balance = existing["balance_after_cents"]
                    if balance is None:
                        balance = self._balance_or_none(user_id)
                    return PaymentResult("SUCCESS", user_id, amount_cents, balance, transaction_id)
                return PaymentResult("TRANSACTION_CONFLICT", user_id, amount_cents, self._balance_or_none(user_id), transaction_id)

            account = self.connection.execute(
                "SELECT balance_cents FROM accounts WHERE user_id = ?", (user_id,)
            ).fetchone()
            if account is None:
                return PaymentResult("ACCOUNT_NOT_FOUND", user_id, amount_cents, None, transaction_id)
            current_balance = int(account["balance_cents"])
            if current_balance < amount_cents:
                return PaymentResult("INSUFFICIENT_BALANCE", user_id, amount_cents, current_balance, transaction_id)

            updated = self.connection.execute(
                "UPDATE accounts SET balance_cents = balance_cents - ? WHERE user_id = ? AND balance_cents >= ?",
                (amount_cents, user_id, amount_cents),
            )
            if updated.rowcount != 1:
                return PaymentResult("INSUFFICIENT_BALANCE", user_id, amount_cents, current_balance, transaction_id)
            self.connection.execute(
                "INSERT INTO transactions(transaction_id, user_id, amount_cents, status, created_at, balance_after_cents) VALUES (?, ?, ?, 'SUCCESS', ?, ?)",
                (transaction_id, user_id, amount_cents, datetime.now(UTC).isoformat(), current_balance - amount_cents),
            )
            return PaymentResult("SUCCESS", user_id, amount_cents, current_balance - amount_cents, transaction_id)

    def _balance_or_none(self, user_id: str) -> int | None:
        row = self.connection.execute(
            "SELECT balance_cents FROM accounts WHERE user_id = ?", (user_id,)
        ).fetchone()
        return None if row is None else int(row["balance_cents"])

    def balance_for(self, user_id: str) -> int | None:
        with self._lock:
            return self._balance_or_none(user_id)

    def transactions_for(self, user_id: str) -> list[Transaction]:
        with self._lock:
            rows = self.connection.execute(
                "SELECT transaction_id, user_id, amount_cents, status, created_at FROM transactions WHERE user_id = ? ORDER BY rowid",
                (user_id,),
            ).fetchall()
        return [Transaction(**dict(row)) for row in rows]

    def transaction_count(self) -> int:
        with self._lock:
            return int(self.connection.execute("SELECT COUNT(*) FROM transactions").fetchone()[0])

    def user_exists(self, user_id: str) -> bool:
        with self._lock:
            return self.connection.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,)).fetchone() is not None

    def account_exists(self, user_id: str) -> bool:
        with self._lock:
            return self.connection.execute("SELECT 1 FROM accounts WHERE user_id = ?", (user_id,)).fetchone() is not None

    def delete_user(self, user_id: str) -> None:
        with self._lock, self.connection:
            self.connection.execute("DELETE FROM users WHERE user_id = ?", (user_id,))

    def close(self) -> None:
        self.connection.close()
