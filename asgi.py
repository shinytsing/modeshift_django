"""
ASGI config for QAToolBox project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import asyncio

import django
from django.core.asgi import get_asgi_application
from asgiref.sync import sync_to_async

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack

# 设置Django设置模块
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

# 初始化Django
django.setup()

# 创建异步安全的HTTP应用包装器
def create_async_safe_http_app():
    """创建异步安全的HTTP应用"""
    sync_app = get_asgi_application()
    
    async def async_app(scope, receive, send):
        """异步HTTP应用包装器"""
        if scope["type"] == "http":
            # 对于HTTP请求，直接调用ASGI应用
            try:
                await sync_app(scope, receive, send)
            except Exception as e:
                # 如果调用失败，记录错误
                print(f"❌ HTTP请求处理失败: {e}")
                # 发送500错误响应
                await send({
                    'type': 'http.response.start',
                    'status': 500,
                    'headers': [[b'content-type', b'text/plain']],
                })
                await send({
                    'type': 'http.response.body',
                    'body': b'Internal Server Error',
                })
        else:
            # 其他类型的请求直接传递
            await sync_app(scope, receive, send)
    
    return async_app

# 导入WebSocket路由（在Django设置后导入）
try:
    from apps.tools.routing import websocket_urlpatterns

    print(f"✅ WebSocket路由加载成功，路由数量: {len(websocket_urlpatterns)}")
    for pattern in websocket_urlpatterns:
        print(f"📍 WebSocket路由: {pattern.pattern.regex.pattern}")
except Exception as e:
    print(f"❌ WebSocket路由加载失败: {e}")
    websocket_urlpatterns = []

application = ProtocolTypeRouter(
    {
        "http": create_async_safe_http_app(),
        "websocket": SessionMiddlewareStack(
            AuthMiddlewareStack(
                URLRouter(websocket_urlpatterns)
            )
        ),
    }
)

print("🚀 ASGI应用已配置完成")
