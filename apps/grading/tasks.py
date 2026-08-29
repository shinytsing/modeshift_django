"""
作业批改Celery异步任务
"""
import logging
from typing import Dict, Any, List
from celery import shared_task
from django.utils import timezone
from django.core.files.base import File

from .models import HomeworkSubmission, QuestionResult, SimilarQuestion
from .services import OCRService, GraderService, QuestionBankService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_homework_task(self, submission_id: int) -> Dict[str, Any]:
    """
    处理作业批改的完整流程

    Args:
        submission_id: 作业提交ID

    Returns:
        处理结果
    """
    try:
        # 获取提交记录
        submission = HomeworkSubmission.objects.get(id=submission_id)
        submission.status = 'ocr_processing'
        submission.save()

        # 步骤1: OCR识别
        logger.info(f"开始OCR识别: {submission.task_id}")
        ocr_service = OCRService()
        ocr_results = ocr_service.process_file(submission.file.path)

        if not ocr_results:
            raise Exception("OCR识别失败，未提取到题目")

        submission.ocr_completed = True
        submission.status = 'matching'
        submission.save()

        # 步骤2: 题目匹配
        logger.info(f"开始题目匹配: {submission.task_id}")
        question_bank_service = QuestionBankService()
        matched_questions = []

        for ocr_result in ocr_results:
            # 匹配题库中的题目
            matched = question_bank_service.match_question(
                question_stem=ocr_result['question_stem'],
                question_type=ocr_result['question_type']
            )

            if matched:
                ocr_result['question_bank_id'] = matched.get('id', '')
                ocr_result['correct_answer'] = matched.get('answer', '')
                ocr_result['question_stem'] = matched.get('question_stem', ocr_result['question_stem'])

            matched_questions.append(ocr_result)

        submission.matching_completed = True
        submission.status = 'grading'
        submission.save()

        # 步骤3: 批改题目
        logger.info(f"开始批改: {submission.task_id}")
        grader_service = GraderService()
        total_score = 0.0
        total_max_score = 0.0
        wrong_question_ids = []

        for question_data in matched_questions:
            # 创建题目结果记录
            question_result = QuestionResult.objects.create(
                submission=submission,
                question_number=question_data['question_number'],
                question_type=question_data['question_type'],
                ocr_text=question_data['ocr_text'],
                ocr_confidence=question_data.get('ocr_confidence', 0.0),
                question_bank_id=question_data.get('question_bank_id', ''),
                question_stem=question_data['question_stem'],
                student_answer=question_data.get('student_answer', ''),
                correct_answer=question_data.get('correct_answer', '')
            )

            # 批改题目
            if question_data.get('correct_answer'):
                grading_result = grader_service.grade_question(
                    question_type=question_data['question_type'],
                    student_answer=question_data.get('student_answer', ''),
                    correct_answer=question_data['correct_answer'],
                    question_stem=question_data['question_stem'],
                    max_score=question_result.max_score
                )

                # 更新批改结果
                question_result.is_correct = grading_result['is_correct']
                question_result.score = grading_result['score']
                question_result.feedback = grading_result['feedback']
                question_result.llm_analysis = grading_result.get('llm_analysis')
                question_result.save()

                total_score += grading_result['score']
                total_max_score += question_result.max_score

                # 记录错题
                if not grading_result['is_correct']:
                    wrong_question_ids.append(question_result.id)
            else:
                logger.warning(f"题目{question_data['question_number']}未匹配到答案，跳过批改")
                total_max_score += question_result.max_score

        submission.grading_completed = True
        submission.total_score = total_score
        submission.max_score = total_max_score
        submission.save()

        # 步骤4: 查找相似题
        logger.info(f"开始查找相似题: {submission.task_id}")
        if wrong_question_ids:
            find_similar_questions_task.delay(submission_id, wrong_question_ids)

        # 完成
        submission.status = 'completed'
        submission.completed_at = timezone.now()
        submission.save()

        logger.info(f"作业批改完成: {submission.task_id}, 得分: {total_score}/{total_max_score}")

        return {
            'success': True,
            'submission_id': submission_id,
            'task_id': submission.task_id,
            'total_score': total_score,
            'max_score': total_max_score,
            'questions_count': len(matched_questions),
            'wrong_count': len(wrong_question_ids)
        }

    except HomeworkSubmission.DoesNotExist:
        logger.error(f"作业提交不存在: {submission_id}")
        return {'success': False, 'error': '作业提交不存在'}

    except Exception as e:
        logger.error(f"作业批改失败: {str(e)}", exc_info=True)

        # 更新失败状态
        try:
            submission = HomeworkSubmission.objects.get(id=submission_id)
            submission.status = 'failed'
            submission.error_message = str(e)
            submission.save()
        except:
            pass

        # 重试
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60)

        return {'success': False, 'error': str(e)}


