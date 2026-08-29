# 测试展示相关的视图函数

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import time
import os
from datetime import datetime

def testing_dashboard_view(request):
    """测试手法展示主页面"""
    return render(request, "testing_dashboard.html")

def testing_functional_view(request):
    """功能测试展示页面"""
    return render(request, "testing_functional.html")

def testing_api_view(request):
    """接口测试展示页面"""
    return render(request, "testing_api.html")

def testing_performance_view(request):
    """性能测试展示页面"""
    return render(request, "testing_performance.html")

def testing_security_view(request):
    """安全测试展示页面"""
    return render(request, "testing_security.html")

# API接口视图
@csrf_exempt
@require_http_methods(["POST"])
def run_tests_api(request):
    """启动测试执行API"""
    try:
        data = json.loads(request.body)
        test_types = data.get('test_types', [])
        
        # 模拟测试执行
        return JsonResponse({
            'status': 'started',
            'message': '测试已启动',
            'test_types': test_types,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_test_status_api(request):
    """获取测试状态API"""
    # 模拟测试状态
    return JsonResponse({
        'is_running': False,
        'progress': 100,
        'current_test': '测试完成',
        'status': 'completed',
        'timestamp': datetime.now().isoformat()
    })

@require_http_methods(["GET"])
def get_test_results_api(request):
    """获取测试结果API"""
    # 模拟测试结果
    return JsonResponse({
        'total': 20,
        'passed': 18,
        'failed': 2,
        'skipped': 0,
        'broken': 0,
        'success_rate': 90.0,
        'duration': 2.3,
        'categories': {
            'functional': {'passed': 5, 'failed': 0, 'total': 5},
            'api': {'passed': 8, 'failed': 1, 'total': 9},
            'performance': {'passed': 3, 'failed': 1, 'total': 4},
            'security': {'passed': 2, 'failed': 0, 'total': 2}
        },
        'timestamp': datetime.now().isoformat()
    })

@require_http_methods(["GET"])
def get_test_stats_api(request):
    """获取测试统计API"""
    # 模拟统计数据
    return JsonResponse({
        'total_runs': 15,
        'total_tests': 300,
        'passed_tests': 270,
        'failed_tests': 30,
        'success_rate': 90.0,
        'avg_duration': 2.1,
        'categories': {
            'functional': {'total': 50, 'passed': 48, 'failed': 2},
            'api': {'total': 80, 'passed': 72, 'failed': 8},
            'performance': {'total': 60, 'passed': 55, 'failed': 5},
            'security': {'total': 40, 'passed': 38, 'failed': 2},
            'ui': {'total': 70, 'passed': 57, 'failed': 13}
        },
        'last_updated': datetime.now().isoformat()
    })

@require_http_methods(["GET"])
def get_test_history_api(request):
    """获取测试历史API"""
    # 模拟历史数据
    history = []
    for i in range(10):
        history.append({
            'id': i + 1,
            'started_at': datetime.now().isoformat(),
            'completed_at': datetime.now().isoformat(),
            'duration': round(1.5 + i * 0.2, 1),
            'test_types': ['functional', 'api'],
            'total_tests': 20 + i * 2,
            'passed': 18 + i * 2,
            'failed': 2,
            'skipped': 0,
            'broken': 0,
            'success_rate': round(90 + i, 2)
        })
    
    return JsonResponse({
        'history': history,
        'pagination': {
            'page': 1,
            'page_size': 10,
            'total_count': 10,
            'total_pages': 1
        }
    })

@require_http_methods(["GET"])
def get_test_report_api(request):
    """获取测试报告API"""
    return JsonResponse({
        'report_url': '/reports/allure-report/index.html',
        'report_path': '/qa/artifacts/allure-report/index.html',
        'exists': True,
        'timestamp': datetime.now().isoformat()
    })

@csrf_exempt
@require_http_methods(["POST"])
def stop_tests_api(request):
    """停止测试API"""
    return JsonResponse({
        'status': 'stopped',
        'message': '测试已停止',
        'timestamp': datetime.now().isoformat()
    })

def allure_report_view(request, path=''):
    """提供Allure报告文件"""
    # 构建文件路径 - 使用当前工作目录
    import os
    # 使用当前工作目录作为项目根目录
    project_root = os.getcwd()
    base_path = os.path.join(project_root, 'tests', 'reports', 'allure-report')
    
    if not path:
        path = 'index.html'
    
    file_path = os.path.join(base_path, path)
    
    # 检查文件是否存在
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise Http404(f"Allure报告文件不存在: {file_path}")
    
    # 读取文件内容
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # 根据文件扩展名设置Content-Type
        if path.endswith('.html'):
            content_type = 'text/html; charset=utf-8'
        elif path.endswith('.css'):
            content_type = 'text/css'
        elif path.endswith('.js'):
            content_type = 'application/javascript'
        elif path.endswith('.ico'):
            content_type = 'image/x-icon'
        elif path.endswith('.json'):
            content_type = 'application/json'
        else:
            content_type = 'application/octet-stream'
        
        response = HttpResponse(content, content_type=content_type)
        
        # 设置缓存头
        response['Cache-Control'] = 'public, max-age=3600'
        
        return response
        
    except Exception as e:
        raise Http404(f"无法读取Allure报告文件: {str(e)}")
