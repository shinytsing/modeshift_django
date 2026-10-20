"""
Celery配置
"""
import os
from celery import Celery
from celery.schedules import crontab

# 设置默认Django settings模块
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

# 创建Celery应用
app = Celery("modeshift_django")

# 从Django settings加载配置
app.config_from_object("django.conf:settings", namespace="CELERY")

# 自动发现所有已注册应用中的tasks
app.autodiscover_tasks()

# Runs after the legacy social crawler's 08:00 slot when Celery Beat is enabled.
app.conf.beat_schedule = {
    **(app.conf.beat_schedule or {}),
    "check-creator-watches-daily": {
        "task": "apps.tools.tasks.check_creator_watches_daily",
        "schedule": crontab(hour=8, minute=5),
        "options": {"queue": "creator_watch"},
    },
}


@app.task(bind=True)
def debug_task(self):
    """调试任务"""
    print(f"Request: {self.request!r}")
