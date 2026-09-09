"""
Celery配置
"""
import os
from celery import Celery

# 设置默认Django settings模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# 创建Celery应用
app = Celery('modeshift_django')

# 从Django settings加载配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现所有已注册应用中的tasks
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """调试任务"""
    print(f'Request: {self.request!r}')
