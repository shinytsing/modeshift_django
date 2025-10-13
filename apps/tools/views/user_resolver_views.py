from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging

from apps.tools.services.social_media.real_crawler import RealSocialMediaCrawler
from apps.tools.views.base import success_response, error_response

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class UserResolverView(View):
    """用户ID解析API"""
    
    def get(self, request):
        """获取用户映射信息"""
        try:
            username = request.GET.get('username')
            if not username:
                return error_response("缺少用户名参数", status=400)
            
            crawler = RealSocialMediaCrawler()
            mapping_info = crawler.get_user_mapping_info(username)
            
            return success_response({
                'mapping_info': mapping_info
            })
            
        except Exception as e:
            logger.error(f"获取用户映射信息失败: {e}")
            return error_response("获取用户映射信息失败", status=500)
    
    def post(self, request):
        """添加用户映射"""
        try:
            data = json.loads(request.body)
            username = data.get('username')
            user_id = data.get('user_id')
            token = data.get('token', '')
            
            if not username or not user_id:
                return error_response("缺少用户名或用户ID参数", status=400)
            
            crawler = RealSocialMediaCrawler()
            crawler.add_user_mapping(username, user_id, token)
            
            # 获取更新后的映射信息
            mapping_info = crawler.get_user_mapping_info(username)
            
            return success_response({
                'message': '用户映射添加成功',
                'mapping_info': mapping_info
            })
            
        except Exception as e:
            logger.error(f"添加用户映射失败: {e}")
            return error_response("添加用户映射失败", status=500)


@method_decorator(csrf_exempt, name='dispatch')
class UserResolverTestView(View):
    """用户ID解析测试API"""
    
    def post(self, request):
        """测试用户ID解析"""
        try:
            data = json.loads(request.body)
            username = data.get('username')
            user_id = data.get('user_id', username)
            
            if not username:
                return error_response("缺少用户名参数", status=400)
            
            from apps.tools.models.social_media_models import SocialMediaSubscription
            
            # 创建临时订阅对象
            temp_subscription = SocialMediaSubscription(
                target_user_name=username,
                target_user_id=user_id
            )
            
            crawler = RealSocialMediaCrawler()
            real_user_id, token = crawler.get_user_id_and_token(temp_subscription)
            
            return success_response({
                'original_username': username,
                'original_user_id': user_id,
                'resolved_user_id': real_user_id,
                'token': token[:20] + '...' if token else '',
                'has_mapping': username in crawler.username_to_id_mapping,
                'mapping_info': crawler.get_user_mapping_info(username)
            })
            
        except Exception as e:
            logger.error(f"测试用户ID解析失败: {e}")
            return error_response("测试用户ID解析失败", status=500)
