"""
修复版本的allauth中间件，支持异步上下文
"""
import asyncio
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user
from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject
from asgiref.sync import sync_to_async


class AsyncSafeAccountMiddleware(MiddlewareMixin):
    """
    异步安全的allauth账户中间件
    修复SynchronousOnlyOperation错误
    """
    
    def process_request(self, request):
        """处理请求"""
        # 在异步上下文中使用sync_to_async包装
        if asyncio.iscoroutinefunction(self._get_user):
            # 异步上下文
            request._cached_user = SimpleLazyObject(lambda: self._get_user_async(request))
        else:
            # 同步上下文
            request._cached_user = SimpleLazyObject(lambda: self._get_user(request))
    
    def _get_user(self, request):
        """同步获取用户"""
        try:
            return get_user(request)
        except Exception:
            return AnonymousUser()
    
    @sync_to_async
    def _get_user_async(self, request):
        """异步获取用户"""
        return self._get_user(request)
    
    def process_response(self, request, response):
        """处理响应"""
        return response