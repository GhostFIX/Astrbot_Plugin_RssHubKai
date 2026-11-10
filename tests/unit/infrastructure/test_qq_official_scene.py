"""QQ 官方主动推送 scene 补标记测试."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from astrbot_plugin_rsshub.src.infrastructure.messaging.senders.qq_official_sender import (
    QQOfficialMessageSender,
)


def test_ensure_group_scene_marks_matching_platform(monkeypatch):
    platform = MagicMock()
    platform.meta.return_value = SimpleNamespace(id="Gh0stF1X", name="qq_official")
    context = SimpleNamespace(
        platform_manager=SimpleNamespace(platform_insts=[platform])
    )
    monkeypatch.setattr(
        "astrbot_plugin_rsshub.src.infrastructure.messaging.senders.qq_official_sender.StarTools._context",
        context,
        raising=False,
    )

    QQOfficialMessageSender._ensure_group_proactive_scene(
        "Gh0stF1X:GroupMessage:7E215ACC9BB3856D3BCDA159E425510D"
    )

    platform.remember_session_scene.assert_called_once_with(
        "7E215ACC9BB3856D3BCDA159E425510D", "group"
    )


def test_ensure_group_scene_ignores_friend_sessions(monkeypatch):
    platform = MagicMock()
    platform.meta.return_value = SimpleNamespace(id="Gh0stF1X", name="qq_official")
    context = SimpleNamespace(
        platform_manager=SimpleNamespace(platform_insts=[platform])
    )
    monkeypatch.setattr(
        "astrbot_plugin_rsshub.src.infrastructure.messaging.senders.qq_official_sender.StarTools._context",
        context,
        raising=False,
    )

    QQOfficialMessageSender._ensure_group_proactive_scene(
        "Gh0stF1X:FriendMessage:ABCDEF"
    )

    platform.remember_session_scene.assert_not_called()
