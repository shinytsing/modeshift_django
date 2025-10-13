"""
修复版本的allauth视图，支持异步上下文
"""
from functools import wraps
from asgiref.sync import sync_to_async
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import asyncio


def async_safe_view(view_func):
    """
    装饰器：使同步视图在异步上下文中安全运行
    """
    @wraps(view_func)
    async def async_wrapper(request, *args, **kwargs):
        # 检查是否在异步上下文中
        try:
            loop = asyncio.get_running_loop()
            # 在异步上下文中，使用sync_to_async包装
            sync_view = sync_to_async(view_func, thread_sensitive=True)
            return await sync_view(request, *args, **kwargs)
        except RuntimeError:
            # 不在异步上下文中，直接调用
            return view_func(request, *args, **kwargs)
    
    return async_wrapper


def async_safe_method_decorator(decorator):
    """
    方法装饰器：使类方法在异步上下文中安全运行
    """
    def decorator_wrapper(func):
        @wraps(func)
        async def async_wrapper(self, request, *args, **kwargs):
            try:
                loop = asyncio.get_running_loop()
                # 在异步上下文中，使用sync_to_async包装
                sync_method = sync_to_async(func, thread_sensitive=True)
                return await sync_method(self, request, *args, **kwargs)
            except RuntimeError:
                # 不在异步上下文中，直接调用
                return func(self, request, *args, **kwargs)
        return async_wrapper
    return decorator_wrapper
