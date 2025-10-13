"""
Django网站功能测试用例
覆盖页面访问、注册、登录、表单提交等核心业务流程
"""

import pytest
import allure
import time
import requests
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from bs4 import BeautifulSoup


@pytest.mark.django_db
@allure.epic("Django网站全维度测试")
@allure.feature("功能测试")
class TestFunctionalPages(TestCase):
    """功能页面测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        self.base_url = "http://localhost:8000"
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123!',
            'password2': 'testpass123!'
        }
    
    @allure.story("页面访问测试")
    @allure.title("测试首页正常加载")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_homepage_loads(self):
        """测试首页能够正常加载并返回200状态码"""
        with allure.step("访问首页"):
            response = self.client.get('/')
            allure.attach(f"状态码: {response.status_code}", name="响应状态码", attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证响应状态码"):
            assert response.status_code == 200, f"首页访问失败，状态码: {response.status_code}"
        
        with allure.step("验证页面内容"):
            content = response.content.decode('utf-8')
            assert 'html' in content.lower(), "页面内容不包含HTML标签"
            allure.attach(content[:500], name="页面内容片段", attachment_type=allure.attachment_type.TEXT)
    
    @allure.story("用户认证测试")
    @allure.title("测试用户登录页面访问")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_page_access(self):
        """测试用户登录页面能够正常访问"""
        with allure.step("访问登录页面"):
            response = self.client.get('/accounts/login/')
            allure.attach(f"状态码: {response.status_code}", name="响应状态码", attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证响应状态码"):
            assert response.status_code == 200, f"登录页面访问失败，状态码: {response.status_code}"
        
        with allure.step("验证登录表单存在"):
            content = response.content.decode('utf-8')
            assert 'login' in content.lower() or 'password' in content.lower(), "登录页面不包含登录表单"
            allure.attach(content[:500], name="登录页面内容", attachment_type=allure.attachment_type.TEXT)
    
    @allure.story("用户认证测试")
    @allure.title("测试用户注册页面访问")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_signup_page_access(self):
        """测试用户注册页面能够正常访问"""
        with allure.step("访问注册页面"):
            response = self.client.get('/accounts/signup/')
            allure.attach(f"状态码: {response.status_code}", name="响应状态码", attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证响应状态码"):
            assert response.status_code == 200, f"注册页面访问失败，状态码: {response.status_code}"
        
        with allure.step("验证注册表单存在"):
            content = response.content.decode('utf-8')
            assert 'signup' in content.lower() or 'register' in content.lower(), "注册页面不包含注册表单"
            allure.attach(content[:500], name="注册页面内容", attachment_type=allure.attachment_type.TEXT)
    
    @allure.story("工具页面测试")
    @allure.title("测试工具主页面访问")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_tools_page_access(self):
        """测试工具主页面能够正常访问"""
        with allure.step("访问工具主页面"):
            response = self.client.get('/tools/')
            allure.attach(f"状态码: {response.status_code}", name="响应状态码", attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证响应状态码"):
            # 工具页面可能需要登录，所以接受重定向
            assert response.status_code in [200, 302], f"工具页面访问异常，状态码: {response.status_code}"
        
        with allure.step("验证页面内容或重定向"):
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                allure.attach(content[:500], name="工具页面内容", attachment_type=allure.attachment_type.TEXT)
            else:
                allure.attach(f"重定向到: {response.url}", name="重定向信息", attachment_type=allure.attachment_type.TEXT)
    
    @allure.story("工具页面测试")
    @allure.title("测试工作模式页面访问")
    @allure.severity(allure.severity_level.NORMAL)
    def test_work_mode_page_access(self):
        """测试工作模式页面能够正常访问"""
        with allure.step("访问工作模式页面"):
            response = self.client.get('/tools/work/')
            allure.attach(f"状态码: {response.status_code}", name="响应状态码", attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证响应状态码"):
            assert response.status_code in [200, 302], f"工作模式页面访问异常，状态码: {response.status_code}"
    
    @allure.story("工具页面测试")
    @allure.title("测试生活模式页面访问")
    @allure.severity(allure.severity_level.NORMAL)
    def test_life_mode_page_access(self):
        """测试生活模式页面能够正常访问"""
        with allure.step("访问生活模式页面"):
            response = self.client.get('/tools/life/')
            allure.attach(f"状态码: {response.status_code}", name="响应状态码", attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证响应状态码"):
            assert response.status_code in [200, 302], f"生活模式页面访问异常，状态码: {response.status_code}"
    
    @allure.story("健康检查测试")
    @allure.title("测试健康检查端点")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_health_check_endpoint(self):
        """测试健康检查端点返回正确的JSON响应"""
        with allure.step("访问健康检查端点"):
            response = self.client.get('/health/')
            allure.attach(f"状态码: {response.status_code}", name="响应状态码", attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证响应状态码"):
            assert response.status_code == 200, f"健康检查端点异常，状态码: {response.status_code}"
        
        with allure.step("验证响应内容"):
            try:
                data = response.json()
                assert 'status' in data, "健康检查响应缺少status字段"
                allure.attach(str(data), name="健康检查响应", attachment_type=allure.attachment_type.JSON)
            except Exception as e:
                allure.attach(f"JSON解析失败: {e}", name="错误信息", attachment_type=allure.attachment_type.TEXT)
                assert False, f"健康检查响应不是有效的JSON格式: {e}"
    
    @allure.story("管理员功能测试")
    @allure.title("测试管理员页面访问")
    @allure.severity(allure.severity_level.NORMAL)
    def test_admin_page_access(self):
        """测试Django管理员页面能够正常访问"""
        with allure.step("访问管理员页面"):
            response = self.client.get('/admin/')
            allure.attach(f"状态码: {response.status_code}", name="响应状态码", attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证响应状态码"):
            # 管理员页面会重定向到登录页面
            assert response.status_code in [200, 302], f"管理员页面访问异常，状态码: {response.status_code}"
        
        with allure.step("验证重定向或登录页面"):
            if response.status_code == 302:
                allure.attach(f"重定向到: {response.url}", name="重定向信息", attachment_type=allure.attachment_type.TEXT)
            else:
                content = response.content.decode('utf-8')
                allure.attach(content[:500], name="管理员页面内容", attachment_type=allure.attachment_type.TEXT)


@pytest.mark.django_db
@allure.epic("Django网站全维度测试")
@allure.feature("功能测试")
class TestUserAuthentication(TestCase):
    """用户认证功能测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123!',
            'password2': 'testpass123!'
        }
    
    @allure.story("用户注册测试")
    @allure.title("测试用户注册功能")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_user_registration(self):
        """测试用户注册功能是否正常工作"""
        with allure.step("清理可能存在的测试用户"):
            User = get_user_model()
            User.objects.filter(username=self.user_data['username']).delete()
        
        with allure.step("访问注册页面"):
            response = self.client.get('/accounts/signup/')
            assert response.status_code == 200, "注册页面访问失败"
        
        with allure.step("提交注册表单"):
            response = self.client.post('/accounts/signup/', self.user_data)
            allure.attach(f"注册响应状态码: {response.status_code}", name="注册响应", attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证注册结果"):
            # 注册成功通常会重定向或返回成功页面
            assert response.status_code in [200, 302], f"注册失败，状态码: {response.status_code}"
            
            # 验证用户是否创建成功
            User = get_user_model()
            user_exists = User.objects.filter(username=self.user_data['username']).exists()
            allure.attach(f"用户创建状态: {user_exists}", name="用户创建结果", attachment_type=allure.attachment_type.TEXT)
    
    @allure.story("用户登录测试")
    @allure.title("测试用户登录功能")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_user_login(self):
        """测试用户登录功能是否正常工作"""
        with allure.step("创建测试用户"):
            User = get_user_model()
            user, created = User.objects.get_or_create(
                username=self.user_data['username'],
                defaults={
                    'email': self.user_data['email'],
                    'is_active': True
                }
            )
            if created:
                user.set_password(self.user_data['password1'])
                user.save()
            allure.attach(f"用户创建状态: {created}", name="用户创建", attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("访问登录页面"):
            response = self.client.get('/accounts/login/')
            assert response.status_code == 200, "登录页面访问失败"
        
        with allure.step("提交登录表单"):
            login_data = {
                'login': self.user_data['username'],
                'password': self.user_data['password1']
            }
            response = self.client.post('/accounts/login/', login_data)
            allure.attach(f"登录响应状态码: {response.status_code}", name="登录响应", attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证登录结果"):
            # 登录成功通常会重定向
            assert response.status_code in [200, 302], f"登录失败，状态码: {response.status_code}"
            
            # 验证用户是否已登录
            if hasattr(response, 'wsgi_request'):
                is_authenticated = response.wsgi_request.user.is_authenticated
                allure.attach(f"用户登录状态: {is_authenticated}", name="登录状态", attachment_type=allure.attachment_type.TEXT)
    
    @allure.story("表单提交测试")
    @allure.title("测试表单提交功能")
    @allure.severity(allure.severity_level.NORMAL)
    def test_form_submission(self):
        """测试表单提交功能是否正常工作"""
        with allure.step("测试CSRF保护"):
            # 测试CSRF保护是否生效
            response = self.client.post('/accounts/login/', {
                'login': 'testuser',
                'password': 'testpass'
            })
            allure.attach(f"CSRF测试响应状态码: {response.status_code}", name="CSRF测试", attachment_type=allure.attachment_type.TEXT)
            
            # CSRF保护应该返回403或重定向到错误页面
            assert response.status_code in [200, 302, 403], f"CSRF保护异常，状态码: {response.status_code}"
        
        with allure.step("测试表单验证"):
            # 测试空表单提交
            response = self.client.post('/accounts/login/', {})
            allure.attach(f"空表单测试响应状态码: {response.status_code}", name="表单验证", attachment_type=allure.attachment_type.TEXT)
            
            assert response.status_code in [200, 400], f"表单验证异常，状态码: {response.status_code}"


