"""Verify that a checkout contains every path the plugin needs at runtime.

Run this before pushing to GitHub:

    python scripts/verify_repo_layout.py

AstrBot installs the repository archive as-is, so a push that only contains the
root files will fail with ``No module named '...src'``.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = (
    "metadata.yaml",
    "main.py",
    "bootstrap.py",
    "_conf_schema.json",
    "requirements.txt",
    "logo.png",
    "src/__init__.py",
    "src/application/__init__.py",
    "src/domain/__init__.py",
    "src/infrastructure/__init__.py",
    "src/interfaces/__init__.py",
    "pages/dashboard/index.html",
    "pages/dashboard/app.js",
    "pages/dashboard/js/api.js",
    ".astrbot-plugin/i18n/zh-CN.json",
)

REQUIRED_DIRS = (
    "src",
    "pages",
    "tests",
)


def main() -> int:
    missing_files = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    missing_dirs = [path for path in REQUIRED_DIRS if not (ROOT / path).is_dir()]

    if not missing_files and not missing_dirs:
        print(f"OK: {ROOT} contains all required runtime paths")
        return 0

    print(f"Repository root: {ROOT}")
    for path in missing_dirs:
        print(f"MISSING DIR : {path}/")
    for path in missing_files:
        print(f"MISSING FILE: {path}")
    print(
        "\nPush the whole plugin directory (including src/, pages/, tests/ and "
        ".astrbot-plugin/), not only the root files."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
