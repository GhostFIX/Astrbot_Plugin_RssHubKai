"""RSSHub Kai 插件入口

本插件只提供 WebUI 管理，不注册聊天命令，也不注册任何 LLM 工具。
"""

from __future__ import annotations

from astrbot.api import AstrBotConfig
from astrbot.api.star import Context, Star

from .bootstrap import PluginDeps, PluginRuntime, create_plugin_runtime
from .src.application.services.session_push_queue import SessionPushQueue
from .src.infrastructure.utils import get_logger

logger = get_logger()


class RSSHubPlugin(Star):
    """RSS 订阅推送插件（WebUI 单用户模式）"""

    def __init__(self, context: Context, config: AstrBotConfig | None = None):
        super().__init__(context)
        self._config = config
        self._scheduler = None
        self._db_initialized = False
        self._web_api = None
        self._deps: PluginDeps = {}
        self._app_settings = None
        self._push_job_queue = SessionPushQueue()
        self._notification_dispatcher = None
        self._runtime: PluginRuntime | None = None

    async def initialize(self):
        """初始化守护进程、数据库、调度器与 Web API。"""
        try:
            runtime = await create_plugin_runtime(
                self.context,
                self._config,
                push_job_queue=self._push_job_queue,
            )
            self._runtime = runtime
            self._scheduler = runtime.scheduler
            self._db_initialized = runtime.db_initialized
            self._web_api = runtime.web_api
            self._deps = runtime.deps
            self._app_settings = runtime.app_settings
            self._push_job_queue = runtime.push_job_queue
            self._notification_dispatcher = runtime.notification_dispatcher
        except Exception as e:
            logger.exception("RSSHub 插件初始化失败: %s", e)

    async def terminate(self):
        """停止调度器、推送队列与数据库连接。"""
        logger.info("正在停止 RSSHub 插件...")
        if self._runtime:
            await self._runtime.stop()
        else:
            await self._push_job_queue.stop_all()
        logger.info("RSSHub 插件已停止")