@shared_task
def find_similar_questions_task(submission_id: int, wrong_question_ids: List[int]) -> Dict[str, Any]:
    """
    查找错题的相似题目

    Args:
        submission_id: 作业提交ID
        wrong_question_ids: 错题ID列表

    Returns:
        处理结果
    """
    try:
        question_bank_service = QuestionBankService()
        similar_count = 0

        for question_id in wrong_question_ids:
            try:
                question_result = QuestionResult.objects.get(id=question_id)

                # 查找相似题
                similar_questions = question_bank_service.find_similar_questions(
                    question_id=question_result.question_bank_id,
                    question_stem=question_result.question_stem,
                    limit=3
                )

                # 保存相似题
                for similar in similar_questions:
                    SimilarQuestion.objects.create(
                        question_result=question_result,
                        question_bank_id=similar.get('id', ''),
                        question_stem=similar.get('question_stem', ''),
                        question_type=similar.get('question_type', ''),
                        answer=similar.get('answer', ''),
                        difficulty=similar.get('difficulty', ''),
                        knowledge_points=similar.get('knowledge_points', []),
                        similarity_score=similar.get('similarity_score', 0.0)
                    )
                    similar_count += 1

                logger.info(f"为题目{question_id}找到{len(similar_questions)}道相似题")

            except QuestionResult.DoesNotExist:
                logger.warning(f"题目结果不存在: {question_id}")
                continue
            except Exception as e:
                logger.error(f"查找相似题失败: {question_id}, {str(e)}")
                continue

        logger.info(f"相似题查找完成，共找到{similar_count}道相似题")

        return {
            'success': True,
            'submission_id': submission_id,
            'similar_count': similar_count
        }

    except Exception as e:
        logger.error(f"相似题查找任务失败: {str(e)}", exc_info=True)
        return {'success': False, 'error': str(e)}


@shared_task
def generate_paper_task(paper_id: int) -> Dict[str, Any]:
    """
    生成试卷文件（PDF和JPG）

    Args:
        paper_id: 试卷ID

    Returns:
        处理结果
    """
    try:
        from .models import GeneratedPaper
        from .services import ExportService
        from django.conf import settings
        import os

        paper = GeneratedPaper.objects.get(id=paper_id)
        export_service = ExportService()

        # 准备输出路径
        output_dir = os.path.join(settings.MEDIA_ROOT, 'papers', str(paper.user.id))
        os.makedirs(output_dir, exist_ok=True)

        pdf_filename = f'paper_{paper.id}.pdf'
        pdf_path = os.path.join(output_dir, pdf_filename)

        # 导出PDF
        logger.info(f"开始导出PDF: {paper_id}")
        export_service.export_to_pdf(paper.paper_data, pdf_path)

        # 保存PDF文件路径
        paper.pdf_file = os.path.join('papers', str(paper.user.id), pdf_filename)

        # 导出JPG
        logger.info(f"开始导出JPG: {paper_id}")
        jpg_dir = os.path.join(output_dir, f'paper_{paper.id}_jpg')
        jpg_files = export_service.export_to_jpg(paper.paper_data, jpg_dir)

        # 保存JPG文件路径（相对路径）
        relative_jpg_files = [
            os.path.join('papers', str(paper.user.id), f'paper_{paper.id}_jpg', os.path.basename(f))
            for f in jpg_files
        ]
        paper.jpg_files = relative_jpg_files
        paper.save()

        logger.info(f"试卷生成完成: {paper_id}")

        return {
            'success': True,
            'paper_id': paper_id,
            'pdf_file': paper.pdf_file.url if paper.pdf_file else '',
            'jpg_files': [os.path.join(settings.MEDIA_URL, f) for f in relative_jpg_files]
        }

    except Exception as e:
        logger.error(f"试卷生成失败: {str(e)}", exc_info=True)
        return {'success': False, 'error': str(e)}
