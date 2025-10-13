# 🧪 QAToolBox 项目完整测试指南

## 📋 目录
- [项目概述](#项目概述)
- [测试环境准备](#测试环境准备)
- [测试类型和策略](#测试类型和策略)
- [功能模块测试](#功能模块测试)
- [API接口测试](#api接口测试)
- [数据库测试](#数据库测试)
- [前端测试](#前端测试)
- [性能测试](#性能测试)
- [安全测试](#安全测试)
- [部署测试](#部署测试)
- [测试自动化](#测试自动化)
- [测试报告](#测试报告)

## 🎯 项目概述

QAToolBox是一个基于Django的多功能工具箱项目，包含以下核心模块：

### 主要应用模块
- **apps/users** - 用户管理和认证系统
- **apps/tools** - 核心工具功能（1384个URL路由）
- **apps/content** - 内容管理系统
- **apps/share** - 分享功能模块

### 核心功能领域
- 🔐 用户认证和权限管理
- 🛠️ 工具集合（健身、音乐、AI、代理等）
- 💼 AI找工作系统
- 🎵 吉他训练系统
- 🏃 健身和营养管理
- 🌐 代理和网络工具
- 💬 聊天和社交功能
- 📊 数据分析和监控

## 🚀 测试环境准备

### 1. 环境要求
```bash
# Python版本
Python 3.8+

# 数据库
PostgreSQL 12+

# 依赖包
pip install -r requirements.txt
```

### 2. 测试数据库配置
```python
# config/settings/testing.py
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "test_modeshift_django",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

### 3. 测试环境启动
```bash
# 激活虚拟环境
source activate_env.sh

# 运行数据库迁移
python manage.py migrate --settings=config.settings.testing

# 创建测试用户
python manage.py set_admin --settings=config.settings.testing

# 启动测试服务器
python manage.py runserver --settings=config.settings.testing
```

## 🧪 测试类型和策略

### 1. 单元测试 (Unit Tests)
- **位置**: `tests/unit/`
- **覆盖**: 模型、视图、服务层
- **工具**: pytest + Django TestCase

### 2. 集成测试 (Integration Tests)
- **位置**: `tests/integration/`
- **覆盖**: API端点、数据库交互
- **工具**: pytest + APIClient

### 3. 端到端测试 (E2E Tests)
- **位置**: `tests/e2e/`
- **覆盖**: 完整用户流程
- **工具**: Playwright

### 4. 性能测试 (Performance Tests)
- **工具**: Locust, Django Debug Toolbar
- **指标**: 响应时间、并发处理能力

## 🔧 功能模块测试

### 1. 用户管理模块 (apps/users)

#### 测试用例
```python
# 用户注册测试
def test_user_registration():
    """测试用户注册流程"""
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password1': 'testpass123',
        'password2': 'testpass123'
    }
    response = client.post('/users/register/', data)
    assert response.status_code == 302  # 重定向

# 用户登录测试
def test_user_login():
    """测试用户登录"""
    user = User.objects.create_user(
        username='testuser',
        password='testpass123'
    )
    response = client.post('/users/login/', {
        'username': 'testuser',
        'password': 'testpass123'
    })
    assert response.status_code == 302

# 用户权限测试
def test_user_permissions():
    """测试用户权限控制"""
    user = User.objects.create_user(username='testuser')
    response = client.get('/tools/')
    assert response.status_code == 302  # 重定向到登录页
```

#### API测试
```python
# 用户API测试
def test_user_profile_api():
    """测试用户资料API"""
    client.force_authenticate(user=user)
    response = client.get('/api/users/profile/')
    assert response.status_code == 200
    assert 'username' in response.data
```

### 2. 工具模块 (apps/tools)

#### 核心功能测试

##### A. 健身工具测试
```python
def test_bmi_calculator():
    """测试BMI计算器"""
    data = {'height': 175, 'weight': 70}
    response = client.post('/api/fitness/bmi/', data)
    assert response.status_code == 200
    assert 'bmi' in response.data

def test_workout_tracker():
    """测试运动记录"""
    data = {
        'exercise_type': '跑步',
        'duration': 30,
        'calories_burned': 300
    }
    response = client.post('/api/fitness/workout/save/', data)
    assert response.status_code == 200
```

##### B. AI找工作系统测试
```python
def test_job_search_start():
    """测试AI找工作启动"""
    data = {
        'job_title': 'Python开发工程师',
        'location': '北京',
        'experience': '3-5年'
    }
    response = client.post('/job-search/api/start/', data)
    assert response.status_code == 200

def test_boss_login():
    """测试Boss直聘登录"""
    response = client.post('/job-search/api/boss-login/')
    assert response.status_code == 200
```

##### C. 吉他训练系统测试
```python
def test_guitar_practice():
    """测试吉他练习记录"""
    data = {
        'practice_type': '和弦练习',
        'difficulty': '初级',
        'duration': 30
    }
    response = client.post('/api/guitar/start-practice/', data)
    assert response.status_code == 200

def test_tab_generation():
    """测试自动扒谱"""
    audio_file = SimpleUploadedFile("test.mp3", b"fake audio content")
    response = client.post('/api/guitar/upload-audio/', {'audio': audio_file})
    assert response.status_code == 200
```

##### D. 代理系统测试
```python
def test_proxy_setup():
    """测试代理设置"""
    data = {
        'proxy_type': 'clash',
        'server_url': 'http://example.com'
    }
    response = client.post('/api/proxy/setup/', data)
    assert response.status_code == 200

def test_ip_comparison():
    """测试IP对比功能"""
    response = client.get('/api/proxy/ip-comparison/')
    assert response.status_code == 200
    assert 'local_ip' in response.data
```

### 3. 内容管理模块 (apps/content)

#### 测试用例
```python
def test_article_crud():
    """测试文章CRUD操作"""
    # 创建文章
    data = {
        'title': '测试文章',
        'content': '这是测试内容',
        'status': 'published'
    }
    response = client.post('/content/create/', data)
    assert response.status_code == 302

    # 查看文章
    article = Article.objects.first()
    response = client.get(f'/content/{article.pk}/')
    assert response.status_code == 200

    # 编辑文章
    data['title'] = '更新后的标题'
    response = client.post(f'/content/edit/{article.pk}/', data)
    assert response.status_code == 302

    # 删除文章
    response = client.post(f'/content/delete/{article.pk}/')
    assert response.status_code == 302
```

## 🌐 API接口测试

### 1. RESTful API测试

#### 认证API
```python
class TestAuthenticationAPI:
    def test_login_api(self):
        """测试登录API"""
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = client.post('/api/users/login/', data)
        assert response.status_code == 200
        assert 'token' in response.data or 'sessionid' in response.cookies

    def test_logout_api(self):
        """测试注销API"""
        client.force_authenticate(user=user)
        response = client.post('/api/users/logout/')
        assert response.status_code == 200
```

#### 工具API
```python
class TestToolsAPI:
    def test_test_case_generator(self):
        """测试测试用例生成API"""
        data = {
            'function_name': 'test_function',
            'parameters': ['param1', 'param2'],
            'expected_output': 'expected result'
        }
        response = client.post('/api/generate-testcases/', data)
        assert response.status_code == 200

    def test_pdf_converter(self):
        """测试PDF转换API"""
        pdf_file = SimpleUploadedFile("test.pdf", b"fake pdf content")
        response = client.post('/api/pdf-converter/', {'file': pdf_file})
        assert response.status_code == 200
```

### 2. WebSocket测试

#### 聊天功能测试
```python
def test_chat_websocket():
    """测试聊天WebSocket连接"""
    # 创建WebSocket连接
    communicator = WebsocketCommunicator(application, "/ws/chat/test_room/")
    connected, subprotocol = await communicator.connect()
    assert connected

    # 发送消息
    await communicator.send_json_to({
        "type": "chat_message",
        "message": "Hello World",
        "user": "testuser"
    })

    # 接收消息
    response = await communicator.receive_json_from()
    assert response["type"] == "chat_message"
    assert response["message"] == "Hello World"

    await communicator.disconnect()
```

## 🗄️ 数据库测试

### 1. 模型测试
```python
class TestModels:
    def test_user_model(self):
        """测试用户模型"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.is_active == True

    def test_tool_usage_log(self):
        """测试工具使用日志"""
        log = ToolUsageLog.objects.create(
            user=user,
            tool_type='TEST_CASE',
            input_data='test input',
            output_file='test.txt'
        )
        assert log.success == True
        assert log.created_at is not None

    def test_fitness_record(self):
        """测试健身记录"""
        record = FitnessRecord.objects.create(
            user=user,
            exercise_type='跑步',
            duration=30,
            calories_burned=300
        )
        assert record.exercise_type == '跑步'
        assert record.duration == 30
```

### 2. 数据库约束测试
```python
def test_unique_constraints():
    """测试唯一约束"""
    User.objects.create_user(username='testuser')
    
    with pytest.raises(IntegrityError):
        User.objects.create_user(username='testuser')

def test_foreign_key_constraints():
    """测试外键约束"""
    with pytest.raises(IntegrityError):
        ToolUsageLog.objects.create(
            user_id=999,  # 不存在的用户ID
            tool_type='TEST_CASE'
        )
```

### 3. 数据库迁移测试
```bash
# 测试数据库迁移
python manage.py migrate --settings=config.settings.testing --dry-run

# 测试迁移回滚
python manage.py migrate apps.tools 0001 --settings=config.settings.testing
python manage.py migrate apps.tools --settings=config.settings.testing
```

## 🎨 前端测试

### 1. 模板测试
```python
def test_templates():
    """测试模板渲染"""
    response = client.get('/tools/')
    assert response.status_code == 200
    assert 'QAToolBox' in response.content.decode()
    
    # 测试登录后的模板
    client.force_login(user)
    response = client.get('/tools/')
    assert '欢迎' in response.content.decode()
```

### 2. 静态文件测试
```python
def test_static_files():
    """测试静态文件"""
    response = client.get('/static/css/main.css')
    assert response.status_code == 200
    
    response = client.get('/static/js/main.js')
    assert response.status_code == 200
```

### 3. JavaScript测试
```javascript
// 前端JavaScript测试示例
describe('QAToolBox Frontend', function() {
    it('should load main page', function() {
        cy.visit('/tools/');
        cy.contains('QAToolBox').should('be.visible');
    });
    
    it('should handle user login', function() {
        cy.visit('/users/login/');
        cy.get('[name="username"]').type('testuser');
        cy.get('[name="password"]').type('testpass123');
        cy.get('[type="submit"]').click();
        cy.url().should('include', '/tools/');
    });
});
```

## ⚡ 性能测试

### 1. 响应时间测试
```python
def test_response_times():
    """测试API响应时间"""
    start_time = time.time()
    response = client.get('/api/fitness/bmi/')
    end_time = time.time()
    
    response_time = end_time - start_time
    assert response_time < 1.0  # 响应时间应小于1秒
    assert response.status_code == 200
```

### 2. 并发测试
```python
import threading
import time

def test_concurrent_requests():
    """测试并发请求处理"""
    results = []
    
    def make_request():
        response = client.get('/api/fitness/bmi/')
        results.append(response.status_code)
    
    # 创建10个并发线程
    threads = []
    for i in range(10):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    # 验证所有请求都成功
    assert all(status == 200 for status in results)
    assert len(results) == 10
```

### 3. 数据库性能测试
```python
def test_database_performance():
    """测试数据库查询性能"""
    # 创建大量测试数据
    users = []
    for i in range(1000):
        user = User.objects.create_user(
            username=f'user{i}',
            email=f'user{i}@example.com'
        )
        users.append(user)
    
    # 测试查询性能
    start_time = time.time()
    User.objects.filter(username__startswith='user').count()
    end_time = time.time()
    
    query_time = end_time - start_time
    assert query_time < 0.1  # 查询时间应小于100ms
```

## 🔒 安全测试

### 1. 认证安全测试
```python
def test_authentication_security():
    """测试认证安全性"""
    # 测试密码强度
    weak_passwords = ['123', 'password', '123456']
    for password in weak_passwords:
        with pytest.raises(ValidationError):
            User.objects.create_user(
                username='testuser',
                password=password
            )
    
    # 测试会话安全
    response = client.post('/users/login/', {
        'username': 'testuser',
        'password': 'testpass123'
    })
    assert 'sessionid' in response.cookies
    assert response.cookies['sessionid'].get('httponly') == True
```

### 2. 权限控制测试
```python
def test_permission_control():
    """测试权限控制"""
    # 未登录用户访问受保护资源
    response = client.get('/tools/')
    assert response.status_code == 302  # 重定向到登录页
    
    # 普通用户访问管理员功能
    client.force_login(user)
    response = client.get('/admin/')
    assert response.status_code == 302  # 重定向
```

### 3. 输入验证测试
```python
def test_input_validation():
    """测试输入验证"""
    # SQL注入测试
    malicious_input = "'; DROP TABLE users; --"
    response = client.post('/api/fitness/bmi/', {
        'height': malicious_input,
        'weight': 70
    })
    assert response.status_code == 400  # 应该返回错误
    
    # XSS测试
    xss_input = "<script>alert('XSS')</script>"
    response = client.post('/api/fitness/bmi/', {
        'height': 175,
        'weight': xss_input
    })
    assert response.status_code == 400
```

## 🚀 部署测试

### 1. Docker部署测试
```bash
# 构建Docker镜像
docker build -t qatoolbox:test .

# 运行Docker容器
docker run -d -p 8000:8000 --name qatoolbox-test qatoolbox:test

# 测试容器健康状态
curl http://localhost:8000/health/

# 清理测试容器
docker stop qatoolbox-test
docker rm qatoolbox-test
```

### 2. 生产环境测试
```bash
# 使用生产环境设置
export DJANGO_SETTINGS_MODULE=config.settings.production

# 运行生产环境测试
python manage.py test --settings=config.settings.production

# 测试静态文件收集
python manage.py collectstatic --noinput

# 测试数据库迁移
python manage.py migrate --dry-run
```

### 3. CI/CD流程测试
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python manage.py test --settings=config.settings.testing
```

## 🤖 测试自动化

### 1. 自动化测试脚本
```bash
#!/bin/bash
# run_tests.sh - 自动化测试脚本

echo "🧪 开始运行QAToolBox测试套件..."

# 设置环境变量
export DJANGO_SETTINGS_MODULE=config.settings.testing

# 清理测试数据库
echo "🗄️ 清理测试数据库..."
python manage.py flush --noinput

# 运行数据库迁移
echo "📊 运行数据库迁移..."
python manage.py migrate --noinput

# 运行单元测试
echo "🔬 运行单元测试..."
python manage.py test tests.unit --verbosity=2

# 运行集成测试
echo "🔗 运行集成测试..."
python manage.py test tests.integration --verbosity=2

# 运行端到端测试
echo "🌐 运行端到端测试..."
pytest tests/e2e/ --browser chromium

# 生成测试报告
echo "📊 生成测试报告..."
coverage run --source='.' manage.py test
coverage report
coverage html

echo "✅ 测试完成！"
```

### 2. 测试数据管理
```python
# tests/fixtures.py
import factory
from django.contrib.auth.models import User
from apps.tools.models import ToolUsageLog

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    is_active = True

class ToolUsageLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ToolUsageLog
    
    user = factory.SubFactory(UserFactory)
    tool_type = factory.Iterator(['TEST_CASE', 'PDF_CONVERTER', 'BMI_CALCULATOR'])
    input_data = factory.Faker('text', max_nb_chars=200)
    output_file = factory.Faker('file_name', extension='txt')
```

### 3. 测试监控和报告
```python
# tests/conftest.py
import pytest
from django.test import Client
from django.contrib.auth.models import User

@pytest.fixture
def client():
    """测试客户端"""
    return Client()

@pytest.fixture
def user():
    """测试用户"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def authenticated_client(user):
    """已认证的测试客户端"""
    client = Client()
    client.force_login(user)
    return client
```

## 📊 测试报告

### 1. 测试覆盖率报告
```bash
# 安装coverage
pip install coverage

# 运行测试并生成覆盖率报告
coverage run --source='.' manage.py test
coverage report
coverage html

# 查看HTML报告
open htmlcov/index.html
```

### 2. 性能测试报告
```python
# 性能测试报告生成
import time
import json
from django.test import TestCase

class PerformanceTestReport(TestCase):
    def generate_performance_report(self):
        """生成性能测试报告"""
        endpoints = [
            '/api/fitness/bmi/',
            '/api/fitness/heart-rate/',
            '/api/fitness/calories/',
            '/job-search/api/start/',
            '/api/guitar/start-practice/',
        ]
        
        results = {}
        for endpoint in endpoints:
            start_time = time.time()
            response = self.client.get(endpoint)
            end_time = time.time()
            
            results[endpoint] = {
                'status_code': response.status_code,
                'response_time': end_time - start_time,
                'timestamp': time.time()
            }
        
        # 保存报告
        with open('performance_report.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
```

### 3. 测试结果汇总
```python
# 测试结果汇总脚本
def generate_test_summary():
    """生成测试结果汇总"""
    summary = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'skipped_tests': 0,
        'coverage_percentage': 0,
        'performance_score': 0,
        'security_score': 0
    }
    
    # 这里可以集成pytest、coverage等工具的结果
    # 生成综合测试报告
    
    return summary
```

## 🎯 测试最佳实践

### 1. 测试命名规范
```python
# 好的测试命名
def test_user_registration_with_valid_data_should_create_user():
    """测试使用有效数据注册用户应该创建用户"""
    pass

def test_bmi_calculator_with_invalid_height_should_return_error():
    """测试BMI计算器使用无效身高应该返回错误"""
    pass

# 避免的命名
def test1():
    """测试1"""
    pass

def test_user():
    """测试用户"""
    pass
```

### 2. 测试数据管理
```python
# 使用工厂模式创建测试数据
def test_tool_usage_log():
    user = UserFactory()
    log = ToolUsageLogFactory(user=user)
    assert log.user == user

# 避免硬编码测试数据
def test_tool_usage_log():
    user = User.objects.create_user(
        username='testuser123',
        email='test@example.com'
    )
    # ...
```

### 3. 测试隔离
```python
# 每个测试都应该独立
class TestUserManagement(TestCase):
    def setUp(self):
        """每个测试前的设置"""
        self.user = UserFactory()
        self.client = Client()
    
    def tearDown(self):
        """每个测试后的清理"""
        User.objects.all().delete()
    
    def test_user_login(self):
        """测试用户登录"""
        # 测试逻辑
        pass
    
    def test_user_logout(self):
        """测试用户注销"""
        # 测试逻辑
        pass
```

## 📝 测试检查清单

### 功能测试检查清单
- [ ] 用户注册和登录
- [ ] 用户权限控制
- [ ] 工具功能完整性
- [ ] API接口正确性
- [ ] 数据库操作
- [ ] 文件上传下载
- [ ] 搜索功能
- [ ] 分页功能
- [ ] 排序功能
- [ ] 过滤功能

### 性能测试检查清单
- [ ] 页面加载时间 < 3秒
- [ ] API响应时间 < 1秒
- [ ] 数据库查询优化
- [ ] 并发用户处理
- [ ] 内存使用情况
- [ ] CPU使用情况
- [ ] 磁盘I/O性能

### 安全测试检查清单
- [ ] SQL注入防护
- [ ] XSS攻击防护
- [ ] CSRF保护
- [ ] 文件上传安全
- [ ] 密码强度验证
- [ ] 会话管理
- [ ] 权限控制
- [ ] 数据加密

### 兼容性测试检查清单
- [ ] 浏览器兼容性
- [ ] 移动端适配
- [ ] 不同操作系统
- [ ] 不同屏幕分辨率
- [ ] 不同网络环境
- [ ] 不同设备类型

## 🚨 常见问题和解决方案

### 1. 测试数据库问题
```python
# 问题：测试数据库连接失败
# 解决方案：检查数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_modeshift_django',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 2. 测试数据清理问题
```python
# 问题：测试数据污染
# 解决方案：使用事务回滚
@pytest.mark.django_db(transaction=True)
def test_with_transaction():
    # 测试代码
    pass
```

### 3. 异步测试问题
```python
# 问题：异步代码测试
# 解决方案：使用pytest-asyncio
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

## 📞 联系和支持

如果在测试过程中遇到问题，请：

1. 查看项目文档
2. 检查测试日志
3. 参考错误信息
4. 联系开发团队

---

**最后更新**: 2024年12月29日  
**版本**: 1.0  
**维护者**: QAToolBox开发团队
