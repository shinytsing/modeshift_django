"""
Token管理和跨标签页同步API视图
参考Java项目get_jobs的token管理机制
"""

import json
import logging
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.cache import cache

from ..services.cookie_manager_service import get_cookie_manager
from ..services.boss_zhipin_service import BossZhipinService

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def save_boss_token_api(request):
    """保存Boss直聘Token - 参考Java项目的token保存机制"""
    try:
        data = json.loads(request.body)
        token = data.get('token', '').strip()
        platform = data.get('platform', 'boss')
        
        if not token:
            return JsonResponse({"success": False, "error": "Token不能为空"})
        
        # 使用Cookie管理器保存token
        cookie_manager = get_cookie_manager(request.user, platform)
        success = cookie_manager.save_token(token, 'api_token')
        
        if success:
            # 同时保存到用户session中
            request.session[f'{platform}_token'] = token
            request.session[f'{platform}_login_time'] = timezone.now().isoformat()
            request.session.modified = True
            
            # 保存到缓存供其他标签页使用
            cache_key = f"user_tokens:{request.user.id}"
            user_tokens = cache.get(cache_key, {})
            user_tokens[platform] = {
                'token': token,
                'login_time': timezone.now().isoformat(),
                'platform': platform
            }
            cache.set(cache_key, user_tokens, 60 * 60 * 24 * 7)  # 7天
            
            logger.info(f"用户 {request.user.username} 保存{platform} Token成功")
            
            return JsonResponse({
                "success": True,
                "message": f"{platform} Token保存成功",
                "token_preview": token[:20] + "..." if len(token) > 20 else token,
                "platform": platform
            })
        else:
            return JsonResponse({"success": False, "error": f"{platform} Token保存失败"})
            
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的请求数据"})
    except Exception as e:
        logger.error(f"保存Token失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"保存Token失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_boss_token_api(request):
    """获取Boss直聘Token - 支持跨标签页同步"""
    try:
        platform = request.GET.get('platform', 'boss')
        
        # 从Cookie管理器获取token
        cookie_manager = get_cookie_manager(request.user, platform)
        token_data = cookie_manager.load_token()
        
        if token_data and token_data.get('is_valid'):
            return JsonResponse({
                "success": True,
                "has_token": True,
                "token_preview": token_data['token'][:20] + "..." if len(token_data['token']) > 20 else token_data['token'],
                "login_time": token_data.get('login_time'),
                "platform": platform,
                "is_valid": True
            })
        else:
            return JsonResponse({
                "success": True,
                "has_token": False,
                "platform": platform,
                "is_valid": False,
                "message": f"未找到有效的{platform} Token"
            })
            
    except Exception as e:
        logger.error(f"获取Token失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"获取Token失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def check_login_status_api(request):
    """检查登录状态 - 跨标签页同步增强版"""
    try:
        platform = request.GET.get('platform', 'boss')
        include_token_details = request.GET.get('include_details', 'false').lower() == 'true'
        
        # 检查session中的登录状态
        session_token = request.session.get(f'{platform}_token')
        session_login_time = request.session.get(f'{platform}_login_time')
        
        # 检查Cookie管理器中的token
        cookie_manager = get_cookie_manager(request.user, platform)
        token_data = cookie_manager.load_token()
        
        # 检查缓存中的token
        cache_key = f"user_tokens:{request.user.id}"
        cached_tokens = cache.get(cache_key, {})
        cached_token = cached_tokens.get(platform)
        
        # 检查跨标签页同步缓存
        cross_tab_key = f"cross_tab_tokens:{request.user.id}"
        cross_tab_data = cache.get(cross_tab_key, {})
        cross_tab_token = cross_tab_data.get('tokens', {}).get(platform) if cross_tab_data else None
        
        # 综合判断登录状态
        has_session_token = bool(session_token)
        has_cookie_token = token_data and token_data.get('is_valid')
        has_cached_token = bool(cached_token)
        has_cross_tab_token = bool(cross_tab_token)
        
        # 确定最新的token信息
        latest_token_info = None
        latest_login_time = None
        
        # 按优先级选择最新的token信息
        if has_cross_tab_token and cross_tab_token.get('login_time'):
            latest_token_info = cross_tab_token
            latest_login_time = cross_tab_token.get('login_time')
        elif has_cached_token and cached_token.get('login_time'):
            latest_token_info = cached_token
            latest_login_time = cached_token.get('login_time')
        elif has_cookie_token and token_data.get('login_time'):
            latest_token_info = token_data
            latest_login_time = token_data.get('login_time')
        elif has_session_token and session_login_time:
            latest_login_time = session_login_time
        
        # 构建响应数据
        login_status = {
            "success": True,
            "platform": platform,
            "user_id": request.user.id,
            "username": request.user.username,
            "has_session_token": has_session_token,
            "has_cookie_token": has_cookie_token,
            "has_cached_token": has_cached_token,
            "has_cross_tab_token": has_cross_tab_token,
            "is_logged_in": has_session_token or has_cookie_token or has_cached_token or has_cross_tab_token,
            "session_login_time": session_login_time,
            "cookie_login_time": token_data.get('login_time') if token_data else None,
            "cached_login_time": cached_token.get('login_time') if cached_token else None,
            "cross_tab_login_time": cross_tab_token.get('login_time') if cross_tab_token else None,
            "latest_login_time": latest_login_time,
            "timestamp": timezone.now().isoformat(),
            "sync_source": "enhanced_api_v2"
        }
        
        # 如果请求包含详细信息
        if include_token_details and latest_token_info:
            login_status["token_details"] = {
                "platform": latest_token_info.get('platform', platform),
                "login_method": latest_token_info.get('login_method', 'unknown'),
                "expires_at": latest_token_info.get('expires_at'),
                "is_valid": latest_token_info.get('is_valid', True),
                "source": "cross_tab" if has_cross_tab_token else "cache" if has_cached_token else "cookie"
            }
        
        # 更新跨标签页同步缓存
        if login_status["is_logged_in"] and latest_token_info:
            sync_data = {
                'tokens': {
                    platform: {
                        'token': latest_token_info.get('token', ''),
                        'login_time': latest_login_time,
                        'user_id': request.user.id,
                        'platform': platform,
                        'sync_time': timezone.now().isoformat()
                    }
                },
                'last_sync': timezone.now().isoformat(),
                'user_id': request.user.id
            }
            cache.set(cross_tab_key, sync_data, 60 * 60 * 24 * 7)  # 7天
        
        return JsonResponse(login_status)
        
    except Exception as e:
        logger.error(f"检查登录状态失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"检查登录状态失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def sync_session_api(request):
    """同步Session - 跨标签页同步"""
    try:
        data = json.loads(request.body)
        platform = data.get('platform', 'boss')
        token = data.get('token', '')
        
        if token:
            # 保存token到session
            request.session[f'{platform}_token'] = token
            request.session[f'{platform}_login_time'] = timezone.now().isoformat()
            request.session.modified = True
            
            # 保存到Cookie管理器
            cookie_manager = get_cookie_manager(request.user, platform)
            cookie_manager.save_token(token, 'sync_token')
            
            # 保存到缓存
            cache_key = f"user_tokens:{request.user.id}"
            user_tokens = cache.get(cache_key, {})
            user_tokens[platform] = {
                'token': token,
                'login_time': timezone.now().isoformat(),
                'platform': platform
            }
            cache.set(cache_key, user_tokens, 60 * 60 * 24 * 7)  # 7天
            
            logger.info(f"用户 {request.user.username} 同步{platform} session成功")
            
            return JsonResponse({
                "success": True,
                "message": f"{platform} Session同步成功",
                "platform": platform
            })
        else:
            return JsonResponse({"success": False, "error": "Token不能为空"})
            
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的请求数据"})
    except Exception as e:
        logger.error(f"同步Session失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"同步Session失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_all_tokens_api(request):
    """获取所有平台的Token状态"""
    try:
        platforms = ['boss', 'lagou', 'liepin', 'zhipin', '51job']
        tokens_status = {}
        
        for platform in platforms:
            cookie_manager = get_cookie_manager(request.user, platform)
            token_data = cookie_manager.load_token()
            
            tokens_status[platform] = {
                'has_token': token_data and token_data.get('is_valid'),
                'login_time': token_data.get('login_time') if token_data else None,
                'is_valid': token_data.get('is_valid', False) if token_data else False
            }
        
        return JsonResponse({
            "success": True,
            "tokens": tokens_status,
            "user_id": request.user.id,
            "username": request.user.username,
            "timestamp": timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"获取所有Token状态失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"获取所有Token状态失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def clear_token_api(request):
    """清除指定平台的Token"""
    try:
        data = json.loads(request.body)
        platform = data.get('platform', 'boss')
        
        # 从Cookie管理器清除
        cookie_manager = get_cookie_manager(request.user, platform)
        cookie_manager.clear_token()
        
        # 从session清除
        if f'{platform}_token' in request.session:
            del request.session[f'{platform}_token']
        if f'{platform}_login_time' in request.session:
            del request.session[f'{platform}_login_time']
        request.session.modified = True
        
        # 从缓存清除
        cache_key = f"user_tokens:{request.user.id}"
        user_tokens = cache.get(cache_key, {})
        if platform in user_tokens:
            del user_tokens[platform]
            cache.set(cache_key, user_tokens, 60 * 60 * 24 * 7)
        
        logger.info(f"用户 {request.user.username} 清除{platform} Token成功")
        
        return JsonResponse({
            "success": True,
            "message": f"{platform} Token已清除",
            "platform": platform
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的请求数据"})
    except Exception as e:
        logger.error(f"清除Token失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"清除Token失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def cross_tab_sync_api(request):
    """跨标签页Token同步API - 专门处理标签页间的token同步"""
    try:
        data = json.loads(request.body)
        platform = data.get('platform', 'boss')
        action = data.get('action', 'sync')  # sync, update, clear
        token_data = data.get('token_data', {})
        
        cross_tab_key = f"cross_tab_tokens:{request.user.id}"
        
        if action == 'sync':
            # 获取最新的跨标签页token数据
            cross_tab_data = cache.get(cross_tab_key, {})
            
            return JsonResponse({
                "success": True,
                "action": "sync",
                "platform": platform,
                "cross_tab_data": cross_tab_data,
                "timestamp": timezone.now().isoformat()
            })
            
        elif action == 'update':
            # 更新跨标签页token数据
            if not token_data:
                return JsonResponse({"success": False, "error": "缺少token数据"})
            
            # 获取现有数据
            existing_data = cache.get(cross_tab_key, {})
            if 'tokens' not in existing_data:
                existing_data['tokens'] = {}
            
            # 更新指定平台的token
            existing_data['tokens'][platform] = {
                'token': token_data.get('token', ''),
                'login_time': token_data.get('login_time', timezone.now().isoformat()),
                'user_id': request.user.id,
                'platform': platform,
                'sync_time': timezone.now().isoformat(),
                'source': token_data.get('source', 'cross_tab_update')
            }
            existing_data['last_sync'] = timezone.now().isoformat()
            existing_data['user_id'] = request.user.id
            
            # 保存到缓存
            cache.set(cross_tab_key, existing_data, 60 * 60 * 24 * 7)  # 7天
            
            logger.info(f"跨标签页Token已更新: {platform} (用户: {request.user.username})")
            
            return JsonResponse({
                "success": True,
                "action": "update",
                "platform": platform,
                "message": f"{platform} Token已同步到其他标签页",
                "timestamp": timezone.now().isoformat()
            })
            
        elif action == 'clear':
            # 清除跨标签页token数据
            existing_data = cache.get(cross_tab_key, {})
            if 'tokens' in existing_data and platform in existing_data['tokens']:
                del existing_data['tokens'][platform]
                existing_data['last_sync'] = timezone.now().isoformat()
                cache.set(cross_tab_key, existing_data, 60 * 60 * 24 * 7)
            
            logger.info(f"跨标签页Token已清除: {platform} (用户: {request.user.username})")
            
            return JsonResponse({
                "success": True,
                "action": "clear",
                "platform": platform,
                "message": f"{platform} Token已从跨标签页同步中清除",
                "timestamp": timezone.now().isoformat()
            })
            
        else:
            return JsonResponse({"success": False, "error": f"不支持的操作: {action}"})
            
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的请求数据"})
    except Exception as e:
        logger.error(f"跨标签页同步失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"跨标签页同步失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def test_boss_login_api(request):
    """测试Boss直聘登录状态"""
    try:
        platform = request.GET.get('platform', 'boss')
        
        # 获取token
        cookie_manager = get_cookie_manager(request.user, platform)
        token_data = cookie_manager.load_token()
        
        if not token_data or not token_data.get('is_valid'):
            return JsonResponse({
                "success": False,
                "error": f"未找到有效的{platform} Token",
                "platform": platform
            })
        
        # 使用BossZhipinService测试登录
        boss_service = BossZhipinService()
        test_result = boss_service.test_login_with_token(token_data['token'])
        
        return JsonResponse({
            "success": True,
            "test_result": test_result,
            "platform": platform,
            "token_valid": token_data.get('is_valid', False)
        })
        
    except Exception as e:
        logger.error(f"测试{platform}登录失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"测试登录失败: {str(e)}"})
