from __future__ import annotations

import sqlite3

import pytest

from payment import PaymentService


def make_service(tmp_path):
    service = PaymentService(tmp_path / "palm_payment.sqlite3")
    service.create_account("P001", "Stephen", 10_000)
    service.create_account("P002", "Bankey", 15_000)
    return service


def test_payment_deducts_cents_and_records_success(tmp_path):
    service = make_service(tmp_path)

    result = service.pay("P001", 500, "TX001")

    assert result.status == "SUCCESS"
    assert result.user_id == "P001"
    assert result.amount_cents == 500
    assert result.balance_cents == 9_500
    assert service.balance_for("P001") == 9_500
    assert service.transactions_for("P001")[0].transaction_id == "TX001"


@pytest.mark.parametrize("amount_cents", [0, -1])
def test_non_positive_amount_is_rejected_without_a_record(tmp_path, amount_cents):
    service = make_service(tmp_path)

    result = service.pay("P001", amount_cents, "TX-invalid")

    assert result.status == "INVALID_AMOUNT"
    assert service.balance_for("P001") == 10_000
    assert service.transaction_count() == 0


def test_insufficient_balance_is_rejected_without_a_partial_debit(tmp_path):
    service = make_service(tmp_path)

    result = service.pay("P001", 10_001, "TX002")

    assert result.status == "INSUFFICIENT_BALANCE"
    assert result.balance_cents == 10_000
    assert service.balance_for("P001") == 10_000
    assert service.transaction_count() == 0


def test_unknown_account_is_rejected_without_a_record(tmp_path):
    service = make_service(tmp_path)

    result = service.pay("P999", 500, "TX003")

    assert result.status == "ACCOUNT_NOT_FOUND"
    assert service.transaction_count() == 0


def test_repeating_same_transaction_is_idempotent(tmp_path):
    service = make_service(tmp_path)

    first = service.pay("P001", 500, "TX004")
    second = service.pay("P001", 500, "TX004")

    assert second == first
    assert service.balance_for("P001") == 9_500
    assert service.transaction_count() == 1


def test_reusing_transaction_id_with_different_details_is_rejected(tmp_path):
    service = make_service(tmp_path)
    service.pay("P001", 500, "TX005")

    result = service.pay("P002", 500, "TX005")

    assert result.status == "TRANSACTION_CONFLICT"
    assert service.balance_for("P002") == 15_000
    assert service.transaction_count() == 1


def test_schema_enables_foreign_keys_and_survives_reopen(tmp_path):
    database = tmp_path / "palm_payment.sqlite3"
    service = PaymentService(database)
    service.create_account("P001", "Stephen", 10_000)
    service.pay("P001", 500, "TX006")
    service.close()

    reopened = PaymentService(database)
    assert reopened.balance_for("P001") == 9_500
    assert reopened.transaction_count() == 1
    with pytest.raises(sqlite3.IntegrityError):
        reopened.connection.execute(
            "INSERT INTO accounts(user_id, balance_cents) VALUES ('P999', 100)"
        )
    reopened.close()


def test_database_error_rolls_back_debit_and_transaction_insert(tmp_path):
    service = make_service(tmp_path)
    service.connection.executescript(
        """
        CREATE TRIGGER fail_tx_insert
        BEFORE INSERT ON transactions
        WHEN NEW.transaction_id = 'TX-FAIL'
        BEGIN
            SELECT RAISE(ABORT, 'injected transaction failure');
        END;
        """
    )

    with pytest.raises(sqlite3.IntegrityError, match="injected transaction failure"):
        service.pay("P001", 500, "TX-FAIL")

    assert service.balance_for("P001") == 10_000
    assert service.transaction_count() == 0
    service.close()
