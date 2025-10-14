"""
Java Job项目集成API视图
"""
import json
import logging
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.cache import cache
from apps.tools.services.java_job_integration_service import java_job_service

logger = logging.getLogger(__name__)


def clear_boss_token_before_java_task(user):
    """在启动Java任务前清理Boss直聘token"""
    try:
        logger.info(f"开始清理用户 {user.username} 的Boss直聘token...")
        
        # 清理token文件
        token_file = os.path.join(settings.BASE_DIR, 'get_jobs_integration', f'boss_token_{user.id}.json')
        cookie_file = os.path.join(settings.BASE_DIR, 'get_jobs_integration', f'boss_cookies_{user.id}.json')
        
        cleared_files = []
        
        # 删除token文件
        if os.path.exists(token_file):
            os.remove(token_file)
            cleared_files.append('token文件')
            logger.info(f"已删除token文件: {token_file}")
        
        # 删除cookie文件
        if os.path.exists(cookie_file):
            os.remove(cookie_file)
            cleared_files.append('cookie文件')
            logger.info(f"已删除cookie文件: {cookie_file}")
        
        # 清理Java项目中的cookie文件
        java_cookie_paths = [
            os.path.join(settings.BASE_DIR, 'java_job', 'cookies', f'boss_cookies_{user.id}.json'),
            os.path.join(settings.BASE_DIR, 'java_job', 'java_job', 'cookies', f'boss_cookies_{user.id}.json'),
            os.path.join(settings.BASE_DIR, 'temp_java_jobs', f'boss_cookies_{user.id}.json'),
        ]
        
        for java_cookie_path in java_cookie_paths:
            if os.path.exists(java_cookie_path):
                os.remove(java_cookie_path)
                cleared_files.append(f'Java cookie文件: {os.path.basename(java_cookie_path)}')
                logger.info(f"已删除Java cookie文件: {java_cookie_path}")
        
        # 清除缓存
        cache_keys_to_clear = [
            f"boss_token_{user.id}",
            f"boss_cookies_{user.id}",
            f"boss_login_status_{user.id}",
            f"user_tokens:{user.id}"
        ]
        
        for cache_key in cache_keys_to_clear:
            cache.delete(cache_key)
        
        logger.info(f"用户 {user.username} 的Boss直聘token清理完成，清理文件: {cleared_files}")
        return True
        
    except Exception as e:
        logger.error(f"清理用户 {user.username} 的Boss直聘token失败: {str(e)}")
        return False


def get_client_ip(request):
    """获取客户端真实IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def start_java_job_delivery_api(request):
    """启动Java版本的Boss直聘投递API"""
    try:
        data = json.loads(request.body)
        
        # 获取客户端IP地址
        client_ip = get_client_ip(request)
        
        # 验证必需字段
        required_fields = ['greeting', 'city', 'position', 'experience', 'expectedSalary', 'education', 'verification_code']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'success': False,
                    'error': f'缺少必需字段: {field}'
                }, status=400)
        
        # 🔥 每次启动Java任务前自动清理token，确保使用最新登录状态
        logger.info(f"用户 {request.user.username} 启动Java任务，先清理历史token...")
        clear_boss_token_before_java_task(request.user)
        
        # 启动任务（包含验证码验证和IP绑定）
        result = java_job_service.start_boss_job_delivery(data, data['verification_code'], client_ip)
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'task_id': result['task_id'],
                'qr_code_url': result['qr_code_url'],
                'message': '验证码验证成功，历史token已清理，任务已启动'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['error']
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"启动Java投递任务失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': '服务器内部错误'
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_java_job_status_api(request):
    """获取Java投递任务状态"""
    try:
        task_id = request.GET.get('task_id')
        
        if not task_id:
            return JsonResponse({
                'success': False,
                'error': '缺少task_id参数'
            }, status=400)
        
        result = java_job_service.get_task_status(task_id)
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'status': result['status']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['error']
            }, status=404)
            
    except Exception as e:
        logger.error(f"获取任务状态失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': '服务器内部错误'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def stop_java_job_api(request):
    """停止Java投递任务"""
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        
        if not task_id:
            return JsonResponse({
                'success': False,
                'error': '缺少task_id参数'
            }, status=400)
        
        success = java_job_service.stop_task(task_id)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': '任务已停止'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': '停止任务失败'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"停止任务失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': '服务器内部错误'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def cleanup_java_job_api(request):
    """清理Java投递任务"""
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        
        if not task_id:
            return JsonResponse({
                'success': False,
                'error': '缺少task_id参数'
            }, status=400)
        
        success = java_job_service.cleanup_task(task_id)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': '任务已清理'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': '清理任务失败'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"清理任务失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': '服务器内部错误'
        }, status=500)
