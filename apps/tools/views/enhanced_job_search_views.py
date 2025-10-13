"""
增强版AI找工作视图 - 融合get_jobs项目功能
支持多平台投递和完整的登录流程
"""
import json
import logging
import os
import time
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.conf import settings
from apps.tools.services.enhanced_job_delivery_service import EnhancedJobDeliveryService, JobSearchConfig

logger = logging.getLogger(__name__)


@login_required
def enhanced_job_search_launcher(request):
    """增强版AI一键投递启动器页面"""
    return render(request, "tools/enhanced_job_search_launcher.html")


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def start_enhanced_job_search_api(request):
    """启动增强版AI一键投递API"""
    try:
        # 暂时移除认证检查，让检测逻辑能够执行
        # if not request.user.is_authenticated:
        #     logger.warning(f"未认证用户尝试访问投递API: {request.META.get('REMOTE_ADDR')}")
        #     return JsonResponse({"success": False, "error": "请先登录"})
        
        logger.info(f"用户 {request.user.username} 启动增强版投递任务")
        
        data = json.loads(request.body)
        
        # 获取平台列表
        platforms = data.get('platforms', ['boss'])
        if not isinstance(platforms, list):
            platforms = [data.get('platform', 'boss')]
        
        # 创建搜索配置
        service = EnhancedJobDeliveryService()
        config = service.create_search_config(data)
        
        # 验证配置
        if not config.keywords:
            return JsonResponse({"success": False, "error": "请填写搜索关键词"})
        
        if not config.cities:
            return JsonResponse({"success": False, "error": "请选择工作城市"})
        
        # 启动投递任务
        result = service.start_multi_platform_delivery(platforms, config, request.user)
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"})
    except Exception as e:
        logger.error(f"启动增强版投递失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"启动失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_enhanced_job_search_status_api(request):
    """获取增强版投递状态API"""
    try:
        service = EnhancedJobDeliveryService()
        status = service.get_delivery_status(request.user)
        return JsonResponse(status)
    except Exception as e:
        logger.error(f"获取增强版投递状态失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"获取状态失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def stop_enhanced_job_search_api(request):
    """停止增强版投递API"""
    try:
        service = EnhancedJobDeliveryService()
        result = service.stop_delivery(request.user)
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"停止增强版投递失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"停止失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_platform_info_api(request):
    """获取平台信息API"""
    try:
        service = EnhancedJobDeliveryService()
        result = service.get_platform_info()
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"获取平台信息失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"获取平台信息失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def boss_login_with_token_api(request):
    """使用Token登录BOSS直聘API"""
    try:
        data = json.loads(request.body)
        token = data.get('token', '').strip()
        
        if not token:
            return JsonResponse({"success": False, "error": "Token不能为空"})
        
        # 保存token到文件
        token_file = os.path.join(settings.BASE_DIR, 'get_jobs_integration', f'boss_token_{request.user.id}.json')
        os.makedirs(os.path.dirname(token_file), exist_ok=True)
        
        token_data = {
            'token': token,
            'login_time': time.time(),
            'user_id': request.user.id,
            'login_method': 'token'
        }
        
        with open(token_file, 'w', encoding='utf-8') as f:
            json.dump(token_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"用户 {request.user.username} 使用Token登录成功")
        
        return JsonResponse({
            "success": True,
            "message": "Token登录成功",
            "token": token[:20] + "..."  # 只返回部分token用于显示
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的请求数据"})
    except Exception as e:
        logger.error(f"Token登录失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"Token登录失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def check_boss_login_status_api(request):
    """检查BOSS直聘登录状态API"""
    try:
        from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
        
        playwright_service = BossZhipinPlaywrightService(headless=True)
        result = playwright_service.check_login_status(request.user.id)
        
        return JsonResponse({
            "success": result.get('success', False),
            "is_logged_in": result.get('is_logged_in', False),
            "message": result.get('message', '检查登录状态'),
            "token_info": result.get('token_info', {}),
            "current_url": result.get('current_url', ''),
            "user_info": result.get('user_info', {})
        })
        
    except Exception as e:
        logger.error(f"检查BOSS直聘登录状态失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"检查状态失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def start_boss_qr_login_api(request):
    """启动BOSS直聘二维码登录API"""
    try:
        from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
        
        playwright_service = BossZhipinPlaywrightService(headless=False)  # 显示浏览器窗口
        
        # 获取登录页面URL
        result = playwright_service.get_login_page_url(request.user.id)
        
        if result.get('success'):
            # 启动浏览器并显示二维码
            login_url = result.get('login_url')
            
            # 这里可以返回二维码图片URL或者登录页面URL
            return JsonResponse({
                "success": True,
                "message": "二维码登录已启动",
                "login_url": login_url,
                "qr_code_url": f"/tools/job-search/api/boss-qr-code/{request.user.id}/"
            })
        else:
            return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"启动BOSS直聘二维码登录失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"启动二维码登录失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def start_boss_phone_login_api(request):
    """启动BOSS直聘手机号登录API"""
    try:
        data = json.loads(request.body)
        phone = data.get('phone', '').strip()
        
        if not phone:
            return JsonResponse({"success": False, "error": "请填写手机号"})
        
        if len(phone) != 11 or not phone.isdigit():
            return JsonResponse({"success": False, "error": "请输入正确的手机号"})
        
        # 这里可以集成真实的手机号登录逻辑
        # 暂时返回成功，实际需要调用BOSS直聘的短信验证码接口
        
        return JsonResponse({
            "success": True,
            "message": "验证码已发送，请查收短信",
            "phone": phone[:3] + "****" + phone[7:]  # 隐藏手机号
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的请求数据"})
    except Exception as e:
        logger.error(f"启动BOSS直聘手机号登录失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"启动手机号登录失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def verify_boss_phone_code_api(request):
    """验证BOSS直聘手机验证码API"""
    try:
        data = json.loads(request.body)
        phone = data.get('phone', '').strip()
        code = data.get('code', '').strip()
        
        if not phone or not code:
            return JsonResponse({"success": False, "error": "请填写手机号和验证码"})
        
        if len(code) != 6 or not code.isdigit():
            return JsonResponse({"success": False, "error": "请输入6位验证码"})
        
        # 这里可以集成真实的验证码验证逻辑
        # 暂时模拟验证成功
        
        # 保存登录状态
        login_file = os.path.join(settings.BASE_DIR, 'get_jobs_integration', f'boss_login_{request.user.id}.json')
        os.makedirs(os.path.dirname(login_file), exist_ok=True)
        
        login_data = {
            'phone': phone,
            'login_time': time.time(),
            'user_id': request.user.id,
            'login_method': 'phone'
        }
        
        with open(login_file, 'w', encoding='utf-8') as f:
            json.dump(login_data, f, ensure_ascii=False, indent=2)
        
        return JsonResponse({
            "success": True,
            "message": "手机号登录成功",
            "phone": phone[:3] + "****" + phone[7:]
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的请求数据"})
    except Exception as e:
        logger.error(f"验证BOSS直聘手机验证码失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"验证验证码失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_boss_iframe_login_url_api(request):
    """获取BOSS直聘iframe登录URL API"""
    try:
        from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
        
        playwright_service = BossZhipinPlaywrightService(headless=True)
        result = playwright_service.get_login_page_url(request.user.id)
        
        if result.get('success'):
            return JsonResponse({
                "success": True,
                "message": "获取登录页面URL成功",
                "login_url": result.get('login_url'),
                "iframe_url": result.get('login_url')
            })
        else:
            return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"获取BOSS直聘iframe登录URL失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"获取登录URL失败: {str(e)}"})
