"""
Google Auth 代理视图
提供服务器端 Google OAuth 代理功能
"""

import logging
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.core.exceptions import ValidationError
from django.conf import settings
from ..services.google_auth_proxy import GoogleAuthProxyViewMixin

logger = logging.getLogger(__name__)


class GoogleAuthProxyView(View, GoogleAuthProxyViewMixin):
    """Google Auth 代理视图"""
    
    def get(self, request):
        """处理 Google Auth 授权请求"""
        try:
            # 生成授权 URL
            auth_url = self.get_auth_url_with_state(request)
            
            # 重定向到 Google 授权页面
            return redirect(auth_url)
            
        except Exception as e:
            logger.error(f"Google auth initiation failed: {e}")
            messages.error(request, "Google 登录初始化失败")
            return redirect('/')
    
    def post(self, request):
        """处理 AJAX 请求获取授权 URL"""
        try:
            auth_url = self.get_auth_url_with_state(request)
            
            return JsonResponse({
                'success': True,
                'auth_url': auth_url,
                'message': 'Google 授权 URL 生成成功'
            })
            
        except Exception as e:
            logger.error(f"Google auth URL generation failed: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e),
                'message': 'Google 授权 URL 生成失败'
            }, status=400)


class GoogleAuthCallbackView(View, GoogleAuthProxyViewMixin):
    """Google Auth 回调处理视图"""
    
    def get(self, request):
        """处理 Google Auth 回调"""
        try:
            # 获取授权码和 state 参数
            code = request.GET.get('code')
            state = request.GET.get('state')
            error = request.GET.get('error')
            
            if error:
                logger.error(f"Google auth error: {error}")
                messages.error(request, f"Google 登录失败: {error}")
                return redirect('/')
            
            if not code:
                logger.error("No authorization code received")
                messages.error(request, "未收到授权码")
                return redirect('/')
            
            # 执行用户认证
            user, created = self.handle_auth_callback(request, code, state)
            
            # 登录用户
            login(request, user)
            
            # 设置成功消息
            if created:
                messages.success(request, f"欢迎！已为您创建新账户：{user.email}")
            else:
                messages.success(request, f"欢迎回来！{user.email}")
            
            logger.info(f"User {user.email} successfully authenticated via Google")
            
            # 重定向到首页或指定页面
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
            
        except ValidationError as e:
            logger.error(f"Google auth validation error: {e}")
            messages.error(request, f"Google 登录验证失败: {str(e)}")
            return redirect('/')
            
        except Exception as e:
            logger.error(f"Google auth callback failed: {e}")
            messages.error(request, "Google 登录处理失败")
            return redirect('/')


@method_decorator(csrf_exempt, name='dispatch')
class GoogleAuthStatusView(View):
    """Google Auth 状态检查视图"""
    
    def get(self, request):
        """检查 Google Auth 配置状态"""
        try:
            from ..services.google_auth_proxy import GoogleAuthProxyService
            
            auth_proxy = GoogleAuthProxyService()
            
            # 检查配置
            config_status = {
                'client_id_configured': bool(auth_proxy.client_id),
                'client_secret_configured': bool(auth_proxy.client_secret),
                'redirect_uri': auth_proxy.redirect_uri,
                'proxy_enabled': True,  # 我们总是启用代理
            }
            
            # 测试代理连接
            try:
                import requests
                response = requests.get(
                    'https://www.google.com',
                    proxies=auth_proxy.proxy_config,
                    timeout=5
                )
                config_status['proxy_working'] = response.status_code == 200
            except Exception as e:
                config_status['proxy_working'] = False
                config_status['proxy_error'] = str(e)
            
            return JsonResponse({
                'success': True,
                'config': config_status,
                'message': 'Google Auth 状态检查完成'
            })
            
        except Exception as e:
            logger.error(f"Google auth status check failed: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e),
                'message': 'Google Auth 状态检查失败'
            }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def google_auth_initiate(request):
    """Google Auth 初始化端点（AJAX）"""
    try:
        from ..services.google_auth_proxy import GoogleAuthProxyService
        
        auth_proxy = GoogleAuthProxyService()
        
        # 生成授权 URL
        state = request.session.session_key or str(request.session.create())
        auth_url = auth_proxy.get_auth_url(state)
        
        return JsonResponse({
            'success': True,
            'auth_url': auth_url,
            'message': 'Google 授权 URL 生成成功'
        })
        
    except Exception as e:
        logger.error(f"Google auth initiation failed: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Google 授权初始化失败'
        }, status=400)
