"""
Java Boss二维码API
获取Java程序生成的真实二维码
"""
import logging
import os
import json
import time
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.contrib.auth.decorators import login_required
from apps.tools.services.java_boss_interface_service import java_boss_service

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_java_boss_qr_code_api(request):
    """获取Java程序生成的Boss直聘二维码"""
    try:
        task_id = request.GET.get('task_id')
        
        if not task_id:
            return JsonResponse({
                'success': False,
                'error': '缺少task_id参数'
            }, status=400)
        
        # 获取任务状态
        status_result = java_boss_service.get_task_status(task_id)
        
        if not status_result['success']:
            return JsonResponse({
                'success': False,
                'error': status_result['error']
            }, status=404)
        
        task_status = status_result['status']
        
        # 检查Java进程是否还在运行
        java_process_id = task_status.get('java_process_id')
        if java_process_id:
            try:
                os.kill(java_process_id, 0)  # 检查进程是否存在
            except OSError:
                return JsonResponse({
                    'success': False,
                    'error': 'Java进程已停止'
                }, status=500)
        
        # 返回二维码信息
        return JsonResponse({
            'success': True,
            'qr_code_url': '/tools/java-job/api/qr-image/',
            'task_id': task_id,
            'status': task_status.get('status', 'unknown'),
            'message': '二维码获取成功'
        })
        
    except Exception as e:
        logger.error(f"获取Java Boss二维码失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': '获取二维码失败'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_login_status_api(request):
    """获取登录状态"""
    try:
        # 获取任务ID
        task_id = request.GET.get('task_id')
        if not task_id:
            return JsonResponse({'success': False, 'error': '缺少task_id参数'})
        
        # 构建登录状态文件路径
        login_status_path = os.path.join(settings.BASE_DIR, 'temp_java_jobs', f'qr_code_{task_id}_login_status.json')
        
        # 检查文件是否存在
        if os.path.exists(login_status_path):
            with open(login_status_path, 'r', encoding='utf-8') as f:
                login_status = json.load(f)
            
            return JsonResponse({
                'success': True,
                'login_status': login_status.get('login_status'),
                'message': login_status.get('message'),
                'login_time': login_status.get('login_time')
            })
        else:
            return JsonResponse({
                'success': True,
                'login_status': 'pending',
                'message': '等待扫码登录'
            })
            
    except Exception as e:
        logger.error(f"获取登录状态失败: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["GET"])
def get_java_boss_qr_image_api(request):
    """获取Java程序生成的Boss直聘二维码图片"""
    try:
        task_id = request.GET.get('task_id')
        
        if not task_id:
            return HttpResponse("缺少task_id参数", status=400)
        
        # 查找真实的二维码图片文件
        qr_image_path = os.path.join(settings.BASE_DIR, 'temp_java_jobs', f'qr_code_{task_id}.png')
        
        if os.path.exists(qr_image_path):
            # 返回真实的二维码图片
            with open(qr_image_path, 'rb') as f:
                image_data = f.read()
            return HttpResponse(image_data, content_type='image/png')
        else:
            # 如果还没有生成二维码图片，返回等待状态的SVG
            svg_waiting = f'''<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">
                <rect width="400" height="400" fill="white" stroke="#00ff41" stroke-width="3"/>
                <circle cx="200" cy="200" r="50" fill="none" stroke="#00ff41" stroke-width="3">
                    <animate attributeName="stroke-dasharray" values="0,314;157,157;0,314" dur="2s" repeatCount="indefinite"/>
                </circle>
                <text x="200" y="280" text-anchor="middle" font-family="Arial" font-size="16" fill="#00ff41" font-weight="bold">
                    正在生成二维码...
                </text>
                <text x="200" y="310" text-anchor="middle" font-family="Arial" font-size="12" fill="#666">
                    请稍候...
                </text>
                <text x="200" y="340" text-anchor="middle" font-family="Arial" font-size="10" fill="#999">
                    任务ID: {task_id[:8]}...
                </text>
            </svg>'''
            return HttpResponse(svg_waiting, content_type='image/svg+xml')
        
    except Exception as e:
        logger.error(f"获取Java Boss二维码图片失败: {str(e)}")
        # 返回简单的错误SVG而不是500错误
        error_svg = f'''<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">
            <rect width="400" height="400" fill="white" stroke="red" stroke-width="3"/>
            <text x="200" y="200" text-anchor="middle" font-family="Arial" font-size="16" fill="red">
                二维码生成失败
            </text>
            <text x="200" y="230" text-anchor="middle" font-family="Arial" font-size="12" fill="#666">
                错误: {str(e)[:50]}...
            </text>
        </svg>'''
        return HttpResponse(error_svg, content_type='image/svg+xml')
