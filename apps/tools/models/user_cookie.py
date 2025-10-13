"""
用户 Cookie 管理模型
参考 get_jobs 项目的实现方式
"""
from django.db import models
from django.contrib.auth.models import User
import json
import logging

logger = logging.getLogger(__name__)


class UserCookie(models.Model):
    """用户 Cookie 存储模型"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    platform = models.CharField(max_length=50, verbose_name="平台", help_text="如: boss, lagou, liepin 等")
    cookies = models.JSONField(verbose_name="Cookie 数据", help_text="存储完整的 cookie 信息")
    is_active = models.BooleanField(default=True, verbose_name="是否有效")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="过期时间")
    
    class Meta:
        verbose_name = "用户 Cookie"
        verbose_name_plural = "用户 Cookie"
        unique_together = ['user', 'platform']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.platform} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_cookies_dict(self):
        """获取 cookies 字典格式"""
        try:
            if isinstance(self.cookies, dict):
                return self.cookies
            elif isinstance(self.cookies, str):
                return json.loads(self.cookies)
            else:
                return {}
        except Exception as e:
            logger.error(f"解析 cookies 失败: {str(e)}")
            return {}
    
    def get_playwright_cookies(self):
        """获取 Playwright 格式的 cookies"""
        cookies_dict = self.get_cookies_dict()
        playwright_cookies = []
        
        for name, value in cookies_dict.items():
            playwright_cookies.append({
                'name': name,
                'value': value,
                'domain': '.zhipin.com' if self.platform == 'boss' else '.lagou.com',
                'path': '/',
                'httpOnly': False,
                'secure': False,
                'sameSite': 'Lax'
            })
        
        return playwright_cookies
    
    def is_expired(self):
        """检查是否过期"""
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False
    
    def save_cookies_from_browser(self, cookies_dict):
        """从浏览器 cookies 保存"""
        try:
            self.cookies = cookies_dict
            self.is_active = True
            self.save()
            logger.info(f"成功保存用户 {self.user.username} 的 {self.platform} cookies")
            return True
        except Exception as e:
            logger.error(f"保存 cookies 失败: {str(e)}")
            return False


class CookieSession(models.Model):
    """Cookie 会话管理"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    platform = models.CharField(max_length=50, verbose_name="平台")
    session_id = models.CharField(max_length=100, unique=True, verbose_name="会话ID")
    storage_state = models.JSONField(verbose_name="存储状态", help_text="Playwright storage state")
    is_active = models.BooleanField(default=True, verbose_name="是否有效")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    last_used = models.DateTimeField(auto_now=True, verbose_name="最后使用时间")
    
    class Meta:
        verbose_name = "Cookie 会话"
        verbose_name_plural = "Cookie 会话"
        ordering = ['-last_used']
    
    def __str__(self):
        return f"{self.user.username} - {self.platform} - {self.session_id}"
    
    def get_storage_state(self):
        """获取 Playwright storage state"""
        try:
            if isinstance(self.storage_state, dict):
                return self.storage_state
            elif isinstance(self.storage_state, str):
                return json.loads(self.storage_state)
            else:
                return {}
        except Exception as e:
            logger.error(f"解析 storage state 失败: {str(e)}")
            return {}
    
    def save_storage_state(self, storage_state):
        """保存 Playwright storage state"""
        try:
            self.storage_state = storage_state
            self.save()
            logger.info(f"成功保存用户 {self.user.username} 的 {self.platform} storage state")
            return True
        except Exception as e:
            logger.error(f"保存 storage state 失败: {str(e)}")
            return False
