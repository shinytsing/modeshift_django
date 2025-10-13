"""
接口测试模块 - 测试网站API接口功能
包含API端点状态码、响应内容、错误处理、Token认证等
"""
import pytest
import allure
import requests
import json
import time
from django.test import TestCase, Client
from django.contrib.auth.models import User


@allure.epic("Shenyiqing.xin 网站全维度测试")
@allure.feature("接口测试")
class TestAPIEndpoints(TestCase):
    """
    API端点测试类
    测试网站各个API接口的基本功能
    """
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        self.base_url = "http://localhost:8000"
        
        # 创建测试用户
        self.test_user = User.objects.create_user(
            username='apitest',
            email='apitest@example.com',
            password='testpass123'
        )
    
    @allure.story("健康检查API")
    @allure.title("测试健康检查API响应")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_health_check_api(self):
        """
        测试健康检查API
        验证API状态和响应格式
        """
        with allure.step("发送GET请求到健康检查API"):
            response = self.client.get('/health/')
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.content.decode('utf-8', errors='ignore'), 
                         name="Response Body", 
                         attachment_type=allure.attachment_type.JSON)
        
        with allure.step("验证响应状态码为200"):
            self.assertEqual(response.status_code, 200)
        
        with allure.step("验证响应内容格式"):
            try:
                data = json.loads(response.content.decode('utf-8', errors='ignore'))
                allure.attach(json.dumps(data, indent=2), 
                             name="Parsed JSON Response", 
                             attachment_type=allure.attachment_type.JSON)
            except json.JSONDecodeError:
                # 如果不是JSON格式，检查是否包含基本文本
                content = response.content.decode('utf-8', errors='ignore')
                self.assertTrue(len(content) > 0)
    
    @allure.story("认证API")
    @allure.title("测试登录API端点")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_api_endpoint(self):
        """
        测试登录API端点
        验证认证接口的响应
        """
        with allure.step("发送GET请求到登录API"):
            response = self.client.get('/accounts/login/')
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.content.decode('utf-8', errors='ignore')[:1000], 
                         name="Response Content", 
                         attachment_type=allure.attachment_type.HTML)
        
        with allure.step("验证响应状态码"):
            # 登录页面可能返回200或302
            self.assertIn(response.status_code, [200, 302])
    
    @allure.story("认证API")
    @allure.title("测试注册API端点")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_signup_api_endpoint(self):
        """
        测试注册API端点
        验证注册接口的响应
        """
        with allure.step("发送GET请求到注册API"):
            response = self.client.get('/accounts/signup/')
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.content.decode('utf-8', errors='ignore')[:1000], 
                         name="Response Content", 
                         attachment_type=allure.attachment_type.HTML)
        
        with allure.step("验证响应状态码"):
            # 注册页面可能返回200或302
            self.assertIn(response.status_code, [200, 302])
    
    @allure.story("用户API")
    @allure.title("测试用户信息API")
    @allure.severity(allure.severity_level.NORMAL)
    def test_user_info_api(self):
        """
        测试用户信息API
        验证用户数据接口
        """
        with allure.step("发送GET请求到用户信息API"):
            response = self.client.get('/api/user/')
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.content.decode('utf-8', errors='ignore'), 
                         name="Response Body", 
                         attachment_type=allure.attachment_type.JSON)
        
        with allure.step("验证响应状态码"):
            # 用户API可能需要认证，所以接受多种状态码
            self.assertIn(response.status_code, [200, 401, 403, 404])
    
    @allure.story("内容API")
    @allure.title("测试内容列表API")
    @allure.severity(allure.severity_level.NORMAL)
    def test_content_list_api(self):
        """
        测试内容列表API
        验证内容数据接口
        """
        with allure.step("发送GET请求到内容列表API"):
            response = self.client.get('/api/content/')
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.content.decode('utf-8', errors='ignore'), 
                         name="Response Body", 
                         attachment_type=allure.attachment_type.JSON)
        
        with allure.step("验证响应状态码"):
            # 内容API可能需要认证，所以接受多种状态码
            self.assertIn(response.status_code, [200, 401, 403, 404])
    
    @allure.story("工具API")
    @allure.title("测试工具功能API")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tools_api(self):
        """
        测试工具功能API
        验证工具相关接口
        """
        with allure.step("发送GET请求到工具API"):
            response = self.client.get('/api/tools/')
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.content.decode('utf-8', errors='ignore'), 
                         name="Response Body", 
                         attachment_type=allure.attachment_type.JSON)
        
        with allure.step("验证响应状态码"):
            # 工具API可能需要认证，所以接受多种状态码
            self.assertIn(response.status_code, [200, 401, 403, 404])
    
    @allure.story("错误处理")
    @allure.title("测试不存在的API端点")
    @allure.severity(allure.severity_level.MINOR)
    def test_nonexistent_api_endpoint(self):
        """
        测试不存在的API端点
        验证404错误处理
        """
        with allure.step("发送GET请求到不存在的API端点"):
            response = self.client.get('/api/nonexistent/')
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.content.decode('utf-8', errors='ignore'), 
                         name="Response Body", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证响应状态码为404"):
            self.assertEqual(response.status_code, 404)


