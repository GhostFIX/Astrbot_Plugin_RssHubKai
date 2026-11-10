from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import StaticPool

from astrbot_plugin_rsshub.src.infrastructure.persistence.database import (
    DatabaseManager,
    RSSHubBaseModel,
)
from astrbot_plugin_rsshub.src.infrastructure.persistence.migrations import (
    cleanup_legacy_translation_tables,
    ensure_push_history_schema,
    ensure_webui_user,
    run_migrations,
)


def test_database_is_initialized_requires_session_maker():
    db = DatabaseManager()
    db._engine = object()
    db._session_maker = None

    assert db.is_initialized is False


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(RSSHubBaseModel.metadata.create_all)
        await run_migrations(conn)
    yield engine
    await engine.dispose()


async def _columns(conn, table: str) -> set[str]:
    result = await conn.exec_driver_sql(f"PRAGMA table_info({table})")
    return {str(row[1]) for row in result.fetchall()}


@pytest.mark.asyncio
async def test_schema_has_no_handler_columns(engine):
    async with engine.begin() as conn:
        sub_columns = await _columns(conn, "rsshub_sub")
        user_columns = await _columns(conn, "rsshub_user")
        history_columns = await _columns(conn, "rsshub_push_history")

    assert {"handlers", "handlers_mode"}.isdisjoint(sub_columns)
    assert "handlers" not in user_columns
    assert "handler_trace" not in history_columns
    assert {"source_type", "source_key", "raw_xml"}.issubset(history_columns)


@pytest.mark.asyncio
async def test_ensure_webui_user_is_idempotent(engine):
    async with engine.begin() as conn:
        assert await ensure_webui_user(conn) == 1
        assert await ensure_webui_user(conn) == 0
        result = await conn.exec_driver_sql(
            "SELECT id FROM rsshub_user ORDER BY id"
        )
        assert [row[0] for row in result.fetchall()] == ["webui"]


@pytest.mark.asyncio
async def test_ensure_push_history_schema_adds_missing_columns(engine):
    async with engine.begin() as conn:
        await conn.exec_driver_sql("DROP TABLE rsshub_push_history")
        await conn.exec_driver_sql(
            """
            CREATE TABLE rsshub_push_history (
                id INTEGER PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                feed_id INTEGER
            )
            """
        )
        applied = await ensure_push_history_schema(conn)
        columns = await _columns(conn, "rsshub_push_history")

    assert applied == ["source_type", "source_key", "raw_xml"]
    assert {"source_type", "source_key", "raw_xml"}.issubset(columns)


@pytest.mark.asyncio
async def test_cleanup_legacy_translation_tables(engine):
    async with engine.begin() as conn:
        await conn.exec_driver_sql(
            "CREATE TABLE rsshub_translation_cache (id INTEGER PRIMARY KEY)"
        )
        dropped = await cleanup_legacy_translation_tables(conn)
        remaining = await conn.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            ("rsshub_translation_cache",),
        )

    assert dropped == ["rsshub_translation_cache"]
    assert remaining.fetchone() is None
