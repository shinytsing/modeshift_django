from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from apps.tools.views.resume_3d_generator_views import parse_resume


class Resume3DGeneratorTests(SimpleTestCase):
    def test_parser_only_adds_city_present_in_work_entry(self):
        result = parse_resume("高杰\n2025.01 - 至今\n顺丰航空有限公司\n深圳\n测试开发工程师")
        self.assertEqual(result["jobs"][0]["location"], "深圳")
        self.assertEqual(result["jobs"][0]["mark"]["label"], "顺丰航空")

    def test_parser_does_not_invent_a_city(self):
        result = parse_resume("王小明\n奇安信科技集团股份有限公司 2024.01 - 至今\n测试工程师")
        self.assertIsNone(result["jobs"][0]["location"])
        self.assertEqual(result["jobs"][0]["mark"]["label"], "奇安信")

    def test_upload_rejects_unsupported_resume_format(self):
        upload = SimpleUploadedFile("resume.txt", b"resume", content_type="text/plain")
        response = self.client.post("/tools/resume-3d-generator/", {"resume": upload})
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "仅支持 PDF 或 DOCX", status_code=400)

    @patch("apps.tools.views.resume_3d_generator_views.extract_resume_text")
    def test_upload_renders_full_source_and_explicit_metadata(self, extract_text):
        extract_text.return_value = "高杰\n2025.01 - 至今\n奇安信科技集团股份有限公司\n上海\n测试工程师"
        upload = SimpleUploadedFile("resume.pdf", BytesIO(b"fake-pdf").getvalue(), content_type="application/pdf")
        response = self.client.post("/tools/resume-3d-generator/", {"resume": upload})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "奇安信科技集团股份有限公司")
        self.assertContains(response, "上海")
