# Changelog

## [1.0.0] - 2026-11-10

基于 `FlanChanXwO/astrbot_plugin_rsshub` v2.1.4 的非官方分支。

### Fixed

- 新建订阅未填写平台时，自动从目标会话前缀推断平台类型；编辑订阅与测试推送同样支持推断，历史遗留的空平台订阅在分发时也会回退推断。
- 停用订阅不再从「订阅列表」消失，列表与统计包含启用和停用订阅，便于再次启用。
- QQ 官方群主动推送在发送前补记 group scene，避免 AstrBot 适配器因没有缓存 `msg_id`/scene 而静默跳过发送。

### Added

- WebUI 支持新建 Feed、新建订阅，以及订阅单条启用/停用。
- 固定用户 `webui`，启动时自动创建，用于订阅与推送历史的外键归属。
- `plugins.json` 自建插件源元数据与插件页面中文标题。

### Changed

- 插件改名为 `astrbot_plugin_rsshub_kai`，展示名 `RSSHub Kai`，数据目录与 Web API 前缀同步更新。
- 兼容性调整为 AstrBot >= 4.24.2。
- 概览页移除“用户数”，改为“启用订阅 / 停用订阅”。
- 订阅列表与推送历史移除用户列与用户筛选。
- Logo 使用色相旋转改为蓝色系。

### Removed

- 移除全部聊天命令与帮助图资源。
- 移除内容处理器 `ai_filter` / `ai_transform` 及处理器页面。
- 移除全部 LLM 工具注册与调用。
- 移除用户管理页面与用户设置命令。
- 移除 RSSHub Routes 知识库同步、命令、配置与页面。
- 移除数据库中的 `handlers`、`handlers_mode`、`handler_trace` 字段。

### Deferred

- 订阅排版自定义模板与预览功能暂未实现，保留原有 `style` 与显示选项。
- 订阅导入/导出仅保留后端接口，WebUI 入口暂未提供。
