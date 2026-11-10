# AGENTS.md

This is `astrbot_plugin_rsshub_kai`, an AstrBot plugin that pushes RSS feeds to chat platforms and is managed entirely from AstrBot Plugin Pages.

## Build, Test, and Lint

From the plugin directory:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests/unit -q
```

Static checks:

```bash
python -m pyflakes src
python -m compileall -q main.py bootstrap.py src
```

## Project Layout

- `_conf_schema.json` - AstrBot plugin configuration schema
- `metadata.yaml` - AstrBot plugin metadata
- `main.py` / `bootstrap.py` - lifecycle entry and runtime composition
- `src/` - domain, application, infrastructure, and interface code
- `pages/dashboard/` - Plugin Pages frontend (vanilla ES modules + petite-vue)
- `tests/` - unit and integration tests

## Invariants

- No chat commands and no LLM tools may be registered.
- Every subscription and push history row belongs to the fixed user `webui`.
- There is no content handler chain; do not reintroduce `handlers` columns or AI provider settings.
- Plugin Pages call the Web API through `window.AstrBotPluginPage`; the route prefix must equal `metadata.name`.
- Keep `astrbot_version: ">=4.24.2"` unless Plugin Pages compatibility is re-verified.

## Style

- Python 3.10+, `from __future__ import annotations`, Google-style docstrings for non-obvious public functions.
- Keep user-facing strings in Chinese; logs may be Chinese or English but stay consistent with nearby code.
- Frontend stays dependency-free beyond the bundled petite-vue and Chart.js assets.
