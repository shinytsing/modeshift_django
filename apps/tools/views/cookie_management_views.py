"""
Cookie 管理视图
提供 cookie 的保存、获取、验证等功能
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from ..services.cookie_storage_service import get_cookie_storage_service

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def save_cookies_api(request):
    """保存用户 cookies API"""
    try:
        data = json.loads(request.body)
        platform = data.get('platform', 'boss')
        cookies = data.get('cookies', {})
        
        if not cookies:
            return JsonResponse({
                "success": False,
                "error": "Cookies 不能为空"
            })
        
        # 获取 cookie 存储服务
        cookie_service = get_cookie_storage_service(request.user)
        
        # 保存 cookies
        success = cookie_service.save_cookies(platform, cookies)
        
        if success:
            return JsonResponse({
                "success": True,
                "message": f"成功保存 {len(cookies)} 个 {platform} cookies",
                "cookie_count": len(cookies)
            })
        else:
            return JsonResponse({
                "success": False,
                "error": "保存 cookies 失败"
            })
            
    except Exception as e:
        logger.error(f"保存 cookies API 失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": f"保存失败: {str(e)}"
        })


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_cookies_api(request):
    """获取用户 cookies API"""
    try:
        platform = request.GET.get('platform', 'boss')
        
        # 获取 cookie 存储服务
        cookie_service = get_cookie_storage_service(request.user)
        
        # 获取 cookies
        cookies = cookie_service.get_cookies(platform)
        
        return JsonResponse({
            "success": True,
            "platform": platform,
            "cookies": cookies,
            "cookie_count": len(cookies)
        })
        
    except Exception as e:
        logger.error(f"获取 cookies API 失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": f"获取失败: {str(e)}"
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def validate_cookies_api(request):
    """验证 cookies 有效性 API"""
    try:
        data = json.loads(request.body)
        platform = data.get('platform', 'boss')
        
        # 获取 cookie 存储服务
        cookie_service = get_cookie_storage_service(request.user)
        
        # 验证 cookies
        validation_result = cookie_service.validate_cookies(platform)
        
        return JsonResponse(validation_result)
        
    except Exception as e:
        logger.error(f"验证 cookies API 失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": f"验证失败: {str(e)}"
        })


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_cookies_info_api(request):
    """获取用户所有 cookies 信息 API"""
    try:
        # 获取 cookie 存储服务
        cookie_service = get_cookie_storage_service(request.user)
        
        # 获取 cookies 信息
        cookies_info = cookie_service.get_user_cookies_info()
        
        return JsonResponse({
            "success": True,
            "cookies_info": cookies_info
        })
        
    except Exception as e:
        logger.error(f"获取 cookies 信息 API 失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": f"获取失败: {str(e)}"
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def clear_cookies_api(request):
    """清除 cookies API"""
    try:
        data = json.loads(request.body)
        platform = data.get('platform')  # 如果为空则清除所有平台的 cookies
        
        # 获取 cookie 存储服务
        cookie_service = get_cookie_storage_service(request.user)
        
        # 清除 cookies
        success = cookie_service.clear_cookies(platform)
        
        if success:
            message = f"成功清除 {platform} cookies" if platform else "成功清除所有 cookies"
            return JsonResponse({
                "success": True,
                "message": message
            })
        else:
            return JsonResponse({
                "success": False,
                "error": "清除 cookies 失败"
            })
            
    except Exception as e:
        logger.error(f"清除 cookies API 失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": f"清除失败: {str(e)}"
        })
