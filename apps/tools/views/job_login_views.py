"""
Boss直聘登录相关API视图
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def boss_status_api(request):
    """检查Boss直聘登录状态 - 超快速版本"""
    try:
        logger.info(f"用户 {request.user.username} 检查Boss直聘登录状态")
        
        # 直接返回默认状态，避免任何长时间操作
        result = {
            "success": True,
            "is_logged_in": False,
            "message": "需要登录",
            "token_info": {},
            "current_url": "",
            "found_indicator": "",
            "login_confidence": 0,
            "token_validation": {},
            "cached": False,
            "fast_mode": True
        }
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"检查Boss直聘登录状态失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": f"检查登录状态失败: {str(e)}"
        })


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def boss_status_detailed_api(request):
    """详细检查Boss直聘登录状态 - 完整版本"""
    try:
        logger.info(f"用户 {request.user.username} 详细检查Boss直聘登录状态")
        
        # 调用Boss直聘服务检查登录状态
        from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
        
        playwright_service = BossZhipinPlaywrightService(headless=True)
        result = playwright_service.check_login_status(request.user.id)
        
        return JsonResponse({
            "success": result.get('success', False),
            "is_logged_in": result.get('is_logged_in', False),
            "message": result.get('message', '检查登录状态'),
            "token_info": result.get('token_info', {}),
            "current_url": result.get('current_url', ''),
            "found_indicator": result.get('found_indicator', ''),
            "login_confidence": result.get('login_confidence', 0),
            "token_validation": result.get('token_validation', {}),
            "detailed": True
        })
        
    except Exception as e:
        logger.error(f"详细检查Boss直聘登录状态失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "is_logged_in": False,
            "message": f"检查失败: {str(e)}",
            "token_info": {},
            "current_url": "",
            "found_indicator": "",
            "login_confidence": 0,
            "token_validation": {},
            "detailed": True
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def boss_login_api(request):
    """启动Boss直聘登录流程"""
    try:
        data = json.loads(request.body)
        method = data.get('method', 'qr')
        
        logger.info(f"用户 {request.user.username} 启动Boss直聘登录，方式: {method}")
        
        if method == 'qr':
            # 二维码登录
            return JsonResponse({
                "success": True,
                "qr_code_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",  # 临时占位
                "message": "请扫描二维码登录"
            })
        elif method == 'phone':
            # 手机登录
            return JsonResponse({
                "success": True,
                "message": "请使用手机号登录"
            })
        elif method == 'iframe':
            # iframe登录
            return JsonResponse({
                "success": True,
                "login_url": "https://login.zhipin.com/",
                "message": "请在弹窗中完成登录"
            })
        else:
            return JsonResponse({
                "success": False,
                "error": "不支持的登录方式"
            })
            
    except Exception as e:
        logger.error(f"启动Boss直聘登录失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": f"启动登录失败: {str(e)}"
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def boss_send_sms_api(request):
    """发送短信验证码"""
    try:
        data = json.loads(request.body)
        phone = data.get('phone')
        
        if not phone:
            return JsonResponse({
                "success": False,
                "error": "手机号不能为空"
            })
        
        logger.info(f"用户 {request.user.username} 请求发送短信验证码到: {phone}")
        
        # 这里应该调用Boss直聘API发送验证码
        # 暂时返回成功
        return JsonResponse({
            "success": True,
            "message": "验证码已发送"
        })
        
    except Exception as e:
        logger.error(f"发送短信验证码失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": f"发送验证码失败: {str(e)}"
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def boss_phone_login_api(request):
    """手机号验证码登录"""
    try:
        data = json.loads(request.body)
        phone = data.get('phone')
        code = data.get('code')
        
        if not phone or not code:
            return JsonResponse({
                "success": False,
                "error": "手机号和验证码不能为空"
            })
        
        logger.info(f"用户 {request.user.username} 尝试手机号登录: {phone}")
        
        # 这里应该调用Boss直聘API验证登录
        # 暂时返回成功
        return JsonResponse({
            "success": True,
            "token": "mock_token_" + str(hash(phone + code)),
            "message": "登录成功"
        })
        
    except Exception as e:
        logger.error(f"手机号登录失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": f"登录失败: {str(e)}"
        })
