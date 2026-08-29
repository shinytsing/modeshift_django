"""
作业批改应用配置
"""
from django.apps import AppConfig


class GradingConfig(AppConfig):
    """作业批改应用配置类"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.grading'
    verbose_name = '作业批改与智能组卷'
