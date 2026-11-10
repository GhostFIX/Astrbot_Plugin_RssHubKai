"""主模块集成测试."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_context():
    """模拟 AstrBot 上下文."""
    context = MagicMock()
    context.platform_manager = MagicMock()
    context.platform_manager.platform_insts = []
    return context


@pytest.fixture
def mock_config():
    """模拟 AstrBot 配置."""
    return {
        "rsshub": {
            "db": {"database": "test.db"},
            "basic": {"timeout": 30, "proxy": ""},
        }
    }


@pytest.fixture
def main_module(monkeypatch):
    """导入带最小 AstrBot 假对象的 main 模块."""

    class FakeStar:
        def __init__(self, context):
            self.context = context

    api_mod = sys.modules["astrbot.api"]
    api_mod.AstrBotConfig = dict

    star_mod = sys.modules["astrbot.api.star"]
    star_mod.Context = object
    star_mod.Star = FakeStar

    monkeypatch.delitem(sys.modules, "astrbot_plugin_rsshub.main", raising=False)

    import astrbot_plugin_rsshub.main as main

    return main


class TestRSSHubPluginIntegration:
    """插件入口集成测试."""

    def test_plugin_initialization(self, main_module, mock_context, mock_config):
        """测试插件对象初始化."""
        plugin = main_module.RSSHubPlugin(mock_context, mock_config)

        assert plugin._config == mock_config
        assert plugin._scheduler is None
        assert plugin._deps == {}

    def test_plugin_exposes_no_chat_commands(self, main_module):
        """入口类不应再暴露聊天命令方法."""
        forbidden = ("sub_feed", "unsub_feed", "sub_list", "rsshelp", "test_sub")
        for name in forbidden:
            assert not hasattr(main_module.RSSHubPlugin, name)


class TestConfigurationIntegration:
    """配置集成测试."""

    def test_config_loading(self, mock_config):
        """测试配置加载."""
        from astrbot_plugin_rsshub.src.infrastructure.config import RsshubPluginConfig

        config = RsshubPluginConfig.from_astrbot_config(mock_config)

        assert config is not None
        assert config.http_config.timeout == 30
