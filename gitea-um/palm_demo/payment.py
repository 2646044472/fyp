from __future__ import annotations

import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path

from models import PaymentResult


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, display_name TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS accounts (user_id TEXT PRIMARY KEY, balance_cents INTEGER NOT NULL CHECK(balance_cents >= 0), FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS transactions (transaction_id TEXT PRIMARY KEY, request_id TEXT NOT NULL UNIQUE, user_id TEXT NOT NULL, amount_cents INTEGER NOT NULL CHECK(amount_cents > 0), balance_before_cents INTEGER NOT NULL, balance_after_cents INTEGER NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL, FOREIGN KEY(user_id) REFERENCES users(user_id));
"""


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


class PaymentService:
    def __init__(self, database_path: str | Path | None = None) -> None:
        self.database_path = Path(database_path) if database_path is not None else Path(__file__).resolve().parent / "runtime" / "palm_payment.sqlite3"
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.row_factory = sqlite3.Row
        return connection

    def create_account(self, user_id: str, display_name: str, initial_balance_cents: int) -> None:
        if not isinstance(initial_balance_cents, int) or initial_balance_cents < 0:
            raise ValueError("initial balance must be a non-negative integer")
        with self._connect() as connection:
            connection.execute("INSERT INTO users(user_id, display_name, created_at) VALUES (?, ?, ?)", (user_id, display_name, now()))
            connection.execute("INSERT INTO accounts(user_id, balance_cents) VALUES (?, ?)", (user_id, initial_balance_cents))

    def pay(self, user_id: str, amount_cents: int, request_id: str) -> PaymentResult:
        if not isinstance(amount_cents, int) or amount_cents <= 0:
            return PaymentResult("ERROR", None, None)
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            previous = connection.execute("SELECT * FROM transactions WHERE request_id = ?", (request_id,)).fetchone()
            if previous is not None:
                return PaymentResult(previous["status"], previous["transaction_id"], previous["balance_after_cents"])
            account = connection.execute("SELECT balance_cents FROM accounts WHERE user_id = ?", (user_id,)).fetchone()
            if account is None:
                return PaymentResult("ERROR", None, None)
            before = int(account["balance_cents"])
            status = "SUCCESS" if before >= amount_cents else "INSUFFICIENT_BALANCE"
            after = before - amount_cents if status == "SUCCESS" else before
            transaction_id = str(uuid.uuid4())
            connection.execute("UPDATE accounts SET balance_cents = ? WHERE user_id = ?", (after, user_id))
            connection.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (transaction_id, request_id, user_id, amount_cents, before, after, status, now()))
            return PaymentResult(status, transaction_id, after)

    def balance_for(self, user_id: str) -> int | None:
        with self._connect() as connection:
            row = connection.execute("SELECT balance_cents FROM accounts WHERE user_id = ?", (user_id,)).fetchone()
            return None if row is None else int(row[0])

    def display_name_for(self, user_id: str) -> str | None:
        with self._connect() as connection:
            row = connection.execute("SELECT display_name FROM users WHERE user_id = ?", (user_id,)).fetchone()
            return None if row is None else str(row[0])

    def user_exists(self, user_id: str) -> bool:
        with self._connect() as connection:
            return connection.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,)).fetchone() is not None

    def account_exists(self, user_id: str) -> bool:
        return self.balance_for(user_id) is not None

    def top_up(self, user_id: str, amount_cents: int) -> int:
        if not isinstance(amount_cents, int) or amount_cents <= 0:
            raise ValueError("top-up must be a positive integer")
        with self._connect() as connection:
            cursor = connection.execute("UPDATE accounts SET balance_cents = balance_cents + ? WHERE user_id = ?", (amount_cents, user_id))
            if cursor.rowcount != 1:
                raise ValueError(f"unknown user {user_id}")
            return int(connection.execute("SELECT balance_cents FROM accounts WHERE user_id = ?", (user_id,)).fetchone()[0])

    def transaction_count(self) -> int:
        with self._connect() as connection:
            return int(connection.execute("SELECT COUNT(*) FROM transactions").fetchone()[0])

    def transactions_for(self, user_id: str) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY created_at", (user_id,)).fetchall()
            return [dict(row) for row in rows]

    def list_users(self) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute("SELECT u.user_id, u.display_name, u.created_at, a.balance_cents FROM users u JOIN accounts a ON a.user_id = u.user_id ORDER BY u.user_id").fetchall()
            return [dict(row) for row in rows]

    def list_transactions(self) -> list[dict]:
        with self._connect() as connection:
            return [dict(row) for row in connection.execute("SELECT * FROM transactions ORDER BY created_at").fetchall()]

    def delete_user(self, user_id: str) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
            connection.execute("DELETE FROM accounts WHERE user_id = ?", (user_id,))
            connection.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
