# API 视图 (api/views.py)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse, FileResponse
from django.conf import settings
from pathlib import Path
import json
import threading
from datetime import datetime
from core.tasks import test_executor
from core.models import TestRun, TestResult
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
def run_tests(request):
    """启动测试执行"""
    try:
        # 检查是否已有测试在运行
        if test_executor.is_running:
            return Response({
                'error': '测试正在运行中',
                'status': 'running'
            }, status=status.HTTP_409_CONFLICT)
        
        # 获取测试类型参数
        test_types = request.data.get('test_types', [])
        
        # 创建测试运行记录
        test_run = TestRun.objects.create(
            status='running',
            test_types=json.dumps(test_types),
            started_at=datetime.now()
        )
        
        # 在后台线程中执行测试
        if test_types:
            thread = threading.Thread(
                target=test_executor.run_specific_tests,
                args=(test_types,)
            )
        else:
            thread = threading.Thread(target=test_executor.run_all_tests)
        
        thread.daemon = True
        thread.start()
        
        return Response({
            'message': '测试已启动',
            'test_run_id': test_run.id,
            'status': 'started'
        }, status=status.HTTP_202_ACCEPTED)
        
    except Exception as e:
        logger.error(f"启动测试失败: {str(e)}")
        return Response({
            'error': f'启动测试失败: {str(e)}',
            'status': 'error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_test_status(request):
    """获取测试执行状态"""
    try:
        status_info = test_executor.get_status()
        
        # 添加测试运行记录信息
        latest_run = TestRun.objects.filter(status='running').first()
        if latest_run:
            status_info['test_run_id'] = latest_run.id
            status_info['started_at'] = latest_run.started_at.isoformat()
        
        return Response(status_info)
        
    except Exception as e:
        logger.error(f"获取测试状态失败: {str(e)}")
        return Response({
            'error': f'获取测试状态失败: {str(e)}',
            'status': 'error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_test_results(request):
    """获取测试结果"""
    try:
        # 获取最新的测试结果
        latest_run = TestRun.objects.filter(status='completed').order_by('-completed_at').first()
        
        if not latest_run:
            return Response({
                'message': '暂无测试结果',
                'results': {}
            })
        
        # 获取测试结果详情
        results = TestResult.objects.filter(test_run=latest_run)
        
        # 构建结果统计
        result_stats = {
            'test_run_id': latest_run.id,
            'total': results.count(),
            'passed': results.filter(status='passed').count(),
            'failed': results.filter(status='failed').count(),
            'skipped': results.filter(status='skipped').count(),
            'broken': results.filter(status='broken').count(),
            'duration': latest_run.duration,
            'completed_at': latest_run.completed_at.isoformat(),
            'categories': {
                'functional': {'passed': 0, 'failed': 0, 'total': 0},
                'api': {'passed': 0, 'failed': 0, 'total': 0},
                'performance': {'passed': 0, 'failed': 0, 'total': 0},
                'security': {'passed': 0, 'failed': 0, 'total': 0},
                'ui': {'passed': 0, 'failed': 0, 'total': 0}
            }
        }
        
        # 按类别统计
        for result in results:
            category = result.category
            if category in result_stats['categories']:
                result_stats['categories'][category]['total'] += 1
                if result.status == 'passed':
                    result_stats['categories'][category]['passed'] += 1
                else:
                    result_stats['categories'][category]['failed'] += 1
        
        return Response(result_stats)
        
    except Exception as e:
        logger.error(f"获取测试结果失败: {str(e)}")
        return Response({
            'error': f'获取测试结果失败: {str(e)}',
            'results': {}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_test_history(request):
    """获取测试历史记录"""
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        # 分页查询测试运行记录
        runs = TestRun.objects.filter(status='completed').order_by('-completed_at')
        
        total_count = runs.count()
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        runs_page = runs[start_index:end_index]
        
        history = []
        for run in runs_page:
            # 获取该次运行的测试结果统计
            results = TestResult.objects.filter(test_run=run)
            
            history_item = {
                'id': run.id,
                'started_at': run.started_at.isoformat(),
                'completed_at': run.completed_at.isoformat(),
                'duration': run.duration,
                'test_types': json.loads(run.test_types) if run.test_types else [],
                'total_tests': results.count(),
                'passed': results.filter(status='passed').count(),
                'failed': results.filter(status='failed').count(),
                'skipped': results.filter(status='skipped').count(),
                'broken': results.filter(status='broken').count(),
                'success_rate': round(
                    results.filter(status='passed').count() / results.count() * 100, 2
                ) if results.count() > 0 else 0
            }
            history.append(history_item)
        
        return Response({
            'history': history,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        })
        
    except Exception as e:
        logger.error(f"获取测试历史失败: {str(e)}")
        return Response({
            'error': f'获取测试历史失败: {str(e)}',
            'history': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_test_report(request):
    """获取测试报告路径"""
    try:
        report_path = settings.ALLURE_REPORT_DIR / 'index.html'
        
        if not report_path.exists():
            return Response({
                'error': '测试报告不存在',
                'report_url': None
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 返回报告URL
        report_url = f"/reports/allure-report/index.html"
        
        return Response({
            'report_url': report_url,
            'report_path': str(report_path),
            'exists': True
        })
        
    except Exception as e:
        logger.error(f"获取测试报告失败: {str(e)}")
        return Response({
            'error': f'获取测试报告失败: {str(e)}',
            'report_url': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def serve_report(request, path):
    """提供测试报告文件服务"""
    try:
        report_file = settings.ALLURE_REPORT_DIR / path
        
        if not report_file.exists():
            return Response({
                'error': '报告文件不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 根据文件类型设置Content-Type
        content_type = 'text/html'
        if path.endswith('.css'):
            content_type = 'text/css'
        elif path.endswith('.js'):
            content_type = 'application/javascript'
        elif path.endswith('.json'):
            content_type = 'application/json'
        elif path.endswith('.png'):
            content_type = 'image/png'
        elif path.endswith('.jpg') or path.endswith('.jpeg'):
            content_type = 'image/jpeg'
        
        return FileResponse(
            open(report_file, 'rb'),
            content_type=content_type
        )
        
    except Exception as e:
        logger.error(f"提供报告文件失败: {str(e)}")
        return Response({
            'error': f'提供报告文件失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_dashboard_stats(request):
    """获取仪表盘统计数据"""
    try:
        # 获取最近30天的测试统计
        from datetime import timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        recent_runs = TestRun.objects.filter(
            status='completed',
            completed_at__gte=thirty_days_ago
        )
        
        # 计算统计数据
        total_runs = recent_runs.count()
        total_tests = TestResult.objects.filter(
            test_run__in=recent_runs
        ).count()
        
        passed_tests = TestResult.objects.filter(
            test_run__in=recent_runs,
            status='passed'
        ).count()
        
        failed_tests = TestResult.objects.filter(
            test_run__in=recent_runs,
            status='failed'
        ).count()
        
        # 计算平均执行时间
        avg_duration = recent_runs.aggregate(
            avg_duration=models.Avg('duration')
        )['avg_duration'] or 0
        
        # 计算成功率
        success_rate = round(
            passed_tests / total_tests * 100, 2
        ) if total_tests > 0 else 0
        
        # 按类别统计
        categories_stats = {}
        for category in ['functional', 'api', 'performance', 'security', 'ui']:
            category_results = TestResult.objects.filter(
                test_run__in=recent_runs,
                category=category
            )
            
            categories_stats[category] = {
                'total': category_results.count(),
                'passed': category_results.filter(status='passed').count(),
                'failed': category_results.filter(status='failed').count(),
                'success_rate': round(
                    category_results.filter(status='passed').count() / 
                    category_results.count() * 100, 2
                ) if category_results.count() > 0 else 0
            }
        
        stats = {
            'total_runs': total_runs,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'avg_duration': round(avg_duration, 2),
            'categories': categories_stats,
            'period': '30天',
            'last_updated': datetime.now().isoformat()
        }
        
        return Response(stats)
        
    except Exception as e:
        logger.error(f"获取仪表盘统计失败: {str(e)}")
        return Response({
            'error': f'获取仪表盘统计失败: {str(e)}',
            'stats': {}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def stop_tests(request):
    """停止正在运行的测试"""
    try:
        if not test_executor.is_running:
            return Response({
                'message': '没有正在运行的测试',
                'status': 'not_running'
            })
        
        # 这里可以实现停止测试的逻辑
        # 由于pytest没有直接的停止API，我们只能标记状态
        test_executor.is_running = False
        test_executor.send_progress_update(0, "测试已停止", "stopped")
        
        return Response({
            'message': '测试已停止',
            'status': 'stopped'
        })
        
    except Exception as e:
        logger.error(f"停止测试失败: {str(e)}")
        return Response({
            'error': f'停止测试失败: {str(e)}',
            'status': 'error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
