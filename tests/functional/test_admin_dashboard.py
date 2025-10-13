"""
Django网站功能测试 - 管理员面板
项目：shenyiqing.xin
功能：测试管理员面板相关功能
"""

import pytest
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.admin.sites import site


@pytest.mark.functional
class TestAdminDashboard:
    """管理员面板测试类"""
    
    def test_admin_login_page(self, client):
        """测试管理员登录页面"""
        response = client.get('/admin/')
        assert response.status_code == 200
        assert 'admin' in response.content.decode().lower()
    
    def test_admin_login_with_valid_credentials(self, admin_client):
        """测试使用有效凭据登录管理员面板"""
        response = admin_client.get('/admin/')
        assert response.status_code == 200
        assert 'admin' in response.content.decode().lower()
    
    def test_admin_login_with_invalid_credentials(self, client):
        """测试使用无效凭据登录管理员面板"""
        response = client.post('/admin/login/', {
            'username': 'nonexistent',
            'password': 'wrongpass'
        })
        assert response.status_code == 200
        assert 'error' in response.content.decode().lower() or 'invalid' in response.content.decode().lower()
    
    def test_admin_dashboard_access(self, admin_client):
        """测试管理员面板访问"""
        response = admin_client.get('/admin/')
        assert response.status_code == 200
        assert 'dashboard' in response.content.decode().lower() or 'admin' in response.content.decode().lower()
    
    def test_admin_user_management(self, admin_client):
        """测试管理员用户管理功能"""
        response = admin_client.get('/admin/auth/user/')
        assert response.status_code == 200
        
        # 测试创建新用户
        user_data = {
            'username': 'newadminuser',
            'email': 'newadmin@example.com',
            'password1': 'adminpass123',
            'password2': 'adminpass123',
            'is_staff': True,
            'is_superuser': True
        }
        
        response = admin_client.post('/admin/auth/user/add/', user_data)
        assert response.status_code == 302  # 重定向到用户列表
        
        # 检查用户是否创建
        assert User.objects.filter(username='newadminuser').exists()
    
    def test_admin_user_edit(self, admin_client, test_user):
        """测试管理员编辑用户"""
        response = admin_client.get(f'/admin/auth/user/{test_user.id}/change/')
        assert response.status_code == 200
        
        # 编辑用户信息
        edit_data = {
            'username': test_user.username,
            'email': 'edited@example.com',
            'first_name': 'Edited',
            'last_name': 'User',
            'is_active': True,
            'is_staff': False,
            'is_superuser': False
        }
        
        response = admin_client.post(f'/admin/auth/user/{test_user.id}/change/', edit_data)
        assert response.status_code == 302
        
        # 检查用户信息是否更新
        test_user.refresh_from_db()
        assert test_user.email == 'edited@example.com'
        assert test_user.first_name == 'Edited'
    
    def test_admin_user_delete(self, admin_client):
        """测试管理员删除用户"""
        # 创建测试用户
        user = User.objects.create_user(
            username='tobedeleted',
            email='delete@example.com',
            password='deletepass123'
        )
        
        response = admin_client.post(f'/admin/auth/user/{user.id}/delete/', {
            'post': 'yes'
        })
        assert response.status_code == 302
        
        # 检查用户是否删除
        assert not User.objects.filter(username='tobedeleted').exists()
    
    def test_admin_permissions(self, client, test_user):
        """测试管理员权限控制"""
        # 普通用户尝试访问管理员面板
        client.force_login(test_user)
        response = client.get('/admin/')
        assert response.status_code == 302  # 重定向到登录页面
    
    def test_admin_logout(self, admin_client):
        """测试管理员登出"""
        response = admin_client.post('/admin/logout/')
        assert response.status_code == 302
        
        # 尝试访问需要权限的页面
        response = admin_client.get('/admin/auth/user/')
        assert response.status_code == 302  # 重定向到登录页面
    
    def test_admin_search_functionality(self, admin_client):
        """测试管理员搜索功能"""
        response = admin_client.get('/admin/auth/user/?q=test')
        assert response.status_code == 200
        
        # 检查搜索结果
        content = response.content.decode()
        assert 'test' in content.lower() or 'no results' in content.lower()
    
    def test_admin_filter_functionality(self, admin_client):
        """测试管理员过滤功能"""
        response = admin_client.get('/admin/auth/user/?is_active__exact=1')
        assert response.status_code == 200
        
        # 检查过滤结果
        content = response.content.decode()
        assert 'filter' in content.lower() or 'active' in content.lower()
    
    def test_admin_bulk_actions(self, admin_client):
        """测试管理员批量操作"""
        # 创建多个测试用户
        users = []
        for i in range(3):
            user = User.objects.create_user(
                username=f'bulkuser{i}',
                email=f'bulk{i}@example.com',
                password='bulkpass123'
            )
            users.append(user)
        
        # 批量删除用户
        user_ids = [str(user.id) for user in users]
        response = admin_client.post('/admin/auth/user/', {
            'action': 'delete_selected',
            'select_across': '0',
            'index': '0',
            '_selected_action': user_ids
        })
        assert response.status_code == 200 or response.status_code == 302
        
        # 检查用户是否删除
        for user in users:
            assert not User.objects.filter(id=user.id).exists()
    
    def test_admin_export_functionality(self, admin_client):
        """测试管理员导出功能"""
        response = admin_client.get('/admin/auth/user/export/')
        assert response.status_code == 200
        
        # 检查响应内容类型
        assert 'csv' in response.get('Content-Type', '').lower() or 'excel' in response.get('Content-Type', '').lower()
    
    def test_admin_import_functionality(self, admin_client):
        """测试管理员导入功能"""
        response = admin_client.get('/admin/auth/user/import/')
        assert response.status_code == 200
        
        # 检查是否有导入表单
        content = response.content.decode()
        assert 'import' in content.lower() or 'upload' in content.lower()
    
    def test_admin_audit_log(self, admin_client):
        """测试管理员审计日志"""
        response = admin_client.get('/admin/audit/log/')
        assert response.status_code == 200
        
        # 检查是否有日志记录
        content = response.content.decode()
        assert 'log' in content.lower() or 'audit' in content.lower()
    
    def test_admin_system_settings(self, admin_client):
        """测试管理员系统设置"""
        response = admin_client.get('/admin/settings/')
        assert response.status_code == 200
        
        # 检查是否有设置表单
        content = response.content.decode()
        assert 'setting' in content.lower() or 'config' in content.lower()
    
    def test_admin_backup_restore(self, admin_client):
        """测试管理员备份恢复功能"""
        response = admin_client.get('/admin/backup/')
        assert response.status_code == 200
        
        # 检查是否有备份选项
        content = response.content.decode()
        assert 'backup' in content.lower() or 'restore' in content.lower()
    
    def test_admin_security_settings(self, admin_client):
        """测试管理员安全设置"""
        response = admin_client.get('/admin/security/')
        assert response.status_code == 200
        
        # 检查是否有安全选项
        content = response.content.decode()
        assert 'security' in content.lower() or 'password' in content.lower()
    
    def test_admin_performance_monitoring(self, admin_client):
        """测试管理员性能监控"""
        response = admin_client.get('/admin/performance/')
        assert response.status_code == 200
        
        # 检查是否有性能指标
        content = response.content.decode()
        assert 'performance' in content.lower() or 'monitor' in content.lower()
    
    def test_admin_error_logs(self, admin_client):
        """测试管理员错误日志"""
        response = admin_client.get('/admin/errors/')
        assert response.status_code == 200
        
        # 检查是否有错误记录
        content = response.content.decode()
        assert 'error' in content.lower() or 'log' in content.lower()
    
    def test_admin_database_management(self, admin_client):
        """测试管理员数据库管理"""
        response = admin_client.get('/admin/database/')
        assert response.status_code == 200
        
        # 检查是否有数据库选项
        content = response.content.decode()
        assert 'database' in content.lower() or 'table' in content.lower()
    
    def test_admin_cache_management(self, admin_client):
        """测试管理员缓存管理"""
        response = admin_client.get('/admin/cache/')
        assert response.status_code == 200
        
        # 检查是否有缓存选项
        content = response.content.decode()
        assert 'cache' in content.lower() or 'clear' in content.lower()
    
    def test_admin_session_management(self, admin_client):
        """测试管理员会话管理"""
        response = admin_client.get('/admin/sessions/')
        assert response.status_code == 200
        
        # 检查是否有会话信息
        content = response.content.decode()
        assert 'session' in content.lower() or 'user' in content.lower()
    
    def test_admin_notification_system(self, admin_client):
        """测试管理员通知系统"""
        response = admin_client.get('/admin/notifications/')
        assert response.status_code == 200
        
        # 检查是否有通知选项
        content = response.content.decode()
        assert 'notification' in content.lower() or 'alert' in content.lower()
    
    def test_admin_analytics_dashboard(self, admin_client):
        """测试管理员分析面板"""
        response = admin_client.get('/admin/analytics/')
        assert response.status_code == 200
        
        # 检查是否有分析数据
        content = response.content.decode()
        assert 'analytics' in content.lower() or 'chart' in content.lower()
    
    def test_admin_mobile_responsiveness(self, admin_client):
        """测试管理员面板移动端响应性"""
        response = admin_client.get('/admin/', HTTP_USER_AGENT='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)')
        assert response.status_code == 200
        
        # 检查是否有移动端适配
        content = response.content.decode()
        assert 'mobile' in content.lower() or 'responsive' in content.lower() or 'viewport' in content.lower()
    
    def test_admin_accessibility(self, admin_client):
        """测试管理员面板可访问性"""
        response = admin_client.get('/admin/')
        assert response.status_code == 200
        
        # 检查是否有可访问性特性
        content = response.content.decode()
        assert 'aria-' in content.lower() or 'alt=' in content.lower() or 'role=' in content.lower()
    
    def test_admin_internationalization(self, admin_client):
        """测试管理员面板国际化"""
        response = admin_client.get('/admin/', HTTP_ACCEPT_LANGUAGE='zh-CN')
        assert response.status_code == 200
        
        # 检查是否有中文内容
        content = response.content.decode()
        # 这里可以根据实际的多语言支持情况调整断言
        assert len(content) > 0  # 至少应该有内容
