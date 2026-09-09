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
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.contrib.auth.decorators import login_required
from apps.tools.services.java_boss_interface_service import java_boss_service, JavaBossInterfaceService

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


@csrf_exempt
@require_http_methods(["POST"])
def refresh_java_boss_qr_api(request):
    """刷新Java程序生成的Boss直聘二维码"""
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')

        if not task_id:
            return JsonResponse({'success': False, 'error': '缺少task_id参数'})

        # 检查任务是否存在
        status_file = os.path.join(settings.BASE_DIR, 'temp_java_jobs', f'status_{task_id}.json')
        if not os.path.exists(status_file):
            return JsonResponse({'success': False, 'error': '任务不存在'})

        # 读取任务状态
        with open(status_file, 'r', encoding='utf-8') as f:
            status_data = json.load(f)

        # 检查任务状态
        if status_data.get('status') == 'completed':
            return JsonResponse({'success': False, 'error': '任务已完成，无法刷新二维码'})

        # 停止现有的Java进程（如果还在运行）
        java_interface = JavaBossInterfaceService()
        java_interface.stop_task(task_id)

        # 清理旧的二维码文件
        qr_url_file = os.path.join(settings.BASE_DIR, 'temp_java_jobs', f'qr_url_{task_id}.txt')
        qr_image_file = os.path.join(settings.BASE_DIR, 'temp_java_jobs', f'qr_code_{task_id}.png')

        for file_path in [qr_url_file, qr_image_file]:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.warning(f"删除文件失败 {file_path}: {str(e)}")

        # 重新启动Java程序生成新的二维码
        # 使用现有的配置重新启动任务
        result = java_interface.start_boss_job_delivery(
            status_data.get('config', {}),
            status_data.get('verification_code', ''),
            client_ip='127.0.0.1'
        )

        if result['success']:
            return JsonResponse({
                'success': True,
                'message': '二维码已刷新',
                'qr_code_url': '/tools/java-job/api/java-qr-image/'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f"刷新二维码失败: {result.get('error', '未知错误')}"
            })

    except Exception as e:
        logger.error(f"刷新Java Boss二维码失败: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def start_delivery_task_api(request):
    """启动投递任务（在登录成功后）"""
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')

        if not task_id:
            return JsonResponse({'success': False, 'error': '缺少task_id参数'})

        # 启动投递任务
        java_interface = JavaBossInterfaceService()
        result = java_interface.start_delivery_task(task_id, client_ip='127.0.0.1')

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"启动投递任务失败: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["GET"])
def get_java_boss_qr_image_api(request):
    """获取Java程序生成的Boss直聘二维码图片"""
    try:
        task_id = request.GET.get('task_id')

        if not task_id:
            return HttpResponse("缺少task_id参数", status=400)

        # 首先检查是否有二维码URL文件
        qr_url_file = os.path.join(settings.BASE_DIR, 'temp_java_jobs', f'qr_url_{task_id}.txt')

        if os.path.exists(qr_url_file):
            # 读取二维码URL
            with open(qr_url_file, 'r', encoding='utf-8') as f:
                qr_url = f.read().strip()

            if qr_url:
                # 如果是相对URL，转换为完整URL
                if qr_url.startswith('/'):
                    full_qr_url = f"https://login.zhipin.com{qr_url}"
                else:
                    full_qr_url = qr_url

                # 返回包含二维码的HTML页面
                html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Boss直聘登录二维码</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: #0a0a0a;
            color: #00ff41;
            font-family: 'JetBrains Mono', monospace;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }}
        .qr-container {{
            text-align: center;
            padding: 20px;
            border: 2px solid #00ff41;
            border-radius: 12px;
            background: #1a1a1a;
        }}
        .qr-image {{
            max-width: 300px;
            width: 100%;
            height: auto;
            border-radius: 8px;
        }}
        .status-text {{
            margin-top: 15px;
            font-size: 14px;
            color: #00ff41;
        }}
        .task-id {{
            margin-top: 10px;
            font-size: 12px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="qr-container">
        <h3>📱 Boss直聘登录二维码</h3>
        <img src="{full_qr_url}" alt="Boss直聘登录二维码" class="qr-image" />
        <div class="status-text">请使用Boss直聘APP扫描二维码登录</div>
        <div class="task-id">任务ID: {task_id[:8]}...</div>
    </div>
</body>
</html>'''
                return HttpResponse(html_content, content_type='text/html')

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
