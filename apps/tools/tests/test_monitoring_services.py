from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class ServiceStatusEndpointTests(TestCase):
    def test_anonymous_user_cannot_read_service_status(self):
        response = self.client.get("/tools/monitoring/services/")

        self.assertEqual(response.status_code, 302)

    def test_non_staff_user_cannot_read_service_status(self):
        user = User.objects.create_user(username="service-user", password="secret")
        self.client.force_login(user)

        response = self.client.get("/tools/monitoring/services/")

        self.assertEqual(response.status_code, 302)

    def test_staff_user_receives_safe_service_status_rows(self):
        user = User.objects.create_user(username="service-admin", password="secret", is_staff=True)
        self.client.force_login(user)

        with patch("apps.tools.monitoring_views._check_celery") as celery, patch(
            "apps.tools.monitoring_views._check_mcp"
        ) as mcp:
            celery.return_value = {
                "key": "scheduler",
                "name": "定时任务 Worker",
                "status": "up",
                "message": "Worker 已响应",
                "kind": "runtime",
            }
            mcp.return_value = {
                "key": "xiaohongshu_mcp",
                "name": "小红书 MCP",
                "status": "up",
                "message": "健康检查通过",
                "kind": "integration",
            }
            response = self.client.get("/tools/monitoring/services/")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["summary"]["total"], len(body["services"]))
        self.assertEqual({"key", "name", "status", "message", "kind"}, set(body["services"][0]))
        self.assertNotIn("token", response.content.decode().lower())

