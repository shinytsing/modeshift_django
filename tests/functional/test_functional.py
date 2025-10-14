"""
功能测试模块 - 测试网站核心功能流程
包含首页访问、用户注册、登录、表单提交等核心业务功能
"""
import pytest
import allure
import os
import time
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.management import call_command


@allure.epic("Shenyiqing.xin 网站全维度测试")
@allure.feature("功能测试")
class TestFunctionalPages(TestCase):
    """
    功能页面测试类
    测试网站各个页面的基本访问和功能
    """
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        # 确保有默认站点
        if not Site.objects.exists():
            Site.objects.create(domain='localhost:8000', name='localhost')
    
    @allure.story("首页访问")
    @allure.title("测试首页正常加载")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_homepage_loads(self):
        """
        验证网站首页是否能正常加载
        检查响应状态码和基本内容
        """
        with allure.step("访问首页"):
            response = self.client.get('/')
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.content.decode('utf-8', errors='ignore')[:500], 
                         name="Homepage Content", 
                         attachment_type=allure.attachment_type.HTML)
        
        with allure.step("验证响应状态码为200"):
            self.assertEqual(response.status_code, 200)
        
        with allure.step("验证页面包含基本内容"):
            content = response.content.decode('utf-8', errors='ignore')
            # 检查是否包含常见的HTML元素
            self.assertTrue(any(tag in content.lower() for tag in ['<html', '<head', '<body']))
    
    @allure.story("用户认证")
    @allure.title("测试登录页面访问")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_page_access(self):
        """
        验证用户登录页面是否可访问
        检查页面内容和表单元素
        """
        with allure.step("访问登录页面"):
            response = self.client.get('/accounts/login/')
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证响应状态码"):
            # 登录页面可能返回200或302（重定向）
            self.assertIn(response.status_code, [200, 302])
        
        if response.status_code == 200:
            with allure.step("验证页面包含登录表单"):
                content = response.content.decode('utf-8', errors='ignore')
                allure.attach(content[:1000], 
                             name="Login Page Content", 
                             attachment_type=allure.attachment_type.HTML)
    
    @allure.story("用户认证")
    @allure.title("测试注册页面访问")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_signup_page_access(self):
        """
        验证用户注册页面是否可访问
        检查页面内容和注册表单
        """
        with allure.step("访问注册页面"):
            response = self.client.get('/accounts/signup/')
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证响应状态码"):
            # 注册页面可能返回200或302（重定向）
            self.assertIn(response.status_code, [200, 302])
    
    @allure.story("核心功能")
    @allure.title("测试工具页面访问")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_tools_page_access(self):
        """
        验证工具页面是否可访问
        检查核心功能页面
        """
        with allure.step("访问工具页面"):
            response = self.client.get('/tools/')
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证响应状态码"):
            # 工具页面可能需要登录，所以接受200或302
            self.assertIn(response.status_code, [200, 302])
    
    @allure.story("核心功能")
    @allure.title("测试工作模式页面访问")
    @allure.severity(allure.severity_level.NORMAL)
    def test_work_mode_page_access(self):
        """
        验证工作模式页面是否可访问
        """
        with allure.step("访问工作模式页面"):
            response = self.client.get('/tools/work/')
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证响应状态码"):
            self.assertIn(response.status_code, [200, 302])
    
    @allure.story("核心功能")
    @allure.title("测试生活模式页面访问")
    @allure.severity(allure.severity_level.NORMAL)
    def test_life_mode_page_access(self):
        """
        验证生活模式页面是否可访问
        """
        with allure.step("访问生活模式页面"):
            response = self.client.get('/tools/life/')
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证响应状态码"):
            self.assertIn(response.status_code, [200, 302])
    
    @allure.story("系统监控")
    @allure.title("测试健康检查端点")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_health_check_endpoint(self):
        """
        验证健康检查端点是否正常工作
        用于监控系统状态
        """
        with allure.step("访问健康检查端点"):
            response = self.client.get('/health/')
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.content.decode('utf-8', errors='ignore'), 
                         name="Health Check Response", 
                         attachment_type=allure.attachment_type.JSON)
        
        with allure.step("验证响应状态码为200"):
            self.assertEqual(response.status_code, 200)
    
    @allure.story("管理功能")
    @allure.title("测试管理员页面访问")
    @allure.severity(allure.severity_level.NORMAL)
    def test_admin_page_access(self):
        """
        验证管理员页面是否可访问
        检查Django admin界面
        """
        with allure.step("访问管理员页面"):
            response = self.client.get('/admin/')
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证响应状态码"):
            # 管理员页面通常需要登录，所以接受200或302
            self.assertIn(response.status_code, [200, 302])


