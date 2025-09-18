"""
Trojan代理服务视图
提供代理配置、管理和监控功能
"""

import json
import logging
from typing import Dict, Any

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from ..services.trojan_auth_service import TrojanAuthService
from ..services.trojan_user_manager import TrojanUserManager
from ..services.trojan_monitor import TrojanMonitor

logger = logging.getLogger(__name__)


class TrojanDashboardView(View):
    """Trojan代理仪表板"""
    
    @method_decorator(login_required)
    def get(self, request):
        """显示代理仪表板"""
        try:
            auth_service = TrojanAuthService()
            user_info = auth_service.get_user_trojan_info(request.user)
            
            context = {
                'user_info': user_info,
                'page_title': 'Trojan代理服务',
                'page_description': '安全、快速的代理服务'
            }
            
            return render(request, 'tools/trojan_dashboard.html', context)
            
        except Exception as e:
            logger.error(f"显示Trojan仪表板失败: {e}")
            return render(request, 'tools/trojan_dashboard.html', {
                'error': str(e),
                'page_title': 'Trojan代理服务'
            })


class TrojanConfigView(View):
    """Trojan配置管理"""
    
    @method_decorator(login_required)
    def get(self, request):
        """获取用户配置"""
        try:
            auth_service = TrojanAuthService()
            user_info = auth_service.get_user_trojan_info(request.user)
            
            return JsonResponse({
                'success': True,
                'data': user_info
            })
            
        except Exception as e:
            logger.error(f"获取Trojan配置失败: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    @method_decorator(login_required)
    def post(self, request):
        """创建或更新配置"""
        try:
            auth_service = TrojanAuthService()
            
            # 检查用户是否已有配置
            user_info = auth_service.get_user_trojan_info(request.user)
            if user_info.get('has_config'):
                return JsonResponse({
                    'success': False,
                    'error': '用户已有Trojan配置'
                })
            
            # 创建新配置
            success, msg, config_data = auth_service.create_trojan_config_for_user(
                user=request.user,
                expires_days=30
            )
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': msg,
                    'data': config_data
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': msg
                })
                
        except Exception as e:
            logger.error(f"创建Trojan配置失败: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class TrojanConfigDownloadView(View):
    """Trojan配置下载"""
    
    @method_decorator(login_required)
    def get(self, request, config_type='trojan'):
        """下载配置文件"""
        try:
            auth_service = TrojanAuthService()
            user_manager = TrojanUserManager()
            
            # 获取配置
            user_info = auth_service.get_user_trojan_info(request.user)
            if not user_info.get('has_config'):
                return JsonResponse({
                    'success': False,
                    'error': '用户没有Trojan配置'
                })
            
            # 根据类型生成配置
            if config_type == 'trojan':
                success, msg, config = user_manager.generate_client_config(request.user)
                filename = f"trojan-{request.user.username}.json"
                content_type = 'application/json'
            elif config_type == 'clash':
                success, msg, config = user_manager.generate_clash_config(request.user)
                filename = f"clash-{request.user.username}.yaml"
                content_type = 'application/x-yaml'
            elif config_type == 'v2ray':
                success, msg, config = user_manager.generate_v2ray_config(request.user)
                filename = f"v2ray-{request.user.username}.json"
                content_type = 'application/json'
            else:
                return JsonResponse({
                    'success': False,
                    'error': '不支持的配置类型'
                })
            
            if not success:
                return JsonResponse({
                    'success': False,
                    'error': msg
                })
            
            # 生成响应
            if config_type == 'clash':
                import yaml
                content = yaml.dump(config, default_flow_style=False, allow_unicode=True)
            else:
                content = json.dumps(config, indent=2, ensure_ascii=False)
            
            response = HttpResponse(content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            logger.error(f"下载Trojan配置失败: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class TrojanUsageStatsView(View):
    """Trojan使用统计"""
    
    @method_decorator(login_required)
    def get(self, request):
        """获取使用统计"""
        try:
            user_manager = TrojanUserManager()
            monitor = TrojanMonitor()
            
            # 获取用户统计
            user_stats = user_manager.get_user_usage_stats(request.user, days=30)
            
            # 获取用户活动
            user_activity = monitor.get_user_activity(request.user, hours=24)
            
            return JsonResponse({
                'success': True,
                'data': {
                    'usage_stats': user_stats,
                    'activity': user_activity
                }
            })
            
        except Exception as e:
            logger.error(f"获取Trojan使用统计失败: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class TrojanAuthView(View):
    """Trojan认证"""
    
    def get(self, request):
        """显示认证页面"""
        return render(request, 'tools/trojan_auth.html', {
            'page_title': 'Trojan代理认证',
            'page_description': '请登录以使用Trojan代理服务'
        })
    
    @csrf_exempt
    def post(self, request):
        """处理认证请求"""
        try:
            auth_service = TrojanAuthService()
            
            # 获取认证参数
            username = request.POST.get('username')
            password = request.POST.get('password')
            google_token = request.POST.get('google_token')
            
            # 执行认证
            success, msg, user = auth_service.authenticate_user(
                request=request,
                username=username,
                password=password,
                google_token=google_token
            )
            
            if success and user:
                # 登录用户
                from django.contrib.auth import login
                login(request, user)
                
                return JsonResponse({
                    'success': True,
                    'message': msg,
                    'redirect_url': '/trojan/dashboard/'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': msg
                })
                
        except Exception as e:
            logger.error(f"Trojan认证失败: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class TrojanGoogleAuthView(View):
    """Google OAuth认证"""
    
    def get(self, request):
        """启动Google OAuth流程"""
        try:
            auth_service = TrojanAuthService()
            auth_url = auth_service.get_google_oauth_url(request)
            return redirect(auth_url)
            
        except Exception as e:
            logger.error(f"启动Google OAuth失败: {e}")
            return render(request, 'tools/trojan_auth.html', {
                'error': f'Google OAuth启动失败: {e}',
                'page_title': 'Trojan代理认证'
            })


class TrojanGoogleCallbackView(View):
    """Google OAuth回调"""
    
    def get(self, request):
        """处理Google OAuth回调"""
        try:
            auth_service = TrojanAuthService()
            
            code = request.GET.get('code')
            state = request.GET.get('state')
            
            if not code or not state:
                return render(request, 'tools/trojan_auth.html', {
                    'error': 'OAuth回调参数不完整',
                    'page_title': 'Trojan代理认证'
                })
            
            # 处理OAuth回调
            success, msg, user = auth_service.handle_google_oauth_callback(
                request=request,
                code=code,
                state=state
            )
            
            if success and user:
                # 登录用户
                from django.contrib.auth import login
                login(request, user)
                
                # 重定向到仪表板
                return redirect('/trojan/dashboard/')
            else:
                return render(request, 'tools/trojan_auth.html', {
                    'error': msg,
                    'page_title': 'Trojan代理认证'
                })
                
        except Exception as e:
            logger.error(f"处理Google OAuth回调失败: {e}")
            return render(request, 'tools/trojan_auth.html', {
                'error': f'OAuth回调处理失败: {e}',
                'page_title': 'Trojan代理认证'
            })


class TrojanAdminView(View):
    """Trojan管理界面（管理员）"""
    
    @method_decorator(login_required)
    def get(self, request):
        """显示管理界面"""
        try:
            # 检查管理员权限
            if not (request.user.is_staff or 
                   (hasattr(request.user, 'role') and request.user.role.is_admin)):
                return render(request, 'tools/trojan_dashboard.html', {
                    'error': '权限不足',
                    'page_title': 'Trojan代理服务'
                })
            
            user_manager = TrojanUserManager()
            monitor = TrojanMonitor()
            
            # 获取服务器状态
            server_status = user_manager.get_server_status()
            
            # 获取仪表板数据
            dashboard_data = monitor.get_dashboard_data()
            
            # 获取所有用户配置
            all_users = user_manager.get_all_users_with_config()
            
            context = {
                'server_status': server_status,
                'dashboard_data': dashboard_data,
                'all_users': all_users,
                'page_title': 'Trojan代理管理',
                'page_description': 'Trojan代理服务管理界面'
            }
            
            return render(request, 'tools/trojan_admin.html', context)
            
        except Exception as e:
            logger.error(f"显示Trojan管理界面失败: {e}")
            return render(request, 'tools/trojan_admin.html', {
                'error': str(e),
                'page_title': 'Trojan代理管理'
            })


@login_required
@require_http_methods(["POST"])
def refresh_trojan_config(request):
    """刷新Trojan配置"""
    try:
        auth_service = TrojanAuthService()
        success, msg = auth_service.refresh_user_config(request.user)
        
        return JsonResponse({
            'success': success,
            'message': msg
        })
        
    except Exception as e:
        logger.error(f"刷新Trojan配置失败: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["POST"])
def revoke_trojan_access(request):
    """撤销Trojan访问权限"""
    try:
        auth_service = TrojanAuthService()
        success, msg = auth_service.revoke_user_access(request.user)
        
        return JsonResponse({
            'success': success,
            'message': msg
        })
        
    except Exception as e:
        logger.error(f"撤销Trojan访问权限失败: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["POST"])
def restore_trojan_access(request):
    """恢复Trojan访问权限"""
    try:
        auth_service = TrojanAuthService()
        success, msg = auth_service.restore_user_access(request.user)
        
        return JsonResponse({
            'success': success,
            'message': msg
        })
        
    except Exception as e:
        logger.error(f"恢复Trojan访问权限失败: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["GET"])
def trojan_server_control(request, action):
    """Trojan服务器控制（管理员）"""
    try:
        # 检查管理员权限
        if not (request.user.is_staff or 
               (hasattr(request.user, 'role') and request.user.role.is_admin)):
            return JsonResponse({
                'success': False,
                'error': '权限不足'
            })
        
        user_manager = TrojanUserManager()
        
        if action == 'start':
            success, msg = user_manager.start_server()
        elif action == 'stop':
            success, msg = user_manager.stop_server()
        elif action == 'restart':
            success, msg = user_manager.restart_server()
        elif action == 'status':
            status = user_manager.get_server_status()
            return JsonResponse({
                'success': True,
                'data': status
            })
        else:
            return JsonResponse({
                'success': False,
                'error': '不支持的操作'
            })
        
        return JsonResponse({
            'success': success,
            'message': msg
        })
        
    except Exception as e:
        logger.error(f"Trojan服务器控制失败: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["GET"])
def trojan_usage_report(request):
    """Trojan使用报告"""
    try:
        # 检查管理员权限
        if not (request.user.is_staff or 
               (hasattr(request.user, 'role') and request.user.role.is_admin)):
            return JsonResponse({
                'success': False,
                'error': '权限不足'
            })
        
        monitor = TrojanMonitor()
        
        # 获取参数
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        format_type = request.GET.get('format', 'json')
        
        if not start_date or not end_date:
            return JsonResponse({
                'success': False,
                'error': '缺少日期参数'
            })
        
        # 解析日期
        start_dt = timezone.datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = timezone.datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # 生成报告
        success, msg, report = monitor.export_usage_report(start_dt, end_dt, format_type)
        
        if success:
            if format_type == 'json':
                return JsonResponse({
                    'success': True,
                    'data': json.loads(report)
                })
            else:
                response = HttpResponse(report, content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="trojan_usage_report_{start_date}_{end_date}.csv"'
                return response
        else:
            return JsonResponse({
                'success': False,
                'error': msg
            })
            
    except Exception as e:
        logger.error(f"生成Trojan使用报告失败: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

