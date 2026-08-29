"""
作业批改URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'grading'

# 创建路由器
router = DefaultRouter()
router.register(r'submissions', views.HomeworkSubmissionViewSet, basename='submission')
router.register(r'papers', views.GeneratedPaperViewSet, basename='paper')

urlpatterns = [
    # API路由
    path('', include(router.urls)),

    # 额外的API端点
    path('subjects/', views.get_available_subjects, name='subjects'),
    path('status/<str:task_id>/', views.homework_status, name='homework_status'),
]
