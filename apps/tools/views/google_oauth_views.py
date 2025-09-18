from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from apps.tools.services.google_oauth_service import google_oauth_service

class GoogleOAuthStartView(View):
    """开始Google OAuth登录"""
    
    def get(self, request):
        auth_url = google_oauth_service.get_auth_url()
        return redirect(auth_url)

class GoogleOAuthCallbackView(View):
    """Google OAuth回调处理"""
    
    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')
        
        if not code:
            return JsonResponse({'error': '缺少授权码'}, status=400)
        
        # 用授权码换取访问令牌
        token_data = google_oauth_service.exchange_code_for_token(code)
        if not token_data:
            return JsonResponse({'error': '获取令牌失败'}, status=400)
        
        access_token = token_data.get('access_token')
        if not access_token:
            return JsonResponse({'error': '令牌无效'}, status=400)
        
        # 获取用户信息
        user_info = google_oauth_service.get_user_info(access_token)
        if not user_info:
            return JsonResponse({'error': '获取用户信息失败'}, status=400)
        
        # 创建或获取用户
        email = user_info.get('email')
        name = user_info.get('name', '')
        
        if not email:
            return JsonResponse({'error': '无法获取用户邮箱'}, status=400)
        
        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                'email': email,
                'first_name': name.split(' ')[0] if name else '',
                'last_name': ' '.join(name.split(' ')[1:]) if len(name.split(' ')) > 1 else '',
                'is_active': True
            }
        )
        
        if created:
            user.set_unusable_password()
            user.save()
        
        # 登录用户
        login(request, user)
        
        return JsonResponse({
            'success': True,
            'message': '登录成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'name': f'{user.first_name} {user.last_name}'.strip()
            }
        })

class GoogleOAuthTestView(View):
    """Google OAuth测试"""
    
    def get(self, request):
        connection_ok = google_oauth_service.test_connection()
        
        return JsonResponse({
            'connection_ok': connection_ok,
            'client_id': google_oauth_service.client_id,
            'redirect_uri': google_oauth_service.redirect_uri,
            'message': 'Google OAuth服务测试'
        })
