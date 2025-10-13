"""
最小化CI测试
确保基本功能正常工作
"""

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import connection
from django.test import TestCase

import pytest

User = get_user_model()


class TestBasicFunctionality(TestCase):
    """基本功能测试"""

    def setUp(self):
        """测试设置"""
        # 创建数据库表
        call_command("migrate", verbosity=0, interactive=False)

    def test_database_connection(self):
        """测试数据库连接"""
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            self.assertEqual(result[0], 1)

    def test_user_creation(self):
        """测试用户创建"""
        user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))

    def test_user_authentication(self):
        """测试用户认证"""
        user = User.objects.create_user(username="authuser", email="auth@example.com", password="authpass123")

        # 测试密码验证
        self.assertTrue(user.check_password("authpass123"))
        self.assertFalse(user.check_password("wrongpassword"))

    def test_user_update(self):
        """测试用户更新"""
        user = User.objects.create_user(username="updateuser", email="update@example.com", password="updatepass123")

        # 更新用户信息
        user.first_name = "Test"
        user.last_name = "User"
        user.save()

        # 验证更新
        updated_user = User.objects.get(id=user.id)
        self.assertEqual(updated_user.first_name, "Test")
        self.assertEqual(updated_user.last_name, "User")

    def test_user_deletion(self):
        """测试用户删除"""
        user = User.objects.create_user(username="deleteuser", email="delete@example.com", password="deletepass123")

        user_id = user.id
        user.delete()

        # 验证删除
        self.assertFalse(User.objects.filter(id=user_id).exists())

    def test_bulk_operations(self):
        """测试批量操作"""
        # 创建多个用户
        users = []
        for i in range(5):
            user = User.objects.create_user(username=f"bulkuser{i}", email=f"bulk{i}@example.com", password=f"bulkpass{i}")
            users.append(user)

        # 验证创建
        self.assertEqual(User.objects.count(), 5)

        # 批量更新
        User.objects.filter(username__startswith="bulkuser").update(is_active=False)

        # 验证更新
        inactive_users = User.objects.filter(is_active=False)
        self.assertEqual(inactive_users.count(), 5)

    def test_database_queries(self):
        """测试数据库查询"""
        # 创建测试数据
        User.objects.create_user(username="query1", email="query1@example.com", password="pass1")
        User.objects.create_user(username="query2", email="query2@example.com", password="pass2")
        User.objects.create_user(username="query3", email="query3@example.com", password="pass3")

        # 测试各种查询
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(User.objects.filter(username__startswith="query").count(), 3)
        self.assertEqual(User.objects.filter(email__contains="@example.com").count(), 3)

        # 测试排序
        users = User.objects.all().order_by("username")
        self.assertEqual(users[0].username, "query1")
        self.assertEqual(users[2].username, "query3")

    def test_database_transactions(self):
        """测试数据库事务"""
        initial_count = User.objects.count()

        # 测试事务回滚
        from django.db import transaction

        try:
            with transaction.atomic():
                User.objects.create_user(username="tx1", email="tx1@example.com", password="pass1")
                User.objects.create_user(username="tx2", email="tx2@example.com", password="pass2")
                # 故意引发异常
                raise Exception("Test rollback")
        except Exception:
            pass

        # 验证回滚
        self.assertEqual(User.objects.count(), initial_count)

        # 测试事务提交
        with transaction.atomic():
            User.objects.create_user(username="tx3", email="tx3@example.com", password="pass3")

        # 验证提交
        self.assertEqual(User.objects.count(), initial_count + 1)


class TestAPIBasic(TestCase):
    """基本API测试"""

    def setUp(self):
        """测试设置"""
        call_command("migrate", verbosity=0, interactive=False)
        self.user = User.objects.create_user(username="apiuser", email="api@example.com", password="apipass123")

    def test_api_health_check(self):
        """测试API健康检查"""
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)

    def test_api_root(self):
        """测试API根路径"""
        response = self.client.get("/api/")
        self.assertIn(response.status_code, [200, 404])  # 可能没有配置根路径

    def test_static_files(self):
        """测试静态文件"""
        response = self.client.get("/static/admin/css/base.css")
        self.assertIn(response.status_code, [200, 404])  # 可能没有收集静态文件


class TestModelBasics(TestCase):
    """基本模型测试"""

    def setUp(self):
        """测试设置"""
        call_command("migrate", verbosity=0, interactive=False)

    def test_user_model_fields(self):
        """测试用户模型字段"""
        user = User.objects.create_user(username="modeltest", email="model@example.com", password="modelpass123")

        # 测试基本字段
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, "modeltest")
        self.assertEqual(user.email, "model@example.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_user_string_representation(self):
        """测试用户字符串表示"""
        user = User.objects.create_user(username="stringtest", email="string@example.com", password="stringpass123")

        # 测试字符串表示
        self.assertEqual(str(user), "stringtest")
        self.assertEqual(user.get_username(), "stringtest")

    def test_user_permissions(self):
        """测试用户权限"""
        user = User.objects.create_user(
            username="permissiontest", email="permission@example.com", password="permissionpass123"
        )

        # 测试权限
        self.assertFalse(user.has_perm("auth.add_user"))
        self.assertFalse(user.has_perm("auth.change_user"))
        self.assertFalse(user.has_perm("auth.delete_user"))

        # 测试超级用户权限
        user.is_superuser = True
        user.save()
        self.assertTrue(user.has_perm("auth.add_user"))
        self.assertTrue(user.has_perm("auth.change_user"))
        self.assertTrue(user.has_perm("auth.delete_user"))
