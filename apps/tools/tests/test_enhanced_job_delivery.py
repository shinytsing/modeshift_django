import tempfile
import time
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.tools.models import CookieSession, JobSearchRequest
from apps.tools.services.enhanced_job_delivery_service import EnhancedJobDeliveryService
from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
from apps.tools.views.enhanced_job_search_views import (
    BOSS_QR_TTL_SECONDS,
    _PLAYWRIGHT_QR_CONTEXTS,
    _playwright_qr_state,
    _load_boss_storage_state,
    _persist_boss_storage_state,
)


class EnhancedBossDeliveryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="boss-user", password="secret")
        self.service = EnhancedJobDeliveryService()

    def test_platform_info_exposes_only_boss(self):
        result = self.service.get_platform_info()

        self.assertTrue(result["success"])
        self.assertEqual(set(result["platforms"]), {"boss"})

    def test_start_rejects_non_boss_platform_without_creating_task(self):
        client = Client()
        client.force_login(self.user)

        response = client.post(
            reverse("tools:start_enhanced_job_search_api"),
            data={
                "platforms": ["liepin"],
                "keywords": ["Python"],
                "cities": ["北京"],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertEqual(JobSearchRequest.objects.count(), 0)

    def test_start_requires_csrf_for_browser_post_requests(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)

        response = client.post(
            reverse("tools:start_enhanced_job_search_api"),
            data={"platforms": ["boss"], "keywords": ["Python"], "cities": ["北京"]},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(JobSearchRequest.objects.count(), 0)

    def test_start_persists_boss_search_request_before_scheduling(self):
        config = self.service.create_search_config(
            {
                "keywords": ["Python", "Django"],
                "cities": ["北京"],
                "expected_salary": [15, 25],
                "max_applications": 8,
                "interval": 4,
            }
        )

        with patch.object(self.service, "_schedule_delivery") as schedule:
            result = self.service.start_boss_delivery(config, self.user)

        self.assertTrue(result["success"])
        request = JobSearchRequest.objects.get(pk=result["task_id"])
        self.assertEqual(request.status, "processing")
        self.assertEqual(request.keywords, ["Python", "Django"])
        self.assertEqual(request.max_applications, 8)
        schedule.assert_called_once_with(request.pk)

    def test_status_and_stop_are_read_from_database_across_service_instances(self):
        request = JobSearchRequest.objects.create(
            user=self.user,
            job_title="Python",
            location="北京",
            min_salary=15,
            max_salary=25,
            keywords=["Python"],
            status="processing",
            max_applications=5,
            application_interval=3,
        )

        fresh_service = EnhancedJobDeliveryService()
        status = fresh_service.get_delivery_status(self.user)
        self.assertEqual(status["task_id"], str(request.pk))
        self.assertEqual(status["status"], "processing")

        stopped = EnhancedJobDeliveryService().stop_delivery(self.user)
        self.assertTrue(stopped["success"])
        request.refresh_from_db()
        self.assertEqual(request.status, "cancelled")

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_boss_storage_state_is_saved_to_cookie_session_and_reloaded(self):
        storage_state = {
            "cookies": [{"name": "wt2", "value": "saved-cookie", "domain": ".zhipin.com", "path": "/"}],
            "origins": [],
        }

        _persist_boss_storage_state(self.user.id, storage_state, "qr-test")

        saved = CookieSession.objects.get(user=self.user, platform="boss")
        self.assertEqual(saved.get_storage_state(), storage_state)
        self.assertEqual(_load_boss_storage_state(self.user.id), storage_state)

    def test_confirmed_qr_poll_persists_the_live_browser_state(self):
        storage_state = {"cookies": [{"name": "wt2", "value": "confirmed-cookie"}], "origins": []}
        class FakeResponse:
            ok = True
            status = 200

            def __init__(self, payload=None, body=b"qr"):
                self.payload = payload or {}
                self._body = body

            def json(self):
                return self.payload

            def body(self):
                return self._body

        class FakeRequest:
            def get(self, url, **kwargs):
                if url.endswith("/qrcode/scan"):
                    return FakeResponse({"scaned": True})
                return FakeResponse({"code": 0, "zpData": {"userId": 1}})

            def post(self, url, **kwargs):
                return FakeResponse({"zpData": {"qrId": "qr-confirmed"}})

        fake_context = type(
            "FakeContext",
            (),
            {
                "storage_state": lambda self: storage_state,
                "close": lambda self: None,
                "request": FakeRequest(),
            },
        )()
        live_session = {
            "context": fake_context,
            "browser": fake_context,
            "playwright": fake_context,
            "qr_id": "qr-confirmed",
            "created_at": time.time(),
        }

        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            with patch.dict(_PLAYWRIGHT_QR_CONTEXTS, {self.user.id: live_session}, clear=True):
                state, _ = _playwright_qr_state(self.user.id)

            self.assertEqual(state, "confirmed")
            self.assertEqual(CookieSession.objects.get(user=self.user, platform="boss").get_storage_state(), storage_state)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_delivery_browser_reads_the_same_persisted_state_file_as_qr_login(self):
        class FakePage:
            def set_viewport_size(self, size):
                self.viewport = size

        class FakeContext:
            def new_page(self):
                return FakePage()

        class FakeBrowser:
            def __init__(self):
                self.storage_state = None

            def new_context(self, storage_state=None):
                self.storage_state = storage_state
                return FakeContext()

        class FakeChromium:
            def __init__(self, browser):
                self.browser = browser

            def launch(self, **kwargs):
                return self.browser

        class FakePlaywright:
            def __init__(self, browser):
                self.chromium = FakeChromium(browser)

            def start(self):
                return self

            def stop(self):
                pass

        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            state_dir = f"{media_root}/boss_sessions/user_{self.user.id}"
            import os
            os.makedirs(state_dir)
            state_file = f"{state_dir}/storage_state.json"
            with open(state_file, "w", encoding="utf-8") as handle:
                handle.write('{"cookies": [], "origins": []}')

            fake_browser = FakeBrowser()
            fake_playwright = FakePlaywright(fake_browser)
            service = BossZhipinPlaywrightService(headless=True, anti_detection=False)
            service._user_id = self.user.id
            with patch("apps.tools.services.boss_zhipin_playwright.sync_playwright", return_value=fake_playwright), \
                    patch("apps.tools.services.boss_zhipin_playwright.proxy_pool.get_random_proxy", return_value=None):
                self.assertTrue(service._init_browser())

            self.assertEqual(fake_browser.storage_state, state_file)

    def test_expired_qr_session_is_closed_after_ten_seconds(self):
        class FakeResponse:
            ok = True

            def json(self):
                return {"scaned": False}

        class FakeObject:
            request = type("FakeRequest", (), {"get": lambda self, *args, **kwargs: FakeResponse()})()

            def close(self):
                pass

            def stop(self):
                pass

        live_session = {
            "context": FakeObject(),
            "browser": FakeObject(),
            "playwright": FakeObject(),
            "qr_id": "qr-expired",
            "created_at": time.time() - BOSS_QR_TTL_SECONDS - 1,
        }

        with patch.dict(_PLAYWRIGHT_QR_CONTEXTS, {self.user.id: live_session}, clear=True):
            state, payload = _playwright_qr_state(self.user.id)

        self.assertEqual(state, "expired")
        self.assertIn("10 秒", payload["message"])
        self.assertNotIn(self.user.id, _PLAYWRIGHT_QR_CONTEXTS)
