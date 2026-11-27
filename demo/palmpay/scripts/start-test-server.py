import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
os.environ["PALMPAY_DATABASE_URL"] = "sqlite:///test-results/e2e.db"
os.environ["PALMPAY_DEMO"] = "1"
os.environ["PALMPAY_AUTH_PROVIDER"] = "mock"
os.environ["PALMPAY_OPERATOR_KEY"] = "playwright-operator"

from alembic import command
from alembic.config import Config
import uvicorn

(root / "test-results").mkdir(exist_ok=True)
command.upgrade(Config(str(root / "alembic.ini")), "head")
uvicorn.run("backend.main:app", host="127.0.0.1", port=8765)

