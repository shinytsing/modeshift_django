"""
简化的Playwright Token测试视图
绕过有问题的依赖，提供核心功能
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import json
import time
import os
from pathlib import Path


def playwright_token_test_view(request):
    """Playwright Token测试页面"""
    return render(request, 'tools/playwright_token_test.html')


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def save_token_api(request):
    """保存Token API"""
    try:
        data = json.loads(request.body)
        platform = data.get('platform', 'boss')
        token = data.get('token', '')
        
        if not token:
            return JsonResponse({"success": False, "error": "Token不能为空"})
        
        # 创建token目录
        token_dir = Path('get_jobs_integration/cookies')
        token_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存token到文件
        token_file = token_dir / f'{platform}_token_{request.user.id}.json'
        token_data = {
            'token': token,
            'login_time': time.time(),
            'user_id': request.user.id,
            'username': request.user.username,
            'platform': platform,
            'expires_at': time.time() + (7 * 24 * 60 * 60),  # 7天后过期
            'is_valid': True
        }
        
        with open(token_file, 'w', encoding='utf-8') as f:
            json.dump(token_data, f, ensure_ascii=False, indent=2)
        
        return JsonResponse({
            "success": True,
            "message": f"{platform} Token保存成功",
            "platform": platform
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的请求数据"})
    except Exception as e:
        return JsonResponse({"success": False, "error": f"保存Token失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_token_api(request):
    """获取Token API"""
    try:
        platform = request.GET.get('platform', 'boss')
        
        # 读取token文件
        token_file = Path(f'get_jobs_integration/cookies/{platform}_token_{request.user.id}.json')
        
        if not token_file.exists():
            return JsonResponse({"success": False, "error": "Token文件不存在"})
        
        with open(token_file, 'r', encoding='utf-8') as f:
            token_data = json.load(f)
        
        # 检查是否过期
        expires_at = token_data.get('expires_at', 0)
        if time.time() > expires_at:
            return JsonResponse({"success": False, "error": "Token已过期"})
        
        return JsonResponse({
            "success": True,
            "token": token_data['token'],
            "platform": platform,
            "login_time": token_data.get('login_time'),
            "is_valid": token_data.get('is_valid', True)
        })
        
    except Exception as e:
        return JsonResponse({"success": False, "error": f"获取Token失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def check_login_status_api(request):
    """检查登录状态API"""
    try:
        platform = request.GET.get('platform', 'boss')
        
        # 检查token文件是否存在
        token_file = Path(f'get_jobs_integration/cookies/{platform}_token_{request.user.id}.json')
        
        has_token = False
        is_valid = False
        
        if token_file.exists():
            try:
                with open(token_file, 'r', encoding='utf-8') as f:
                    token_data = json.load(f)
                
                # 检查是否过期
                expires_at = token_data.get('expires_at', 0)
                if time.time() <= expires_at:
                    has_token = True
                    is_valid = token_data.get('is_valid', True)
            except Exception:
                pass
        
        return JsonResponse({
            "success": True,
            "platform": platform,
            "user_id": request.user.id,
            "username": request.user.username,
            "has_token": has_token,
            "is_valid": is_valid,
            "is_logged_in": has_token and is_valid,
            "timestamp": time.time()
        })
        
    except Exception as e:
        return JsonResponse({"success": False, "error": f"检查登录状态失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def clear_token_api(request):
    """清除Token API"""
    try:
        data = json.loads(request.body)
        platform = data.get('platform', 'boss')
        
        # 删除token文件
        token_file = Path(f'get_jobs_integration/cookies/{platform}_token_{request.user.id}.json')
        
        if token_file.exists():
            token_file.unlink()
        
        return JsonResponse({
            "success": True,
            "message": f"{platform} Token已清除",
            "platform": platform
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的请求数据"})
    except Exception as e:
        return JsonResponse({"success": False, "error": f"清除Token失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def test_playwright_api(request):
    """测试Playwright API"""
    try:
        data = json.loads(request.body)
        platform = data.get('platform', 'boss')
        
        # 这里可以添加实际的Playwright测试逻辑
        # 目前返回模拟结果
        
        return JsonResponse({
            "success": True,
            "message": f"{platform} Playwright测试完成（模拟）",
            "platform": platform,
            "test_result": "success",
            "timestamp": time.time()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的请求数据"})
    except Exception as e:
        return JsonResponse({"success": False, "error": f"Playwright测试失败: {str(e)}"})
