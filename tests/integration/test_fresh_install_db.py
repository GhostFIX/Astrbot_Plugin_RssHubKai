"""Fresh-install database and repository smoke tests."""

from __future__ import annotations

import pytest
from sqlalchemy import text

from astrbot_plugin_rsshub.src.domain.entities.feed import Feed
from astrbot_plugin_rsshub.src.domain.entities.push_history import PushHistory
from astrbot_plugin_rsshub.src.domain.entities.subscription import Subscription
from astrbot_plugin_rsshub.src.infrastructure.persistence import database as db_module
from astrbot_plugin_rsshub.src.infrastructure.persistence.database import DatabaseManager
from astrbot_plugin_rsshub.src.infrastructure.persistence.feed_repository_impl import (
    FeedRepositoryImpl,
)
from astrbot_plugin_rsshub.src.infrastructure.persistence.push_history_repository_impl import (
    PushHistoryRepositoryImpl,
)
from astrbot_plugin_rsshub.src.infrastructure.persistence.subscription_repository_impl import (
    SubscriptionRepositoryImpl,
)


@pytest.mark.asyncio
async def test_fresh_install_creates_webui_and_accepts_rows(tmp_path, monkeypatch):
    db = DatabaseManager()
    monkeypatch.setattr(db_module, "db_manager_instance", db)
    await db.init(str(tmp_path / "rsshub.db"))

    feed_repo = FeedRepositoryImpl()
    sub_repo = SubscriptionRepositoryImpl()
    history_repo = PushHistoryRepositoryImpl()

    feed = await feed_repo.save(Feed(link="https://example.com/feed.xml", title="Feed"))
    sub = await sub_repo.save(
        Subscription(
            user_id="webui",
            feed_id=feed.id,
            target_session="aiocqhttp:FriendMessage:123",
            platform_name="aiocqhttp",
        )
    )
    history = await history_repo.save(
        PushHistory(
            user_id="webui",
            feed_id=feed.id,
            sub_id=sub.id,
            entry_title="Entry",
            entry_link="https://example.com/1",
            target_session=sub.target_session,
            status="success",
        )
    )

    assert sub.id is not None
    assert sub.user_id == "webui"
    assert history.id is not None
    assert await sub_repo.get_by_id(sub.id) is not None

    async with db.get_session() as session:
        result = await session.execute(text("SELECT id FROM rsshub_user"))
        assert [row[0] for row in result.fetchall()] == ["webui"]

    await db.close()
