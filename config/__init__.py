"""
配置包初始化
"""
from __future__ import annotations

import os
import sys
from typing import Optional

# 注意：Django 启动时会导入 `config` 包；在本地开发环境里强制加载 Celery
# 可能触发底层依赖（如 greenlet）的导入卡住，从而导致 `runserver` 无法启动。
# 因此仅在明确运行 Celery 时才加载 celery_app。
celery_app: Optional[object] = None

_argv0 = (sys.argv[0] if sys.argv else "").lower()
_running_celery = _argv0.endswith("celery") or _argv0.endswith("celery.exe")
_enable_celery = os.getenv("ENABLE_CELERY") == "1"

if _running_celery or _enable_celery:
    from .celery import app as celery_app  # noqa: F401

__all__ = ("celery_app",)
