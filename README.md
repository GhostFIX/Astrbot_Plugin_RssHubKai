# RSSHub Kai for AstrBot

<div align="center">

<img src="./logo.png" width="200" alt="RSSHub Kai"/>

**RSS 订阅推送插件 · 纯 WebUI 管理 · 不调用 LLM**

</div>

## 项目简介

`astrbot_plugin_rsshub_kai` 是 [FlanChanXwO/astrbot_plugin_rsshub](https://github.com/FlanChanXwO/astrbot_plugin_rsshub) 的非官方分支，保留原项目的 Feed 抓取、富媒体解析与多平台发送能力，移除了内容处理器、LLM 工具、用户体系与 RSSHub Routes 知识库。

所有管理操作都在 AstrBot WebUI 的插件页面完成，不注册任何聊天命令，也不会调用任何大模型。

## 功能特性

- 在 WebUI 中增删改查 **Feed 源** 与 **订阅**，支持单条/批量启用、停用、删除。
- 新建订阅时校验 RSS 链接并自动抓取标题，推送目标会话可手填或从现有订阅补全。
- 订阅级推送选项：刷新间隔、发送模式、通知、长度限制、作者/来源/标题/标签/媒体显示、排版策略。
- 支持 RSS 2.0、Atom 1.0、JSON Feed。
- 富媒体推送：图片、音频、视频、文件、表格转图片、GIF/视频转码，按平台差异化发送。
- 失败重试、推送历史、人工重试、按天清理。
- 订阅导入/导出后端（TOML）保留，暂未提供 WebUI 入口。
- 单用户模式：所有订阅统一归属固定用户 `webui`，不提供用户管理。

## 与上游的差异

| 能力 | 本分支 |
| --- | --- |
| 聊天命令（`/sub` 等） | 已移除，仅 WebUI |
| 内容处理器（`ai_filter` / `ai_transform`） | 已移除 |
| LLM 工具（订阅/查询/XML 推送等） | 已移除，全流程无 LLM 调用 |
| 用户管理 / 用户级配置 | 已移除，统一归属 `webui` |
| RSSHub Routes 知识库同步 | 已移除 |
| 排版自定义模板与预览 | 暂未实现，保留原有排版选项 |
| Feed 抓取、媒体发送、失败重试、推送历史 | 保留 |
| 导入/导出后端 | 保留（暂无 WebUI 入口） |

## 安装

要求 **AstrBot >= 4.24.2**（Plugin Pages 从该版本开始提供）。

1. 在 AstrBot WebUI 打开「插件」页面；
2. 选择「从链接安装」，填入：

   ```text
   https://github.com/GhostFIX/Astrbot_Plugin_RssHubKai
   ```

3. 等待依赖安装完成，重载插件；
4. 在插件详情页打开「RSS 订阅管理」页面。

升级前请先停用或卸载原版 `astrbot_plugin_rsshub`，避免同一 Feed 被两个插件重复推送。本分支使用独立数据目录，不读取原版数据，也不做数据迁移。

## 使用

### 新建 Feed

「Feed 源」页点击「新建 Feed」，填写 RSS 链接；标题留空时自动抓取。创建后可编辑标题、链接、启用状态，或手动刷新。

### 新建订阅

「订阅列表」页点击「新建订阅」，填写：

- **RSS 链接**：Feed 地址，不存在时会自动创建 Feed；
- **推送目标会话**：AstrBot 的 `unified_msg_origin`，格式为 `平台实例ID:消息类型:会话ID`，例如：

  ```text
  aiocqhttp:FriendMessage:123456
  aiocqhttp:GroupMessage:987654321
  telegram:GroupMessage:-1001234567890
  ```

  输入框会从现有订阅补全可用的目标会话；
- **平台**（可选）：`aiocqhttp`、`telegram`、`qq_official` 等，留空时按目标会话推断；
- **标题**（可选）：留空使用 Feed 标题。

### 启用 / 停用

- 订阅：点击状态列，或在「批量操作」中批量启用/停用；
- Feed：编辑 Feed，或直接切换「状态」；停用 Feed 会停止其下所有订阅的轮询。

### 测试推送与历史

订阅详情页提供「测试推送」，使用真实发送链路验证目标会话与平台配置。推送历史页支持按状态、Feed、关键词筛选，单条重试、删除、按天清理。

## 配置

插件配置页保留以下分组：

- `basic_config`：默认 RSSHub 域名、最小间隔、去重窗口、失败队列、多 Bot 去重等；
- `http_config`：代理、请求超时、媒体下载超时；
- `media`：媒体反代、缓存、表格转图、GIF/视频转码、FFmpeg 来源与镜像；
- `sender_strategies`：Telegram / OneBot / QQ 官方发送策略。

订阅默认值在 WebUI「默认订阅设置」页维护。

## 兼容性

- AstrBot >= 4.24.2；
- Python 3.10+；
- Windows / Linux / macOS；
- 平台发送能力沿用上游实现：OneBot（NapCat/Lagrange）、Telegram、QQ 官方、微信 OC 等。

## 开发

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests/unit -q
```

测试使用 `tests/conftest.py` 中的 AstrBot mock，不需要完整 AstrBot 运行时。

## 项目结构

```text
main.py                插件生命周期入口（无聊天命令、无 LLM 工具）
bootstrap.py           依赖装配与 Web API 注册
src/domain/            实体与仓库协议
src/application/       命令、查询、DTO、轮询与分发服务
src/infrastructure/    配置、持久化、抓取、发送、渲染、调度
src/interfaces/        Web API
pages/dashboard/       Plugin Pages 管理界面
tests/                 单元与集成测试
```

## 协议

本项目基于 [AGPL-3.0](./LICENSE) 发布，原项目同样使用 AGPL-3.0。

- 原作者：FlanChanXwO
- 上游项目：https://github.com/FlanChanXwO/astrbot_plugin_rsshub
- 本分支修改：移除 LLM/处理器/用户体系/知识库，改为 WebUI 单用户管理模式，Logo 基于原素材色相旋转。

## 致谢

- [RSS-to-Telegram-Bot](https://github.com/Rongronggg9/RSS-to-Telegram-Bot)
- [AstrBot](https://github.com/AstrBotDevs/AstrBot)
- [feedparser](https://github.com/kurtmckee/feedparser)
