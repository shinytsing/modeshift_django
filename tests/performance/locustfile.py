"""
Django网站性能测试 - Locust压力测试
项目：shenyiqing.xin
功能：使用Locust进行网站性能压力测试
"""

from locust import HttpUser, task, between
import random
import json


class WebsiteUser(HttpUser):
    """网站用户行为模拟"""
    wait_time = between(1, 3)  # 用户操作间隔1-3秒
    
    def on_start(self):
        """用户开始时的初始化操作"""
        self.login()
    
    def login(self):
        """模拟用户登录"""
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post('/login/', login_data)
        if response.status_code == 200:
            # 登录成功，保存会话
            self.session_cookies = response.cookies
        else:
            # 登录失败，使用匿名会话
            self.session_cookies = None
    
    @task(3)
    def visit_homepage(self):
        """访问首页 - 权重3"""
        response = self.client.get('/')
        assert response.status_code == 200
    
    @task(2)
    def visit_login_page(self):
        """访问登录页面 - 权重2"""
        response = self.client.get('/login/')
        assert response.status_code == 200
    
    @task(2)
    def visit_register_page(self):
        """访问注册页面 - 权重2"""
        response = self.client.get('/register/')
        assert response.status_code == 200
    
    @task(1)
    def visit_about_page(self):
        """访问关于页面 - 权重1"""
        response = self.client.get('/about/')
        assert response.status_code == 200
    
    @task(1)
    def visit_contact_page(self):
        """访问联系页面 - 权重1"""
        response = self.client.get('/contact/')
        assert response.status_code == 200
    
    @task(2)
    def submit_contact_form(self):
        """提交联系表单 - 权重2"""
        form_data = {
            'name': f'Test User {random.randint(1, 1000)}',
            'email': f'test{random.randint(1, 1000)}@example.com',
            'subject': 'Performance Test',
            'message': 'This is a performance test message'
        }
        
        response = self.client.post('/contact/', form_data)
        assert response.status_code in [200, 302]
    
    @task(1)
    def visit_dashboard(self):
        """访问仪表板 - 权重1"""
        if self.session_cookies:
            response = self.client.get('/dashboard/', cookies=self.session_cookies)
            assert response.status_code in [200, 302]
        else:
            # 未登录用户访问仪表板会被重定向
            response = self.client.get('/dashboard/')
            assert response.status_code == 302
    
    @task(1)
    def visit_profile(self):
        """访问个人资料 - 权重1"""
        if self.session_cookies:
            response = self.client.get('/profile/', cookies=self.session_cookies)
            assert response.status_code in [200, 302]
        else:
            response = self.client.get('/profile/')
            assert response.status_code == 302
    
    @task(1)
    def search_content(self):
        """搜索内容 - 权重1"""
        search_terms = ['test', 'django', 'python', 'web', 'development']
        search_term = random.choice(search_terms)
        
        response = self.client.get(f'/search/?q={search_term}')
        assert response.status_code == 200
    
    @task(1)
    def view_content_list(self):
        """查看内容列表 - 权重1"""
        response = self.client.get('/content/')
        assert response.status_code == 200
    
    @task(1)
    def view_content_detail(self):
        """查看内容详情 - 权重1"""
        # 假设有一些内容ID
        content_ids = [1, 2, 3, 4, 5]
        content_id = random.choice(content_ids)
        
        response = self.client.get(f'/content/{content_id}/')
        assert response.status_code in [200, 404]


