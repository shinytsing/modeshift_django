"""
作业批改系统单元测试
"""
import os
import tempfile
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock

from .models import HomeworkSubmission, QuestionResult, GeneratedPaper
from .services import OCRService, GraderService, QuestionBankService, ExportService


class OCRServiceTest(TestCase):
    """OCR服务测试"""

    def setUp(self):
        self.ocr_service = OCRService()

    def test_detect_question_type_choice(self):
        """测试选择题识别"""
        question_stem = "1. 下列哪个是Python的特点？\nA. 编译型\nB. 解释型\nC. 汇编\nD. 机器码"
        question_type = self.ocr_service._detect_question_type(question_stem)
        self.assertEqual(question_type, 'choice')

    def test_detect_question_type_fill(self):
        """测试填空题识别"""
        question_stem = "Python中的列表使用___符号表示。"
        question_type = self.ocr_service._detect_question_type(question_stem)
        self.assertEqual(question_type, 'fill')

    def test_detect_question_type_subjective(self):
        """测试主观题识别"""
        question_stem = "请简述Python的特点。"
        question_type = self.ocr_service._detect_question_type(question_stem)
        self.assertEqual(question_type, 'subjective')

    def test_parse_ocr_text(self):
        """测试OCR文本解析"""
        text = """1. 下列哪个是Python的特点？
A. 编译型
B. 解释型
答案：B

2. Python中的列表使用___符号表示。
答案：[]"""

        questions = self.ocr_service._parse_ocr_text(text)
        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0]['question_number'], 1)
        self.assertEqual(questions[0]['student_answer'], 'B')
        self.assertEqual(questions[1]['question_number'], 2)
        self.assertEqual(questions[1]['student_answer'], '[]')


class GraderServiceTest(TestCase):
    """批改服务测试"""

    def setUp(self):
        self.grader_service = GraderService()

    def test_grade_choice_correct(self):
        """测试选择题批改 - 正确"""
        result = self.grader_service.grade_question(
            question_type='choice',
            student_answer='B',
            correct_answer='B',
            max_score=10.0
        )
        self.assertTrue(result['is_correct'])
        self.assertEqual(result['score'], 10.0)

    def test_grade_choice_wrong(self):
        """测试选择题批改 - 错误"""
        result = self.grader_service.grade_question(
            question_type='choice',
            student_answer='A',
            correct_answer='B',
            max_score=10.0
        )
        self.assertFalse(result['is_correct'])
        self.assertEqual(result['score'], 0.0)

    def test_grade_fill_numeric(self):
        """测试填空题批改 - 数值"""
        result = self.grader_service.grade_question(
            question_type='fill',
            student_answer='3.14',
            correct_answer='3.14',
            max_score=10.0
        )
        self.assertTrue(result['is_correct'])
        self.assertEqual(result['score'], 10.0)

    def test_grade_fill_text(self):
        """测试填空题批改 - 文本"""
        result = self.grader_service.grade_question(
            question_type='fill',
            student_answer='[]',
            correct_answer='[]',
            max_score=10.0
        )
        self.assertTrue(result['is_correct'])
        self.assertEqual(result['score'], 10.0)

    def test_normalize_choice_answer(self):
        """测试选择题答案标准化"""
        self.assertEqual(self.grader_service._normalize_choice_answer('  A  '), 'A')
        self.assertEqual(self.grader_service._normalize_choice_answer('b'), 'B')
        self.assertEqual(self.grader_service._normalize_choice_answer('A B C'), 'ABC')

    def test_compare_numeric(self):
        """测试数值比较"""
        self.assertTrue(self.grader_service._compare_numeric('3.14', '3.14'))
        self.assertTrue(self.grader_service._compare_numeric('3.14', '3.1400'))
        self.assertFalse(self.grader_service._compare_numeric('3.14', '3.15'))
        self.assertIsNone(self.grader_service._compare_numeric('abc', '3.14'))


class QuestionBankServiceTest(TestCase):
    """题库服务测试"""

    def setUp(self):
        self.question_bank_service = QuestionBankService()

    @patch('requests.post')
    def test_match_question_success(self, mock_post):
        """测试题目匹配 - 成功"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': {
                'id': 'q001',
                'question_stem': '测试题干',
                'answer': 'B'
            }
        }
        mock_post.return_value = mock_response

        result = self.question_bank_service.match_question('测试题干')
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], 'q001')

    @patch('requests.post')
    def test_match_question_not_found(self, mock_post):
        """测试题目匹配 - 未找到"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': False,
            'data': None
        }
        mock_post.return_value = mock_response

        result = self.question_bank_service.match_question('不存在的题干')
        self.assertIsNone(result)


class ExportServiceTest(TestCase):
    """导出服务测试"""

    def setUp(self):
        self.export_service = ExportService()

    def test_wrap_text(self):
        """测试文本换行"""
        text = "这是一段很长的文本，需要进行自动换行处理，以适应PDF页面的宽度限制。"
        lines = self.export_service._wrap_text(text, 200, 12)
        self.assertGreater(len(lines), 1)

    def test_export_to_pdf(self):
        """测试PDF导出"""
        paper_data = {
            'title': '测试试卷',
            'questions': [
                {
                    'number': 1,
                    'stem': '测试题目1',
                    'type': 'choice',
                    'answer': 'A',
                    'show_answer': False
                }
            ]
        }

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            output_path = tmp.name

        try:
            result = self.export_service.export_to_pdf(paper_data, output_path)
            self.assertTrue(os.path.exists(result))
            self.assertGreater(os.path.getsize(result), 0)
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)


class HomeworkSubmissionAPITest(TestCase):
    """作业提交API测试"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_upload_homework(self):
        """测试作业上传"""
        # 创建测试文件
        test_file = SimpleUploadedFile(
            "test_homework.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )

        response = self.client.post('/api/grading/submissions/upload/', {
            'file': test_file
        })

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('task_id', data)
        self.assertIn('submission_id', data)

    def test_upload_invalid_file(self):
        """测试上传无效文件"""
        test_file = SimpleUploadedFile(
            "test.txt",
            b"text content",
            content_type="text/plain"
        )

        response = self.client.post('/api/grading/submissions/upload/', {
            'file': test_file
        })

        self.assertEqual(response.status_code, 400)

    def test_get_result_without_task_id(self):
        """测试获取结果 - 缺少task_id"""
        response = self.client.get('/api/grading/submissions/result/')
        self.assertEqual(response.status_code, 400)


class HomeworkSubmissionModelTest(TestCase):
    """作业提交模型测试"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_create_submission(self):
        """测试创建提交记录"""
        submission = HomeworkSubmission.objects.create(
            user=self.user,
            file='test.jpg',
            file_type='image',
            task_id='test-task-123',
            status='pending'
        )

        self.assertEqual(submission.user, self.user)
        self.assertEqual(submission.status, 'pending')
        self.assertFalse(submission.ocr_completed)
        self.assertFalse(submission.matching_completed)
        self.assertFalse(submission.grading_completed)

    def test_create_question_result(self):
        """测试创建题目结果"""
        submission = HomeworkSubmission.objects.create(
            user=self.user,
            file='test.jpg',
            file_type='image',
            task_id='test-task-123'
        )

        question = QuestionResult.objects.create(
            submission=submission,
            question_number=1,
            question_type='choice',
            ocr_text='测试题目',
            question_stem='测试题干',
            correct_answer='A',
            student_answer='B'
        )

        self.assertEqual(question.submission, submission)
        self.assertEqual(question.question_number, 1)
        self.assertEqual(question.question_type, 'choice')
