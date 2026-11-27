from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column as col
from .db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = col(String, primary_key=True)
    email: Mapped[str] = col(String, unique=True)
    name: Mapped[str]
    password: Mapped[str]
    consent: Mapped[bool]
    locale: Mapped[str] = col(default="en")

class Merchant(Base):
    __tablename__ = "merchants"
    id: Mapped[str] = col(String, primary_key=True)
    name: Mapped[str]

class Terminal(Base):
    __tablename__ = "terminals"
    id: Mapped[str] = col(String, primary_key=True)
    merchant_id: Mapped[str] = col(ForeignKey("merchants.id"))
    name: Mapped[str]

class Wallet(Base):
    __tablename__ = "wallets"
    id: Mapped[str] = col(String, primary_key=True)
    user_id: Mapped[str | None] = col(ForeignKey("users.id"), unique=True)
    merchant_id: Mapped[str | None] = col(ForeignKey("merchants.id"), unique=True)
    balance: Mapped[int] = col(default=0)

class Product(Base):
    __tablename__ = "products"
    id: Mapped[str] = col(String, primary_key=True)
    merchant_id: Mapped[str] = col(ForeignKey("merchants.id"))
    name: Mapped[str]
    category: Mapped[str]
    price: Mapped[int]
    available: Mapped[bool] = col(Boolean, default=True)
    image: Mapped[str] = col(default="")

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[str] = col(String, primary_key=True)
    merchant_id: Mapped[str] = col(ForeignKey("merchants.id"))
    total: Mapped[int]
    status: Mapped[str] = col(default="pending")
    created_at: Mapped[str]
    request_key: Mapped[str] = col(unique=True)

class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = col(Integer, primary_key=True)
    order_id: Mapped[str] = col(ForeignKey("orders.id"), index=True)
    product_id: Mapped[str] = col(ForeignKey("products.id"))
    name: Mapped[str]
    price: Mapped[int]
    quantity: Mapped[int]

class PaymentIntent(Base):
    __tablename__ = "payment_intents"
    id: Mapped[str] = col(String, primary_key=True)
    order_id: Mapped[str] = col(ForeignKey("orders.id"), index=True)
    merchant_id: Mapped[str] = col(ForeignKey("merchants.id"))
    amount: Mapped[int]
    currency: Mapped[str] = col(default="MOP")
    expires_at: Mapped[int]
    created_at: Mapped[str]
    status: Mapped[str] = col(default="awaiting_authorization")
    reason: Mapped[str | None]
    user_id: Mapped[str | None] = col(ForeignKey("users.id"))
    reference: Mapped[str | None] = col(unique=True)
    paid_at: Mapped[str | None]
    request_key: Mapped[str] = col(unique=True)

class Authorization(Base):
    __tablename__ = "authorizations"
    intent_id: Mapped[str] = col(ForeignKey("payment_intents.id"), primary_key=True)
    merchant_id: Mapped[str]
    amount: Mapped[int]
    currency: Mapped[str]
    expires_at: Mapped[int]
    identity: Mapped[str]

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    __table_args__ = (UniqueConstraint("wallet_id", "reference"),)
    id: Mapped[int] = col(Integer, primary_key=True)
    wallet_id: Mapped[str] = col(ForeignKey("wallets.id"), index=True)
    reference: Mapped[str]
    amount: Mapped[int]
    created_at: Mapped[str]

class PalmEnrollment(Base):
    __tablename__ = "palm_enrollments"
    user_id: Mapped[str] = col(ForeignKey("users.id"), primary_key=True)
    identity: Mapped[str | None] = col(unique=True)
    pending_identity: Mapped[str | None]
    pairing_code: Mapped[str | None] = col(unique=True)
    expires_at: Mapped[int | None]
    hand: Mapped[str]

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = col(Integer, primary_key=True)
    action: Mapped[str]
    subject: Mapped[str]
    created_at: Mapped[str]

class LoginSession(Base):
    __tablename__ = "login_sessions"
    token_hash: Mapped[str] = col(String, primary_key=True)
    subject: Mapped[str]
    role: Mapped[str]
    expires_at: Mapped[int]

