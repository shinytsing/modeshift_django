#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析数据模型
用于存储服务器分析相关的数据
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ServerMetrics(models.Model):
    """服务器指标模型"""
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="记录时间")
    cpu_percent = models.FloatField(verbose_name="CPU使用率")
    memory_percent = models.FloatField(verbose_name="内存使用率")
    disk_percent = models.FloatField(verbose_name="磁盘使用率")
    load_average = models.JSONField(null=True, blank=True, verbose_name="负载平均值")
    network_bytes_sent = models.BigIntegerField(verbose_name="网络发送字节数")
    network_bytes_recv = models.BigIntegerField(verbose_name="网络接收字节数")
    
    class Meta:
        verbose_name = "服务器指标"
        verbose_name_plural = "服务器指标"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"服务器指标 - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class DatabaseMetrics(models.Model):
    """数据库指标模型"""
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="记录时间")
    db_size = models.CharField(max_length=50, verbose_name="数据库大小")
    total_connections = models.IntegerField(verbose_name="总连接数")
    active_connections = models.IntegerField(verbose_name="活跃连接数")
    idle_connections = models.IntegerField(verbose_name="空闲连接数")
    slow_queries = models.IntegerField(verbose_name="慢查询数")
    dead_tuples = models.IntegerField(verbose_name="死元组数")
    
    class Meta:
        verbose_name = "数据库指标"
        verbose_name_plural = "数据库指标"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"数据库指标 - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class ApplicationMetrics(models.Model):
    """应用指标模型"""
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="记录时间")
    total_requests = models.IntegerField(verbose_name="总请求数")
    successful_requests = models.IntegerField(verbose_name="成功请求数")
    failed_requests = models.IntegerField(verbose_name="失败请求数")
    avg_response_time = models.FloatField(verbose_name="平均响应时间")
    max_response_time = models.FloatField(verbose_name="最大响应时间")
    active_users = models.IntegerField(verbose_name="活跃用户数")
    new_users = models.IntegerField(verbose_name="新用户数")
    
    class Meta:
        verbose_name = "应用指标"
        verbose_name_plural = "应用指标"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"应用指标 - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class ErrorLog(models.Model):
    """错误日志模型"""
    
    ERROR_TYPES = [
        ('api_error', 'API错误'),
        ('database_error', '数据库错误'),
        ('system_error', '系统错误'),
        ('authentication_error', '认证错误'),
        ('permission_error', '权限错误'),
        ('validation_error', '验证错误'),
        ('external_service_error', '外部服务错误'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('critical', '严重'),
    ]
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="发生时间")
    error_type = models.CharField(max_length=50, choices=ERROR_TYPES, verbose_name="错误类型")
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, verbose_name="严重程度")
    message = models.TextField(verbose_name="错误消息")
    stack_trace = models.TextField(null=True, blank=True, verbose_name="堆栈跟踪")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="相关用户")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP地址")
    endpoint = models.CharField(max_length=255, null=True, blank=True, verbose_name="端点")
    user_agent = models.TextField(null=True, blank=True, verbose_name="用户代理")
    resolved = models.BooleanField(default=False, verbose_name="是否已解决")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="解决时间")
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name="resolved_errors", verbose_name="解决人")
    
    class Meta:
        verbose_name = "错误日志"
        verbose_name_plural = "错误日志"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["error_type"]),
            models.Index(fields=["severity"]),
            models.Index(fields=["resolved"]),
        ]

    def __str__(self):
        return f"{self.get_error_type_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class PerformanceAlert(models.Model):
    """性能告警模型"""
    
    ALERT_TYPES = [
        ('cpu_high', 'CPU使用率过高'),
        ('memory_high', '内存使用率过高'),
        ('disk_high', '磁盘使用率过高'),
        ('response_time_slow', '响应时间过慢'),
        ('error_rate_high', '错误率过高'),
        ('connection_high', '连接数过高'),
        ('database_slow', '数据库查询缓慢'),
    ]
    
    ALERT_STATUS = [
        ('active', '活跃'),
        ('acknowledged', '已确认'),
        ('resolved', '已解决'),
        ('dismissed', '已忽略'),
    ]
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="告警时间")
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES, verbose_name="告警类型")
    status = models.CharField(max_length=20, choices=ALERT_STATUS, default='active', verbose_name="状态")
    title = models.CharField(max_length=255, verbose_name="告警标题")
    message = models.TextField(verbose_name="告警消息")
    threshold_value = models.FloatField(verbose_name="阈值")
    actual_value = models.FloatField(verbose_name="实际值")
    severity = models.CharField(max_length=20, choices=ErrorLog.SEVERITY_LEVELS, verbose_name="严重程度")
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name="acknowledged_alerts", verbose_name="确认人")
    acknowledged_at = models.DateTimeField(null=True, blank=True, verbose_name="确认时间")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="解决时间")
    
    class Meta:
        verbose_name = "性能告警"
        verbose_name_plural = "性能告警"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["alert_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["severity"]),
        ]

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class AnalyticsReport(models.Model):
    """分析报告模型"""
    
    REPORT_TYPES = [
        ('daily', '日报'),
        ('weekly', '周报'),
        ('monthly', '月报'),
        ('custom', '自定义'),
    ]
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, verbose_name="报告类型")
    title = models.CharField(max_length=255, verbose_name="报告标题")
    description = models.TextField(null=True, blank=True, verbose_name="报告描述")
    start_date = models.DateTimeField(verbose_name="开始时间")
    end_date = models.DateTimeField(verbose_name="结束时间")
    data = models.JSONField(verbose_name="报告数据")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建人")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    is_public = models.BooleanField(default=False, verbose_name="是否公开")
    
    class Meta:
        verbose_name = "分析报告"
        verbose_name_plural = "分析报告"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["report_type"]),
            models.Index(fields=["start_date", "end_date"]),
            models.Index(fields=["created_by"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.created_at.strftime('%Y-%m-%d')}"


class UserBehaviorMetrics(models.Model):
    """用户行为指标模型"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    date = models.DateField(verbose_name="日期")
    page_views = models.IntegerField(default=0, verbose_name="页面浏览量")
    session_duration = models.IntegerField(default=0, verbose_name="会话时长(秒)")
    api_calls = models.IntegerField(default=0, verbose_name="API调用次数")
    login_count = models.IntegerField(default=0, verbose_name="登录次数")
    last_activity = models.DateTimeField(verbose_name="最后活动时间")
    
    class Meta:
        verbose_name = "用户行为指标"
        verbose_name_plural = "用户行为指标"
        ordering = ["-date", "-last_activity"]
        unique_together = ["user", "date"]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["user", "date"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class SystemHealthScore(models.Model):
    """系统健康评分模型"""
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="评分时间")
    overall_score = models.FloatField(verbose_name="总体评分")
    performance_score = models.FloatField(verbose_name="性能评分")
    reliability_score = models.FloatField(verbose_name="可靠性评分")
    security_score = models.FloatField(verbose_name="安全性评分")
    user_experience_score = models.FloatField(verbose_name="用户体验评分")
    details = models.JSONField(verbose_name="详细评分")
    
    class Meta:
        verbose_name = "系统健康评分"
        verbose_name_plural = "系统健康评分"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"系统健康评分 - {self.overall_score} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
