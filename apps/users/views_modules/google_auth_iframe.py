import logging
import requests
import os
import secrets
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from django.contrib import messages
from django.conf import settings

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class GoogleAuthIframeView(View):
    def get(self, request):
        # 生成state参数
        state = secrets.token_urlsafe(32)
        request.session['google_oauth_state'] = state
        
        # 构建授权URL
        client_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
        redirect_uri = f"{settings.SITE_URL}/users/auth/google/iframe-callback/"
        
        auth_url = f'https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&scope=openid+email+profile&response_type=code&access_type=offline&prompt=consent&state={state}'
        
        return render(request, 'users/google_auth_iframe.html', {
            'auth_url': auth_url
        })

@method_decorator(csrf_exempt, name='dispatch')
class GoogleAuthIframeCallbackView(View):
    def post(self, request):
        try:
            import json
            data = json.loads(request.body)
            code = data.get('code')
            state = data.get('state')
            session_state = request.session.pop('google_oauth_state', None)
            
            if not code:
                return JsonResponse({'success': False, 'message': '未收到授权码'})
                
            if not state or state != session_state:
                logger.warning(f'CSRF state mismatch. Received: {state}, Expected: {session_state}')
                return JsonResponse({'success': False, 'message': 'CSRF验证失败'})
            
            # 处理授权码
            result = self.process_auth_code(request, code)
            return JsonResponse(result)
                
        except Exception as e:
            logger.error(f'处理Google OAuth回调失败: {e}', exc_info=True)
            return JsonResponse({'success': False, 'message': f'Google登录失败: {str(e)}'})
    
    def process_auth_code(self, request, auth_code):
        try:
            # 1. 交换授权码获取访问令牌
            token_data = self.exchange_code_for_token(auth_code)
            access_token = token_data.get('access_token')
            if not access_token:
                return {'success': False, 'message': '获取访问令牌失败'}
            
            # 2. 使用访问令牌获取用户信息
            user_info = self.get_user_info(access_token)
            google_id = user_info.get('sub')
            email = user_info.get('email')
            
            if not google_id or not email:
                return {'success': False, 'message': '获取用户信息失败'}
            
            # 3. 创建或更新用户
            from django.contrib.auth import get_user_model
            from allauth.socialaccount.models import SocialAccount
            
            User = get_user_model()
            
            try:
                social_account = SocialAccount.objects.get(provider='google', uid=google_id)
                user = social_account.user
                user.email = email
                user.first_name = user_info.get('given_name', '')
                user.last_name = user_info.get('family_name', '')
                user.save()
            except SocialAccount.DoesNotExist:
                user, created = User.objects.get_or_create(email=email)
                if created:
                    user.username = email
                    user.first_name = user_info.get('given_name', '')
                    user.last_name = user_info.get('family_name', '')
                    user.save()
                
                social_account = SocialAccount.objects.create(
                    user=user,
                    provider='google',
                    uid=google_id,
                    extra_data=user_info
                )
            
            # 4. 登录用户
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            return {
                'success': True, 
                'message': '登录成功',
                'email': email,
                'user_id': user.id
            }
            
        except Exception as e:
            logger.error(f'处理授权码时发生错误: {e}', exc_info=True)
            return {'success': False, 'message': f'处理授权码时发生错误: {str(e)}'}
    
    def exchange_code_for_token(self, auth_code):
        client_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')
        redirect_uri = f"{settings.SITE_URL}/users/auth/google/iframe-callback/"
        
        proxy_config = {
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890'
        }
        
        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'client_id': client_id,
                'client_secret': client_secret,
                'code': auth_code,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code',
            },
            proxies=proxy_config,
            verify=False,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def get_user_info(self, access_token):
        proxy_config = {
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890'
        }
        
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers=headers,
            proxies=proxy_config,
            verify=False,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