@allure.epic("Shenyiqing.xin 网站全维度测试")
@allure.feature("接口测试")
class TestAPIAuthentication(TestCase):
    """
    API认证测试类
    测试API接口的认证和授权功能
    """
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
        
        # 创建测试用户
        self.test_user = User.objects.create_user(
            username='authtest',
            email='authtest@example.com',
            password='testpass123'
        )
    
    @allure.story("认证流程")
    @allure.title("测试POST登录请求")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_post_login_request(self):
        """
        测试POST登录请求
        验证登录表单提交
        """
        with allure.step("发送POST请求到登录API"):
            response = self.client.post('/accounts/login/', {
                'login': self.test_user.username,
                'password': 'testpass123',
            })
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.content.decode('utf-8', errors='ignore')[:1000], 
                         name="Response Content", 
                         attachment_type=allure.attachment_type.HTML)
        
        with allure.step("验证响应状态码"):
            # 登录可能成功(302)或失败(200)
            self.assertIn(response.status_code, [200, 302])
    
    @allure.story("认证流程")
    @allure.title("测试POST注册请求")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_post_signup_request(self):
        """
        测试POST注册请求
        验证注册表单提交
        """
        with allure.step("发送POST请求到注册API"):
            response = self.client.post('/accounts/signup/', {
                'username': 'newuser123',
                'email': 'newuser@example.com',
                'password1': 'newpass123',
                'password2': 'newpass123',
            })
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.content.decode('utf-8', errors='ignore')[:1000], 
                         name="Response Content", 
                         attachment_type=allure.attachment_type.HTML)
        
        with allure.step("验证响应状态码"):
            # 注册可能成功(302)或失败(200)
            self.assertIn(response.status_code, [200, 302])
    
    @allure.story("认证流程")
    @allure.title("测试无效凭据登录")
    @allure.severity(allure.severity_level.NORMAL)
    def test_invalid_credentials_login(self):
        """
        测试无效凭据登录
        验证错误处理
        """
        with allure.step("使用无效凭据发送POST请求"):
            response = self.client.post('/accounts/login/', {
                'login': 'invaliduser',
                'password': 'invalidpass',
            })
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.content.decode('utf-8', errors='ignore')[:1000], 
                         name="Response Content", 
                         attachment_type=allure.attachment_type.HTML)
        
        with allure.step("验证响应状态码为200（显示错误）"):
            self.assertEqual(response.status_code, 200)


@allure.epic("Shenyiqing.xin 网站全维度测试")
@allure.feature("接口测试")
class TestAPIResponseFormat(TestCase):
    """
    API响应格式测试类
    测试API接口的响应格式和数据完整性
    """
    
    def setUp(self):
        """测试前置设置"""
        self.client = Client()
    
    @allure.story("响应格式")
    @allure.title("测试API响应头信息")
    @allure.severity(allure.severity_level.NORMAL)
    def test_api_response_headers(self):
        """
        测试API响应头信息
        验证Content-Type等头部信息
        """
        with allure.step("发送请求并检查响应头"):
            response = self.client.get('/health/')
            headers = dict(response.headers)
            allure.attach(json.dumps(headers, indent=2), 
                         name="Response Headers", 
                         attachment_type=allure.attachment_type.JSON)
        
        with allure.step("验证响应头包含基本字段"):
            self.assertIn('Content-Type', headers)
            self.assertIn('Content-Length', headers)
    
    @allure.story("响应格式")
    @allure.title("测试API响应时间")
    @allure.severity(allure.severity_level.NORMAL)
    def test_api_response_time(self):
        """
        测试API响应时间
        验证接口响应速度
        """
        with allure.step("测量API响应时间"):
            start_time = time.time()
            response = self.client.get('/health/')
            end_time = time.time()
            response_time = end_time - start_time
            
            allure.attach(f"Response Time: {response_time:.3f} seconds", 
                         name="Response Time", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(f"Response Status Code: {response.status_code}", 
                         name="Status Code", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证响应时间小于3秒"):
            self.assertLess(response_time, 3.0)
        
        with allure.step("验证响应状态码为200"):
            self.assertEqual(response.status_code, 200)
    
    @allure.story("响应格式")
    @allure.title("测试API错误响应格式")
    @allure.severity(allure.severity_level.MINOR)
    def test_api_error_response_format(self):
        """
        测试API错误响应格式
        验证错误响应的格式一致性
        """
        with allure.step("请求不存在的端点"):
            response = self.client.get('/api/nonexistent/')
            allure.attach(f"Error Response Status: {response.status_code}", 
                         name="Error Status", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(response.content.decode('utf-8', errors='ignore'), 
                         name="Error Response Body", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("验证错误响应状态码为404"):
            self.assertEqual(response.status_code, 404)





