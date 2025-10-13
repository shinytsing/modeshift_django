"""
Boss直聘二维码API
"""
import logging
import requests
import json
import time
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_boss_qr_code_api(request):
    """获取Boss直聘登录二维码"""
    try:
        # 模拟获取Boss直聘二维码的过程
        # 实际实现中，这里应该调用Boss直聘的API获取真实的二维码
        
        # 生成一个模拟的二维码数据
        qr_data = {
            'qr_id': f'boss_qr_{int(time.time())}',
            'qr_url': 'https://login.zhipin.com/web/user/security/login',
            'expire_time': int(time.time()) + 300,  # 5分钟过期
            'status': 'waiting'
        }
        
        # 这里应该返回真实的二维码图片
        # 暂时返回一个包含二维码信息的JSON
        return JsonResponse({
            'success': True,
            'qr_data': qr_data,
            'qr_image_url': '/tools/java-job/api/qr-image/',  # 二维码图片URL
            'message': '二维码获取成功'
        })
        
    except Exception as e:
        logger.error(f"获取Boss二维码失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': '获取二维码失败'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_boss_qr_image_api(request):
    """获取Boss直聘二维码图片"""
    try:
        # 这里应该返回真实的二维码图片
        # 暂时返回一个SVG格式的二维码占位符
        
        svg_qr = f'''
        <svg width="300" height="300" xmlns="http://www.w3.org/2000/svg">
            <rect width="300" height="300" fill="white" stroke="black" stroke-width="2"/>
            <text x="150" y="150" text-anchor="middle" font-family="Arial" font-size="14" fill="black">
                Boss直聘登录二维码
            </text>
            <text x="150" y="170" text-anchor="middle" font-family="Arial" font-size="12" fill="gray">
                请使用Boss直聘APP扫码
            </text>
            <text x="150" y="190" text-anchor="middle" font-family="Arial" font-size="10" fill="gray">
                二维码ID: boss_qr_{int(time.time())}
            </text>
        </svg>
        '''
        
        return HttpResponse(svg_qr, content_type='image/svg+xml')
        
    except Exception as e:
        logger.error(f"生成二维码图片失败: {str(e)}")
        return HttpResponse("二维码生成失败", status=500)