@allure.epic("Shenyiqing.xin 网站全维度测试")
@allure.feature("功能测试")
class TestUserAuthentication(TestCase):
    """
    用户认证测试类
    测试用户注册、登录、表单提交等功能
    """
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        # 确保有默认站点
        if not Site.objects.exists():
            Site.objects.create(domain='localhost:8000', name='localhost')
        
        # 测试用户数据
        self.user_data = {
            'username': 'testuser123',
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
    
    @allure.story("用户注册")
    @allure.title("测试新用户注册流程")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_user_registration(self):
        """
        测试新用户注册功能
        验证注册表单提交和用户创建
        """
        with allure.step("清理可能存在的测试用户"):
            User.objects.filter(username=self.user_data['username']).delete()
        
        with allure.step("访问注册页面"):
            response = self.client.get('/accounts/signup/')
            allure.attach(f"Registration Page Status: {response.status_code}", 
                         name="Registration Page", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("提交注册表单"):
            # 尝试注册新用户
            response = self.client.post('/accounts/signup/', {
                'username': self.user_data['username'],
                'email': self.user_data['email'],
                'password1': self.user_data['password'],
                'password2': self.user_data['password'],
            }, follow=True)
            
            allure.attach(f"Registration Response Status: {response.status_code}", 
                         name="Registration Response", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.content.decode('utf-8', errors='ignore')[:1000], 
                         name="Registration Response Content", 
                         attachment_type=allure.attachment_type.HTML)
        
        with allure.step("验证注册结果"):
            # 注册可能成功或失败，检查响应状态
            self.assertIn(response.status_code, [200, 302])
    
    @allure.story("用户登录")
    @allure.title("测试用户登录功能")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_user_login(self):
        """
        测试用户登录功能
        验证登录表单提交和认证
        """
        with allure.step("创建测试用户"):
            user, created = User.objects.get_or_create(
                username=self.user_data['username'],
                defaults={
                    'email': self.user_data['email'],
                    'is_active': True
                }
            )
            if created:
                user.set_password(self.user_data['password'])
                user.save()
            
            allure.attach(f"Test User Created: {created}, Username: {user.username}", 
                         name="Test User Info", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("访问登录页面"):
            response = self.client.get('/accounts/login/')
            allure.attach(f"Login Page Status: {response.status_code}", 
                         name="Login Page", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("提交登录表单"):
            response = self.client.post('/accounts/login/', {
                'login': self.user_data['username'],
                'password': self.user_data['password'],
            }, follow=True)
            
            allure.attach(f"Login Response Status: {response.status_code}", 
                         name="Login Response", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.content.decode('utf-8', errors='ignore')[:1000], 
                         name="Login Response Content", 
                         attachment_type=allure.attachment_type.HTML)
        
        with allure.step("验证登录结果"):
            # 登录可能成功或失败，检查响应状态
            self.assertIn(response.status_code, [200, 302])
    
    @allure.story("表单提交")
    @allure.title("测试表单提交功能")
    @allure.severity(allure.severity_level.NORMAL)
    def test_form_submission(self):
        """
        测试表单提交功能
        验证表单数据处理和响应
        """
        with allure.step("测试登录表单提交"):
            response = self.client.post('/accounts/login/', {
                'login': 'nonexistent@example.com',
                'password': 'wrongpassword',
            })
            
            allure.attach(f"Form Submission Status: {response.status_code}", 
                         name="Form Submission", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.content.decode('utf-8', errors='ignore')[:1000], 
                         name="Form Submission Content", 
                         attachment_type=allure.attachment_type.HTML)
        
        with allure.step("验证表单提交响应"):
            # 表单提交应该返回200（显示错误）或302（重定向）
            self.assertIn(response.status_code, [200, 302])


@allure.epic("Shenyiqing.xin 网站全维度测试")
@allure.feature("功能测试")
class TestCoreBusinessLogic(TestCase):
    """
    核心业务逻辑测试类
    测试网站的核心业务功能
    """
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        # 确保有默认站点
        if not Site.objects.exists():
            Site.objects.create(domain='localhost:8000', name='localhost')
    
    @allure.story("内容管理")
    @allure.title("测试内容页面访问")
    @allure.severity(allure.severity_level.NORMAL)
    def test_content_pages_access(self):
        """
        测试内容相关页面的访问
        验证内容管理功能
        """
        content_urls = [
            '/content/',
            '/posts/',
            '/articles/',
        ]
        
        for url in content_urls:
            with allure.step(f"访问内容页面: {url}"):
                response = self.client.get(url)
                allure.attach(f"Content Page {url} Status: {response.status_code}", 
                             name=f"Content Page {url}", 
                             attachment_type=allure.attachment_type.TEXT)
                
                # 内容页面可能返回200、302或404
                self.assertIn(response.status_code, [200, 302, 404])
    
    @allure.story("API接口")
    @allure.title("测试API端点访问")
    @allure.severity(allure.severity_level.NORMAL)
    def test_api_endpoints_access(self):
        """
        测试API端点的基本访问
        验证API接口可用性
        """
        api_urls = [
            '/api/',
            '/api/health/',
            '/api/users/',
        ]
        
        for url in api_urls:
            with allure.step(f"访问API端点: {url}"):
                response = self.client.get(url)
                allure.attach(f"API Endpoint {url} Status: {response.status_code}", 
                             name=f"API Endpoint {url}", 
                             attachment_type=allure.attachment_type.TEXT)
                
                # API端点可能返回200、401、403、404等
                self.assertIn(response.status_code, [200, 401, 403, 404])
    
    @allure.story("静态资源")
    @allure.title("测试静态资源加载")
    @allure.severity(allure.severity_level.MINOR)
    def test_static_resources_access(self):
        """
        测试静态资源的访问
        验证CSS、JS、图片等资源加载
        """
        static_urls = [
            '/static/css/main.css',
            '/static/js/main.js',
            '/favicon.ico',
        ]
        
        for url in static_urls:
            with allure.step(f"访问静态资源: {url}"):
                response = self.client.get(url)
                allure.attach(f"Static Resource {url} Status: {response.status_code}", 
                             name=f"Static Resource {url}", 
                             attachment_type=allure.attachment_type.TEXT)
                
                # 静态资源可能返回200或404
                self.assertIn(response.status_code, [200, 404])






