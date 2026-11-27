import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

engine = create_engine(os.getenv("PALMPAY_DATABASE_URL", "sqlite:///palmpay.db"))

@event.listens_for(engine, "connect")
def configure_sqlite(connection, _):
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("PRAGMA busy_timeout=5000")

class Base(DeclarativeBase):
    pass

Session = sessionmaker(engine, expire_on_commit=False)

