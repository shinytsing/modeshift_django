"""
增强批改服务
结合OCR和AI，确保：
1. 准确的OCR识别和位置信息
2. 准确的AI判题
3. 完整的文件生成
"""
import os
import logging
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


class EnhancedGradingService:
    """增强批改服务 - 结合OCR和AI"""

    def __init__(self):
        """初始化增强批改服务"""
        from .ocr_service import OCRService
        from .subject_grading_service import SubjectGradingService

        self.ocr_service = OCRService()
        self.subject_service = None  # 延迟初始化

    def grade_homework_with_marking(
        self,
        image_path: str,
        subject: str = 'chinese'
    ) -> Dict[str, Any]:
        """
        批改作业并生成标记图片

        Args:
            image_path: 作业图片路径
            subject: 学科代码

        Returns:
            完整的批改结果，包含位置信息
        """
        logger.info(f"开始增强批改: {image_path}, 学科: {subject}")

        # 步骤1: OCR识别，获取文字和位置
        logger.info("步骤1: OCR识别...")
        ocr_results = self.ocr_service.process_file(image_path)

        if not ocr_results:
            raise ValueError("OCR识别失败，未提取到任何题目")

        logger.info(f"OCR识别完成，提取到{len(ocr_results)}道题目")

        # 步骤2: AI批改，结合OCR结果
        logger.info("步骤2: AI批改...")
        from .subject_grading_service import SubjectGradingService
        subject_service = SubjectGradingService(subject=subject)

        if not subject_service.is_available():
            raise ValueError(f"{subject}批改服务不可用")

        # 使用AI批改（传入OCR结果作为上下文）
        ai_result = subject_service.grade_homework(image_path)

        # 步骤3: 合并OCR位置信息和AI批改结果
        logger.info("步骤3: 合并OCR位置信息和AI批改结果...")
        enhanced_questions = self._merge_ocr_and_ai_results(ocr_results, ai_result['questions'])

        # 步骤4: 生成标记图片
        logger.info("步骤4: 生成标记图片...")
        from .image_marking_service import ImageMarkingService
        marking_service = ImageMarkingService()

        # 准备标记数据
        marking_data = []
        for q in enhanced_questions:
            marking_data.append({
                'question_number': q['question_number'],
                'is_correct': q['is_correct'],
                'bbox': q.get('bbox'),
                'region': q.get('region')
            })

        marked_image_path = marking_service.mark_image(
            image_path=image_path,
            questions=marking_data,
            output_path=None
        )

        # 步骤5: 生成错题再练卷
        logger.info("步骤5: 生成错题再练卷...")
        wrong_questions = [q for q in enhanced_questions if not q['is_correct']]

        result = {
            'subject': subject,
            'total_score': ai_result.get('total_score', 0),
            'max_score': ai_result.get('max_score', 100),
            'questions': enhanced_questions,
            'marked_image_path': marked_image_path,
            'wrong_questions': wrong_questions,
            'grading_engine': ai_result.get('grading_engine', '')
        }

        logger.info(f"✅ 增强批改完成: {len(enhanced_questions)}道题目，{len(wrong_questions)}道错题")

        return result

    def _merge_ocr_and_ai_results(
        self,
        ocr_results: List[Dict[str, Any]],
        ai_questions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        合并OCR结果和AI批改结果

        Args:
            ocr_results: OCR识别结果（包含位置信息）
            ai_questions: AI批改结果（包含判题信息）

        Returns:
            合并后的题目列表
        """
        enhanced_questions = []

        # 创建OCR结果索引（按题号）
        ocr_by_number = {q.get('question_number', 0): q for q in ocr_results}

        # 合并结果
        for ai_q in ai_questions:
            question_number = ai_q.get('question_number', 0)
            ocr_q = ocr_by_number.get(question_number)

            # 合并数据（包含知识点）
            enhanced_q = {
                'question_number': question_number,
                'question_type': ai_q.get('question_type', ocr_q.get('question_type', 'subjective') if ocr_q else 'subjective'),
                'question_stem': ai_q.get('question_stem', ocr_q.get('question_stem', '') if ocr_q else ''),
                'student_answer': ai_q.get('student_answer', ocr_q.get('student_answer', '') if ocr_q else ''),
                'correct_answer': ai_q.get('correct_answer', ''),
                'score': ai_q.get('score', 0),
                'max_score': ai_q.get('max_score', 10),
                'is_correct': ai_q.get('is_correct', False),
                'feedback': ai_q.get('feedback', ''),
                'analysis': ai_q.get('feedback', ''),  # 兼容字段
                'knowledge_point': ai_q.get('knowledge_point', ''),  # 知识点
            }

            # 添加位置信息（从OCR结果）
            if ocr_q:
                if 'bbox' in ocr_q:
                    enhanced_q['bbox'] = ocr_q['bbox']
                if 'region' in ocr_q:
                    enhanced_q['region'] = ocr_q['region']

            enhanced_questions.append(enhanced_q)

        # 如果OCR识别到但AI没批改的题目，也添加进去
        ai_numbers = {q.get('question_number', 0) for q in ai_questions}
        for ocr_q in ocr_results:
            if ocr_q.get('question_number', 0) not in ai_numbers:
                enhanced_q = {
                    'question_number': ocr_q.get('question_number', 0),
                    'question_type': ocr_q.get('question_type', 'subjective'),
                    'question_stem': ocr_q.get('question_stem', ''),
                    'student_answer': ocr_q.get('student_answer', ''),
                    'correct_answer': '',
                    'score': 0,
                    'max_score': 10,
                    'is_correct': False,
                    'feedback': 'AI未识别到此题',
                    'analysis': 'AI未识别到此题',
                }
                if 'bbox' in ocr_q:
                    enhanced_q['bbox'] = ocr_q['bbox']
                if 'region' in ocr_q:
                    enhanced_q['region'] = ocr_q['region']
                enhanced_questions.append(enhanced_q)

        return enhanced_questions
