from django.test import TestCase

from apps.tools.models.rag_models import RequirementDocument
from apps.tools.services.rag_service import sync_site_capabilities
from apps.tools.services.site_capability_catalog import build_site_capability_cards


class SiteCapabilityCatalogTests(TestCase):
    def test_catalog_contains_real_page_and_api_evidence(self):
        cards = {card["route"]: card for card in build_site_capability_cards()}

        diary = cards["/tools/api/diary/quick-save/"]["content"]
        self.assertIn("apps/tools/views/simple_diary_views.py", diary)
        self.assertIn("HTTP 方法", diary)
        self.assertIn("视图源码中的写操作调用", diary)

        bmi = cards["/tools/fitness/tools/bmi-calculator/"]["content"]
        self.assertIn("BMI计算器页面", bmi)
        self.assertIn("不可据此推断其他方法可用", bmi)

    def test_sync_is_granular_and_idempotent(self):
        sync_site_capabilities()
        first_count = RequirementDocument.objects.filter(owner=None).count()
        first_auto_count = RequirementDocument.objects.filter(owner=None, source_type="catalog").count()
        self.assertGreaterEqual(first_auto_count, 500)
        self.assertTrue(
            RequirementDocument.objects.filter(
                owner=None,
                title__startswith="ModeShift / 生活模式 / 生活日记 / API 快速保存日记",
            ).exists()
        )

        sync_site_capabilities()
        self.assertEqual(RequirementDocument.objects.filter(owner=None).count(), first_count)
        self.assertEqual(RequirementDocument.objects.filter(owner=None, source_type="catalog").count(), first_auto_count)
