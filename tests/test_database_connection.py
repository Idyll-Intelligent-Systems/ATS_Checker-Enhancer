import importlib.machinery
import types
import sys
from pathlib import Path

import pytest


_SRC_PATH = Path(__file__).resolve().parents[1] / "src"
spec = importlib.machinery.ModuleSpec("src", loader=None, is_package=True)
src_module = types.ModuleType("src")
src_module.__path__ = [str(_SRC_PATH)]
sys.modules.setdefault("src", src_module)

from src.database.connection import get_database
from src.database import connection
from src.core.config import settings


@pytest.fixture(autouse=True)
def reset_db_state():
    connection._db = None
    connection.engine = None
    connection.async_engine = None
    connection.async_session_factory = None
    connection.sync_session_factory = None
    yield
    connection._db = None
    connection.engine = None
    connection.async_engine = None
    connection.async_session_factory = None
    connection.sync_session_factory = None


@pytest.mark.asyncio
async def test_get_database_singleton():
    first = get_database()
    second = get_database()
    assert first is second


@pytest.mark.asyncio
async def test_connect_disconnect_lifecycle(tmp_path: Path):
    settings.database_url = f"sqlite:///{tmp_path}/test.db"
    db = get_database()
    assert not db.initialized
    await db.connect()
    assert db.initialized
    await db.disconnect()
    assert not db.initialized
