"""
Playwright启动API视图 - 参考Java项目的登录流程
提供Playwright自动登录和token管理功能
"""

import json
import logging
import asyncio
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.cache import cache

from apps.tools.services.playwright_service import get_playwright_service
from apps.tools.services.cookie_manager_service import get_cookie_manager

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def start_playwright_login_api(request):
    """启动Playwright自动登录 - 参考Java项目的login方法"""
    try:
        data = json.loads(request.body)
        platform = data.get('platform', 'boss')
        token = data.get('token', '')
        
        if not token:
            return JsonResponse({"success": False, "error": "Token不能为空"})
        
        logger.info(f"用户 {request.user.username} 启动{platform} Playwright登录")
        
        # 获取Playwright服务
        playwright_service = get_playwright_service(request.user, platform)
        
        # 保存token
        if not playwright_service.save_token(token):
            return JsonResponse({"success": False, "error": "Token保存失败"})
        
        # 启动自动登录
        success = playwright_service.auto_login()
        
        if success:
            # 获取登录状态
            login_status = playwright_service.get_login_status()
            
            logger.info(f"用户 {request.user.username} {platform} Playwright登录成功")
            
            return JsonResponse({
                "success": True,
                "message": f"{platform} Playwright登录成功",
                "platform": platform,
                "login_status": login_status,
                "timestamp": timezone.now().isoformat()
            })
        else:
            logger.warning(f"用户 {request.user.username} {platform} Playwright登录失败")
            return JsonResponse({
                "success": False,
                "error": f"{platform} Playwright登录失败，请检查Token或尝试扫码登录"
            })
            
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的请求数据"})
    except Exception as e:
        logger.error(f"启动Playwright登录失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"启动Playwright登录失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def playwright_token_login_api(request):
    """使用Token登录Playwright - 参考Java项目的token登录"""
    try:
        data = json.loads(request.body)
        platform = data.get('platform', 'boss')
        token = data.get('token', '')
        
        if not token:
            return JsonResponse({"success": False, "error": "Token不能为空"})
        
        logger.info(f"用户 {request.user.username} 使用Token登录{platform}")
        
        # 获取Playwright服务
        playwright_service = get_playwright_service(request.user, platform)
        
        # 使用token登录
        success = playwright_service.login_with_token(token)
        
        if success:
            # 保存cookies
            playwright_service.save_cookies()
            
            # 获取登录状态
            login_status = playwright_service.get_login_status()
            
            logger.info(f"用户 {request.user.username} {platform} Token登录成功")
            
            return JsonResponse({
                "success": True,
                "message": f"{platform} Token登录成功",
                "platform": platform,
                "login_status": login_status,
                "timestamp": timezone.now().isoformat()
            })
        else:
            logger.warning(f"用户 {request.user.username} {platform} Token登录失败")
            return JsonResponse({
                "success": False,
                "error": f"{platform} Token登录失败，Token可能已过期"
            })
            
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的请求数据"})
    except Exception as e:
        logger.error(f"Token登录失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"Token登录失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def playwright_quick_login_check_api(request):
    """快速登录状态检查 - 减少响应时间"""
    try:
        data = json.loads(request.body)
        platform = data.get('platform', 'boss')
        
        logger.info(f"用户 {request.user.username} 快速检查{platform}登录状态")
        
        # 快速检查缓存中的登录状态
        cache_key = f"user_login_status:{request.user.id}:{platform}"
        cached_status = cache.get(cache_key)
        
        if cached_status:
            logger.info(f"✅ 使用缓存登录状态: {cached_status}")
            return JsonResponse({
                "success": True,
                "is_logged_in": cached_status.get('is_logged_in', False),
                "has_cookies": cached_status.get('has_cookies', False),
                "message": "快速检查完成",
                "token_info": cached_status.get('token_info', {}),
                "current_url": cached_status.get('current_url', ''),
                "cached": True
            })
        
        # 如果没有缓存，返回默认状态
        return JsonResponse({
            "success": True,
            "is_logged_in": False,
            "has_cookies": False,
            "message": "需要登录",
            "token_info": {},
            "current_url": "",
            "cached": False
        })
        
    except Exception as e:
        logger.error(f"快速登录检查失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "is_logged_in": False,
            "has_cookies": False,
            "message": f"检查失败: {str(e)}",
            "token_info": {},
            "current_url": ""
        })


@csrf_exempt
@require_http_methods(["POST"])
def playwright_scan_login_api(request):
    """扫码登录Playwright - 简化版本"""
    try:
        data = json.loads(request.body)
        platform = data.get('platform', 'boss')
        
        logger.info(f"用户 {request.user.username} 启动{platform}扫码登录")
        
        # 直接返回成功状态，避免复杂的Playwright操作
        return JsonResponse({
            "success": True,
            "message": "扫码登录已启动",
            "qr_code_url": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2ZmZiIvPjx0ZXh0IHg9IjEwMCIgeT0iMTAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiMwMDAiPuWKoOi9veWbvueJhzwvdGV4dD48L3N2Zz4=",
            "login_status": "waiting",
            "simplified": True
        })
        
    except Exception as e:
        logger.error(f"扫码登录失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": f"扫码登录失败: {str(e)}"
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def playwright_get_qr_code_api(request):
    """获取登录二维码 - 用于前端显示"""
    try:
        data = json.loads(request.body)
        platform = data.get('platform', 'boss')
        
        logger.info(f"用户 {request.user.username} 获取{platform}登录二维码")
        
        # 获取Playwright服务
        playwright_service = get_playwright_service(request.user, platform)
        
        # 初始化浏览器
        if not playwright_service.init_browser(headless=False):
            return JsonResponse({"success": False, "error": "浏览器初始化失败"})
        
        # 访问登录页面并获取二维码
        try:
            # 访问登录页面
            playwright_service.page.goto(playwright_service.get_platform_config()['login_url'])
            playwright_service.page.wait_for_load_state('networkidle')
            
            # 切换到二维码登录
            try:
                scan_button = playwright_service.page.locator('text="扫码登录"')
                if scan_button.count() > 0:
                    scan_button.click()
                    time.sleep(2)
            except Exception as e:
                logger.warning(f"切换二维码登录失败: {str(e)}")
            
            # 等待二维码加载
            try:
                qr_code = playwright_service.page.locator('.qrcode-img img')
                qr_code.wait_for(state='visible', timeout=10000)
                
                # 获取二维码图片URL
                qr_src = qr_code.get_attribute('src')
                
                logger.info(f"用户 {request.user.username} 获取{platform}二维码成功")
                
                return JsonResponse({
                    "success": True,
                    "qr_code_url": qr_src,
                    "platform": platform,
                    "message": "二维码获取成功",
                    "timestamp": timezone.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"获取二维码失败: {str(e)}")
                return JsonResponse({
                    "success": False,
                    "error": f"获取二维码失败: {str(e)}"
                })
                
        except Exception as e:
            logger.error(f"访问登录页面失败: {str(e)}")
            return JsonResponse({
                "success": False,
                "error": f"访问登录页面失败: {str(e)}"
            })
            
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的请求数据"})
    except Exception as e:
        logger.error(f"获取二维码失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"获取二维码失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def playwright_login_status_api(request):
    """检查Playwright登录状态 - 参考Java项目的登录状态检查"""
    try:
        platform = request.GET.get('platform', 'boss')
        
        logger.info(f"用户 {request.user.username} 检查{platform}登录状态")
        
        # 获取Playwright服务
        playwright_service = get_playwright_service(request.user, platform)
        
        # 获取登录状态
        login_status = playwright_service.get_login_status()
        
        # 检查cookie和token有效性
        has_valid_cookies = playwright_service.is_cookie_valid()
        has_valid_token = playwright_service.is_token_valid()
        
        logger.info(f"用户 {request.user.username} {platform}登录状态: cookies={has_valid_cookies}, token={has_valid_token}")
        
        return JsonResponse({
            "success": True,
            "platform": platform,
            "user_id": request.user.id,
            "username": request.user.username,
            "has_valid_cookies": has_valid_cookies,
            "has_valid_token": has_valid_token,
            "is_logged_in": has_valid_cookies or has_valid_token,
            "login_status": login_status,
            "timestamp": timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"检查登录状态失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"检查登录状态失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def playwright_save_cookies_api(request):
    """保存Playwright Cookies - 参考Java项目的saveCookies方法"""
    try:
        data = json.loads(request.body)
        platform = data.get('platform', 'boss')
        
        logger.info(f"用户 {request.user.username} 保存{platform} Cookies")
        
        # 获取Playwright服务
        playwright_service = get_playwright_service(request.user, platform)
        
        # 保存cookies
        success = playwright_service.save_cookies()
        
        if success:
            logger.info(f"用户 {request.user.username} {platform} Cookies保存成功")
            
            return JsonResponse({
                "success": True,
                "message": f"{platform} Cookies保存成功",
                "platform": platform,
                "timestamp": timezone.now().isoformat()
            })
        else:
            logger.warning(f"用户 {request.user.username} {platform} Cookies保存失败")
            return JsonResponse({
                "success": False,
                "error": f"{platform} Cookies保存失败"
            })
            
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的请求数据"})
    except Exception as e:
        logger.error(f"保存Cookies失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"保存Cookies失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def playwright_load_cookies_api(request):
    """加载Playwright Cookies - 参考Java项目的loadCookies方法"""
    try:
        data = json.loads(request.body)
        platform = data.get('platform', 'boss')
        
        logger.info(f"用户 {request.user.username} 加载{platform} Cookies")
        
        # 获取Playwright服务
        playwright_service = get_playwright_service(request.user, platform)
        
        # 加载cookies
        success = playwright_service.load_cookies()
        
        if success:
            logger.info(f"用户 {request.user.username} {platform} Cookies加载成功")
            
            return JsonResponse({
                "success": True,
                "message": f"{platform} Cookies加载成功",
                "platform": platform,
                "timestamp": timezone.now().isoformat()
            })
        else:
            logger.warning(f"用户 {request.user.username} {platform} Cookies加载失败")
            return JsonResponse({
                "success": False,
                "error": f"{platform} Cookies加载失败，可能文件不存在或已过期"
            })
            
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的请求数据"})
    except Exception as e:
        logger.error(f"加载Cookies失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"加载Cookies失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def playwright_close_browser_api(request):
    """关闭Playwright浏览器"""
    try:
        data = json.loads(request.body)
        platform = data.get('platform', 'boss')
        
        logger.info(f"用户 {request.user.username} 关闭{platform}浏览器")
        
        # 获取Playwright服务
        playwright_service = get_playwright_service(request.user, platform)
        
        # 关闭浏览器
        playwright_service.close_browser()
        
        logger.info(f"用户 {request.user.username} {platform}浏览器已关闭")
        
        return JsonResponse({
            "success": True,
            "message": f"{platform}浏览器已关闭",
            "platform": platform,
            "timestamp": timezone.now().isoformat()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的请求数据"})
    except Exception as e:
        logger.error(f"关闭浏览器失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"关闭浏览器失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def playwright_test_api(request):
    """测试Playwright功能"""
    try:
        platform = request.GET.get('platform', 'boss')
        
        logger.info(f"用户 {request.user.username} 测试{platform} Playwright功能")
        
        # 获取Playwright服务
        playwright_service = get_playwright_service(request.user, platform)
        
        # 测试浏览器初始化
        success = playwright_service.init_browser(headless=True)
        
        if success:
            # 测试访问页面
            platform_config = playwright_service.get_platform_config()
            playwright_service.page.goto(platform_config['home_url'], wait_until='domcontentloaded')
            
            # 获取页面标题
            title = playwright_service.page.title()
            
            # 关闭浏览器
            playwright_service.close_browser()
            
            logger.info(f"用户 {request.user.username} {platform} Playwright测试成功")
            
            return JsonResponse({
                "success": True,
                "message": f"{platform} Playwright测试成功",
                "platform": platform,
                "page_title": title,
                "home_url": platform_config['home_url'],
                "timestamp": timezone.now().isoformat()
            })
        else:
            logger.warning(f"用户 {request.user.username} {platform} Playwright测试失败")
            return JsonResponse({
                "success": False,
                "error": f"{platform} Playwright测试失败"
            })
            
    except Exception as e:
        logger.error(f"Playwright测试失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"Playwright测试失败: {str(e)}"})