class APIUser(HttpUser):
    """API用户行为模拟"""
    wait_time = between(0.5, 2)  # API调用间隔0.5-2秒
    
    def on_start(self):
        """API用户初始化"""
        self.token = self.get_auth_token()
    
    def get_auth_token(self):
        """获取认证token"""
        token_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post('/api/auth/token/', json=token_data)
        if response.status_code == 200:
            return response.json().get('access') or response.json().get('token')
        return None
    
    @task(3)
    def get_user_profile(self):
        """获取用户资料 - 权重3"""
        if self.token:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = self.client.get('/api/users/profile/', headers=headers)
            assert response.status_code in [200, 401]
        else:
            response = self.client.get('/api/users/profile/')
            assert response.status_code == 401
    
    @task(2)
    def get_content_list(self):
        """获取内容列表 - 权重2"""
        if self.token:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = self.client.get('/api/content/', headers=headers)
            assert response.status_code in [200, 401]
        else:
            response = self.client.get('/api/content/')
            assert response.status_code == 401
    
    @task(2)
    def create_content(self):
        """创建内容 - 权重2"""
        if self.token:
            headers = {'Authorization': f'Bearer {self.token}'}
            content_data = {
                'title': f'Performance Test Article {random.randint(1, 1000)}',
                'content': 'This is a performance test article content',
                'category': 'general',
                'status': 'draft'
            }
            response = self.client.post('/api/content/', json=content_data, headers=headers)
            assert response.status_code in [200, 201, 400, 401]
        else:
            response = self.client.post('/api/content/', json={})
            assert response.status_code == 401
    
    @task(1)
    def search_content(self):
        """搜索内容 - 权重1"""
        if self.token:
            headers = {'Authorization': f'Bearer {self.token}'}
            search_terms = ['test', 'django', 'python', 'web']
            search_term = random.choice(search_terms)
            response = self.client.get(f'/api/content/search/?q={search_term}', headers=headers)
            assert response.status_code in [200, 401]
        else:
            response = self.client.get('/api/content/search/?q=test')
            assert response.status_code == 401
    
    @task(1)
    def get_content_detail(self):
        """获取内容详情 - 权重1"""
        if self.token:
            headers = {'Authorization': f'Bearer {self.token}'}
            content_ids = [1, 2, 3, 4, 5]
            content_id = random.choice(content_ids)
            response = self.client.get(f'/api/content/{content_id}/', headers=headers)
            assert response.status_code in [200, 401, 404]
        else:
            response = self.client.get('/api/content/1/')
            assert response.status_code == 401
    
    @task(1)
    def update_content(self):
        """更新内容 - 权重1"""
        if self.token:
            headers = {'Authorization': f'Bearer {self.token}'}
            content_ids = [1, 2, 3, 4, 5]
            content_id = random.choice(content_ids)
            update_data = {
                'title': f'Updated Article {random.randint(1, 1000)}',
                'content': 'This is updated content',
                'status': 'published'
            }
            response = self.client.put(f'/api/content/{content_id}/', json=update_data, headers=headers)
            assert response.status_code in [200, 400, 401, 404]
        else:
            response = self.client.put('/api/content/1/', json={})
            assert response.status_code == 401
    
    @task(1)
    def delete_content(self):
        """删除内容 - 权重1"""
        if self.token:
            headers = {'Authorization': f'Bearer {self.token}'}
            content_ids = [1, 2, 3, 4, 5]
            content_id = random.choice(content_ids)
            response = self.client.delete(f'/api/content/{content_id}/', headers=headers)
            assert response.status_code in [200, 204, 401, 404]
        else:
            response = self.client.delete('/api/content/1/')
            assert response.status_code == 401


class AdminUser(HttpUser):
    """管理员用户行为模拟"""
    wait_time = between(2, 5)  # 管理员操作间隔2-5秒
    
    def on_start(self):
        """管理员初始化"""
        self.login()
    
    def login(self):
        """管理员登录"""
        login_data = {
            'username': 'admin',
            'password': 'adminpass123'
        }
        
        response = self.client.post('/admin/login/', login_data)
        if response.status_code == 200:
            self.session_cookies = response.cookies
        else:
            self.session_cookies = None
    
    @task(2)
    def visit_admin_dashboard(self):
        """访问管理员面板 - 权重2"""
        if self.session_cookies:
            response = self.client.get('/admin/', cookies=self.session_cookies)
            assert response.status_code == 200
        else:
            response = self.client.get('/admin/')
            assert response.status_code == 200
    
    @task(1)
    def manage_users(self):
        """管理用户 - 权重1"""
        if self.session_cookies:
            response = self.client.get('/admin/auth/user/', cookies=self.session_cookies)
            assert response.status_code == 200
        else:
            response = self.client.get('/admin/auth/user/')
            assert response.status_code == 302
    
    @task(1)
    def manage_content(self):
        """管理内容 - 权重1"""
        if self.session_cookies:
            response = self.client.get('/admin/content/', cookies=self.session_cookies)
            assert response.status_code in [200, 404]
        else:
            response = self.client.get('/admin/content/')
            assert response.status_code == 302
    
    @task(1)
    def view_analytics(self):
        """查看分析数据 - 权重1"""
        if self.session_cookies:
            response = self.client.get('/admin/analytics/', cookies=self.session_cookies)
            assert response.status_code in [200, 404]
        else:
            response = self.client.get('/admin/analytics/')
            assert response.status_code == 302
    
    @task(1)
    def view_logs(self):
        """查看日志 - 权重1"""
        if self.session_cookies:
            response = self.client.get('/admin/logs/', cookies=self.session_cookies)
            assert response.status_code in [200, 404]
        else:
            response = self.client.get('/admin/logs/')
            assert response.status_code == 302


class MobileUser(HttpUser):
    """移动端用户行为模拟"""
    wait_time = between(1, 4)  # 移动端操作间隔1-4秒
    
    def on_start(self):
        """移动端用户初始化"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        }
    
    @task(3)
    def visit_mobile_homepage(self):
        """访问移动端首页 - 权重3"""
        response = self.client.get('/', headers=self.headers)
        assert response.status_code == 200
    
    @task(2)
    def mobile_login(self):
        """移动端登录 - 权重2"""
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post('/login/', login_data, headers=self.headers)
        assert response.status_code in [200, 302]
    
    @task(1)
    def mobile_search(self):
        """移动端搜索 - 权重1"""
        search_terms = ['mobile', 'app', 'responsive', 'design']
        search_term = random.choice(search_terms)
        
        response = self.client.get(f'/search/?q={search_term}', headers=self.headers)
        assert response.status_code == 200
    
    @task(1)
    def mobile_content_view(self):
        """移动端内容查看 - 权重1"""
        content_ids = [1, 2, 3, 4, 5]
        content_id = random.choice(content_ids)
        
        response = self.client.get(f'/content/{content_id}/', headers=self.headers)
        assert response.status_code in [200, 404]
    
    @task(1)
    def mobile_form_submit(self):
        """移动端表单提交 - 权重1"""
        form_data = {
            'name': f'Mobile User {random.randint(1, 1000)}',
            'email': f'mobile{random.randint(1, 1000)}@example.com',
            'message': 'Mobile performance test message'
        }
        
        response = self.client.post('/contact/', form_data, headers=self.headers)
        assert response.status_code in [200, 302]


class HighLoadUser(HttpUser):
    """高负载用户行为模拟"""
    wait_time = between(0.1, 0.5)  # 高负载用户操作间隔0.1-0.5秒
    
    @task(5)
    def rapid_page_requests(self):
        """快速页面请求 - 权重5"""
        pages = ['/', '/login/', '/register/', '/about/', '/contact/']
        page = random.choice(pages)
        
        response = self.client.get(page)
        assert response.status_code == 200
    
    @task(3)
    def rapid_api_calls(self):
        """快速API调用 - 权重3"""
        response = self.client.get('/api/auth/status/')
        assert response.status_code in [200, 401]
    
    @task(2)
    def rapid_form_submissions(self):
        """快速表单提交 - 权重2"""
        form_data = {
            'name': f'Load Test User {random.randint(1, 10000)}',
            'email': f'load{random.randint(1, 10000)}@example.com',
            'message': 'High load test message'
        }
        
        response = self.client.post('/contact/', form_data)
        assert response.status_code in [200, 302]
    
    @task(1)
    def rapid_search_queries(self):
        """快速搜索查询 - 权重1"""
        search_terms = ['load', 'test', 'performance', 'stress', 'concurrent']
        search_term = random.choice(search_terms)
        
        response = self.client.get(f'/search/?q={search_term}')
        assert response.status_code == 200