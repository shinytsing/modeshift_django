"""
作业批改API视图
"""
import logging
import uuid
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.files import File
from typing import List, Dict, Any

from .models import HomeworkSubmission, QuestionResult, GeneratedPaper
from .serializers import (
    HomeworkSubmissionSerializer,
    HomeworkUploadSerializer,
    QuestionResultSerializer,
    GeneratedPaperSerializer,
    GeneratePaperRequestSerializer
)
# 导入服务类用于同步处理
from .services.ocr_service import OCRService
from .services.grader_service import GraderService
from .services.question_bank_service import QuestionBankService
from .services.export_service import ExportService
from .services.gemini_grading_service import GeminiGradingService
from .services.subject_grading_service import SubjectGradingService
from .services.image_marking_service import ImageMarkingService

logger = logging.getLogger(__name__)


class HomeworkSubmissionViewSet(viewsets.ModelViewSet):
    """作业提交视图集"""
    queryset = HomeworkSubmission.objects.all()
    serializer_class = HomeworkSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """只返回当前用户的作业"""
        return self.queryset.filter(user=self.request.user)

    def _extract_student_answer(self, question_text):
        """
        从题目文本中提取学生答案
        简单实现：查找"答案："后面的内容
        """
        import re

        # 匹配"答案："或"答："后面的内容
        patterns = [
            r'答案[：:]\s*([^\n]+)',
            r'答[：:]\s*([^\n]+)',
            r'学生答案[：:]\s*([^\n]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, question_text)
            if match:
                return match.group(1).strip()

        # 如果没有找到，返回空字符串
        return ''

    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        上传作业文件

        POST /api/homework/upload
        body: { file: image/pdf, student_id }
        返回: { task_id, submission_id }
        """
        serializer = HomeworkUploadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'success': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 获取上传的文件和学科
            uploaded_file = serializer.validated_data['file']
            subject = request.data.get('subject', 'chinese')  # 默认语文

            # 验证学科
            valid_subjects = ['chinese', 'math', 'english', 'physics', 'chemistry']
            if subject not in valid_subjects:
                subject = 'chinese'

            logger.info(f"上传作业 - 学科: {subject}")

            # 确定文件类型
            content_type = uploaded_file.content_type
            if 'image' in content_type:
                file_type = 'image'
            elif 'pdf' in content_type:
                file_type = 'pdf'
            else:
                return Response(
                    {'success': False, 'error': '不支持的文件类型'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 生成任务ID
            task_id = str(uuid.uuid4())

            # 创建提交记录
            submission = HomeworkSubmission.objects.create(
                user=request.user,
                file=uploaded_file,
                file_type=file_type,
                task_id=task_id,
                status='processing'
            )

            logger.info(f"作业上传成功: {task_id}, 用户: {request.user.username}")

            # 同步处理作业
            try:
                submission.status = 'processing'
                submission.save()

                # 使用增强批改服务（结合OCR和AI）
                from .services.enhanced_grading_service import EnhancedGradingService
                enhanced_service = EnhancedGradingService()

                try:
                    logger.info(f"🌟 使用增强批改服务批改{subject}作业")

                    # 增强批改：OCR识别 + AI批改 + 图片标记
                    enhanced_result = enhanced_service.grade_homework_with_marking(
                        image_path=submission.file.path,
                        subject=subject
                    )

                    # 保存批改结果
                    submission.ocr_result = {
                        'subject': subject,
                        'grading_engine': enhanced_result.get('grading_engine', ''),
                        'questions': enhanced_result['questions']
                    }
                    submission.ocr_completed = True
                    submission.matching_completed = True
                    submission.grading_completed = True

                    total_score = enhanced_result['total_score']
                    max_score = enhanced_result['max_score']

                    # 保存每道题的结果（包含知识点）
                    for q_data in enhanced_result['questions']:
                        question_result = QuestionResult.objects.create(
                            submission=submission,
                            question_number=q_data['question_number'],
                            question_stem=q_data['question_stem'],
                            question_type=q_data['question_type'],
                            student_answer=q_data['student_answer'],
                            correct_answer=q_data['correct_answer'],
                            score=q_data['score'],
                            max_score=q_data['max_score'],
                            is_correct=q_data['is_correct'],
                            feedback=q_data.get('feedback', q_data.get('analysis', ''))
                        )

                        # 保存知识点（如果有knowledge_point字段）
                        if q_data.get('knowledge_point'):
                            # 如果QuestionResult模型有knowledge_point字段，保存它
                            if hasattr(question_result, 'knowledge_point'):
                                question_result.knowledge_point = q_data['knowledge_point']
                                question_result.save()

                        logger.info(f"批改题目{q_data['question_number']}: {q_data['score']}/{q_data['max_score']}")

                        # 如果答错，查找相似题
                        if not q_data['is_correct']:
                            question_bank_service = QuestionBankService()
                            knowledge_point = q_data.get('knowledge_point', q_data['question_stem'][:20])
                            similar_questions = question_bank_service.find_similar_questions(
                                question_stem=q_data['question_stem'],
                                limit=5
                            )

                            for similar in similar_questions:
                                from .models import SimilarQuestion
                                SimilarQuestion.objects.create(
                                    question_result=question_result,
                                    question_bank_id=similar.get('id', ''),
                                    question_stem=similar.get('question_stem', ''),
                                    question_type=similar.get('question_type', ''),
                                    answer=similar.get('answer', ''),
                                    similarity_score=0.8
                                )

                    submission.total_score = total_score
                    submission.max_score = max_score
                    submission.status = 'completed'

                    # 保存标记后的图片
                    if enhanced_result.get('marked_image_path'):
                        from django.core.files import File
                        with open(enhanced_result['marked_image_path'], 'rb') as f:
                            file_name = os.path.basename(enhanced_result['marked_image_path'])
                            submission.marked_image.save(file_name, File(f), save=False)
                        logger.info(f"✅ 图片标记完成: {enhanced_result['marked_image_path']}")

                    # 生成批改结果PDF（题目+解析列表）
                    try:
                        from .services.grading_result_export_service import GradingResultExportService
                        result_export_service = GradingResultExportService()

                        result_pdf_dir = os.path.join(settings.MEDIA_ROOT, 'grading_results', 'pdf')
                        os.makedirs(result_pdf_dir, exist_ok=True)
                        result_pdf_path = os.path.join(result_pdf_dir, f'grading_result_{submission.id}.pdf')

                        result_export_service.export_grading_result_pdf(
                            questions=enhanced_result['questions'],
                            total_score=total_score,
                            max_score=max_score,
                            output_path=result_pdf_path
                        )

                        # 保存到submission（可以添加新字段或使用现有字段）
                        submission.grading_result_pdf_path = result_pdf_path
                        logger.info(f"✅ 批改结果PDF生成完成: {result_pdf_path}")
                    except Exception as pdf_error:
                        logger.warning(f"生成批改结果PDF失败: {str(pdf_error)}")

                    # 生成错题再练卷（改进版：根据知识点筛选）
                    wrong_questions = enhanced_result.get('wrong_questions', [])
                    if wrong_questions:
                        logger.info(f"开始生成错题再练卷，错题数: {len(wrong_questions)}")
                        try:
                            self._generate_practice_paper_enhanced(submission, wrong_questions)
                        except Exception as paper_error:
                            logger.warning(f"生成错题再练卷失败: {str(paper_error)}")

                    submission.save()

                    logger.info(f"✅ {subject}作业批改完成: {task_id}, 得分: {total_score}/{max_score}")

                    return Response({
                        'success': True,
                        'task_id': task_id,
                        'submission_id': submission.id,
                        'message': f'作业批改完成（{enhanced_result.get("grading_engine", subject)}）',
                        'score': f'{total_score}/{max_score}',
                        'subject': subject,
                        'grading_engine': enhanced_result.get('grading_engine', '')
                    }, status=status.HTTP_201_CREATED)

                except Exception as enhanced_error:
                    logger.warning(f"增强批改失败，降级到传统方案: {str(enhanced_error)}")
                    # 降级到传统方案

                # 传统方案：OCR + LLM批改
                logger.info("使用传统OCR+LLM方案")
                ocr_service = OCRService()
                ocr_questions = ocr_service.process_file(submission.file.path)

                # 保存OCR结果
                submission.ocr_result = {'questions': ocr_questions}
                submission.ocr_completed = True
                submission.save()

                logger.info(f"OCR识别完成: {task_id}, 识别到{len(ocr_questions)}个题目")

                # 2. 题目匹配和批改
                grader_service = GraderService()
                question_bank_service = QuestionBankService()

                total_score = 0
                max_score = 0

                # 处理每个识别出的题目
                for ocr_question in ocr_questions:
                    question_number = ocr_question.get('question_number', 0)
                    question_stem = ocr_question.get('question_stem', '')
                    student_answer = ocr_question.get('student_answer', '')
                    question_type = ocr_question.get('question_type', 'subjective')

                    if not question_stem:
                        continue

                    # 匹配题库获取正确答案
                    question_info = question_bank_service.match_question(
                        question_stem,
                        question_type
                    )

                    if question_info:
                        correct_answer = question_info['answer']

                        # 批改
                        grading_result = grader_service.grade_question(
                            question_type=question_type,
                            student_answer=student_answer,
                            correct_answer=correct_answer,
                            question_stem=question_stem
                        )

                        # 保存结果
                        question_result = QuestionResult.objects.create(
                            submission=submission,
                            question_number=question_number,
                            question_stem=question_stem,
                            question_type=question_type,
                            student_answer=student_answer,
                            correct_answer=correct_answer,
                            score=grading_result['score'],
                            max_score=grading_result['max_score'],
                            is_correct=grading_result['is_correct'],
                            feedback=grading_result['feedback']
                        )

                        total_score += grading_result['score']
                        max_score += grading_result['max_score']

                        logger.info(f"题目{question_number}批改完成: {grading_result['score']}/{grading_result['max_score']}")

                        # 如果答错，查找相似题
                        if not grading_result['is_correct']:
                            similar_questions = question_bank_service.find_similar_questions(
                                question_id=question_info.get('id', ''),
                                question_stem=question_stem,
                                limit=3
                            )

                            for similar in similar_questions:
                                from .models import SimilarQuestion
                                SimilarQuestion.objects.create(
                                    question_result=question_result,
                                    question_bank_id=similar.get('id', ''),
                                    question_stem=similar.get('question_stem', ''),
                                    question_type=similar.get('question_type', ''),
                                    answer=similar.get('answer', ''),
                                    similarity_score=0.8
                                )

                submission.matching_completed = True
                submission.grading_completed = True
                submission.total_score = total_score
                submission.max_score = max_score
                submission.status = 'completed'
                submission.save()

                logger.info(f"作业批改完成: {task_id}, 得分: {total_score}/{max_score}")

            except Exception as e:
                logger.error(f"作业处理失败: {str(e)}", exc_info=True)
                submission.status = 'failed'
                submission.error_message = str(e)
                submission.save()

                return Response({
                    'success': False,
                    'error': f'作业处理失败: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                'success': True,
                'task_id': task_id,
                'submission_id': submission.id,
                'message': '作业批改完成',
                'score': f'{total_score}/{max_score}'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"作业上传失败: {str(e)}", exc_info=True)
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def result(self, request):
        """
        获取批改结果

        GET /api/homework/result?task_id=xxx
        返回: 批改结果详情
        """
        task_id = request.query_params.get('task_id')

        if not task_id:
            return Response(
                {'success': False, 'error': '缺少task_id参数'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            submission = get_object_or_404(
                HomeworkSubmission,
                task_id=task_id,
                user=request.user
            )

            serializer = self.get_serializer(submission)

            # 构建返回数据
            data = serializer.data

            # 添加步骤状态
            data['steps'] = {
                'ocr': {
                    'completed': submission.ocr_completed,
                    'status': 'completed' if submission.ocr_completed else 'pending'
                },
                'matching': {
                    'completed': submission.matching_completed,
                    'status': 'completed' if submission.matching_completed else 'pending'
                },
                'grading': {
                    'completed': submission.grading_completed,
                    'status': 'completed' if submission.grading_completed else 'pending'
                }
            }

            # 添加错题ID列表
            wrong_questions = submission.questions.filter(is_correct=False)
            data['wrong_question_ids'] = list(wrong_questions.values_list('id', flat=True))

            # 添加相似题
            similar_questions = []
            for question in wrong_questions:
                for similar in question.similar_questions.all():
                    similar_questions.append({
                        'original_question_id': question.id,
                        'id': similar.question_bank_id,
                        'stem': similar.question_stem,
                        'type': similar.question_type,
                        'answer': similar.answer,
                        'similarity_score': similar.similarity_score
                    })

            data['similar_questions'] = similar_questions

            return Response({
                'success': True,
                'data': data
            })

        except Exception as e:
            logger.error(f"获取批改结果失败: {str(e)}", exc_info=True)
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    def _generate_practice_paper_enhanced(
        self,
        submission: HomeworkSubmission,
        wrong_questions: List[Dict[str, Any]]
    ):
        """
        生成错题再练卷（改进版：根据知识点筛选相似题）

        Args:
            submission: 作业提交记录
            wrong_questions: 错题列表（包含knowledge_point字段）
        """
        try:
            from .services.export_service import ExportService
            from .services.question_bank_service import QuestionBankService

            export_service = ExportService()
            question_bank_service = QuestionBankService()

            # 收集所有错题和相似题
            paper_questions = []
            question_number = 1
            knowledge_points_collected = set()  # 收集的知识点

            for wrong_q in wrong_questions[:10]:  # 最多10道错题
                # 添加错题（带答案和解析）
                knowledge_point = wrong_q.get('knowledge_point', '')
                if knowledge_point:
                    knowledge_points_collected.add(knowledge_point)

                paper_questions.append({
                    'number': question_number,
                    'stem': wrong_q.get('question_stem', ''),
                    'type': wrong_q.get('question_type', 'subjective'),
                    'answer': wrong_q.get('correct_answer', ''),
                    'show_answer': True,  # 显示答案
                    'analysis': wrong_q.get('feedback', wrong_q.get('analysis', '')),
                    'knowledge_point': knowledge_point
                })
                question_number += 1

                # 根据知识点查找相似题（优先使用知识点）
                similar_questions = []
                if knowledge_point:
                    # 优先根据知识点查找
                    similar_questions = question_bank_service.find_similar_questions(
                        question_stem=wrong_q.get('question_stem', ''),
                        knowledge_points=[knowledge_point],
                        limit=5
                    )

                # 如果根据知识点没找到，再根据题干查找
                if not similar_questions:
                    similar_questions = question_bank_service.find_similar_questions(
                        question_stem=wrong_q.get('question_stem', ''),
                        limit=5
                    )

                # 添加相似题（最多3道）
                for similar in similar_questions[:3]:
                    if question_number > 25:  # 最多25道题
                        break
                    paper_questions.append({
                        'number': question_number,
                        'stem': similar.get('question_stem', ''),
                        'type': similar.get('question_type', 'subjective'),
                        'answer': similar.get('answer', ''),
                        'show_answer': False,  # 不显示答案（让学生练习）
                        'analysis': '',
                        'knowledge_point': similar.get('knowledge_points', [knowledge_point])[0] if similar.get('knowledge_points') else knowledge_point
                    })
                    question_number += 1

            # 生成PDF
            paper_data = {
                'title': f'错题再练卷 - {submission.user.username}',
                'subtitle': f'涉及知识点：{", ".join(list(knowledge_points_collected)[:5])}' if knowledge_points_collected else '',
                'questions': paper_questions
            }

            # 确保输出目录存在
            output_dir = os.path.join(settings.MEDIA_ROOT, 'papers', 'pdf')
            os.makedirs(output_dir, exist_ok=True)

            pdf_path = os.path.join(output_dir, f'practice_paper_{submission.id}.pdf')
            export_service.export_to_pdf(paper_data, pdf_path)

            # 创建试卷记录
            paper = GeneratedPaper.objects.create(
                submission=submission,
                user=submission.user,
                paper_data=paper_data,
                total_questions=len(paper_questions),
                wrong_question_count=len([q for q in paper_questions if q.get('show_answer')]),
                similar_question_count=len([q for q in paper_questions if not q.get('show_answer')])
            )

            # 保存PDF文件
            with open(pdf_path, 'rb') as f:
                paper.pdf_file.save(f'practice_paper_{submission.id}.pdf', File(f), save=False)

            logger.info(f"✅ 错题再练卷生成完成: {pdf_path}, 共{len(paper_questions)}道题，涉及知识点: {knowledge_points_collected}")

        except Exception as e:
            logger.error(f"生成错题再练卷失败: {str(e)}", exc_info=True)
            raise

    def _generate_practice_paper(self, submission: HomeworkSubmission, wrong_questions: List[Dict[str, Any]]):
        """
        生成错题再练卷（保留原方法作为备用）

        Args:
            submission: 作业提交记录
            wrong_questions: 错题列表
        """
        return self._generate_practice_paper_enhanced(submission, wrong_questions)


class GeneratedPaperViewSet(viewsets.ModelViewSet):
    """生成试卷视图集"""
    queryset = GeneratedPaper.objects.all()
    serializer_class = GeneratedPaperSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """只返回当前用户的试卷"""
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        生成试卷

        POST /api/homework/generate_paper
        body: { submission_id, include_wrong_questions, include_similar_questions, max_questions }
        返回: 生成的试卷信息
        """
        serializer = GeneratePaperRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'success': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            submission_id = serializer.validated_data['submission_id']
            include_wrong = serializer.validated_data['include_wrong_questions']
            include_similar = serializer.validated_data['include_similar_questions']
            max_questions = serializer.validated_data['max_questions']

            # 获取作业提交
            submission = get_object_or_404(
                HomeworkSubmission,
                id=submission_id,
                user=request.user
            )

            if submission.status != 'completed':
                return Response(
                    {'success': False, 'error': '作业尚未批改完成'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 构建试卷数据
            paper_questions = []
            question_number = 1

            # 添加错题
            if include_wrong:
                wrong_questions = submission.questions.filter(is_correct=False)
                for q in wrong_questions[:max_questions]:
                    paper_questions.append({
                        'number': question_number,
                        'stem': q.question_stem,
                        'type': q.question_type,
                        'answer': q.correct_answer,
                        'show_answer': False
                    })
                    question_number += 1

            # 添加相似题
            if include_similar and question_number <= max_questions:
                wrong_questions = submission.questions.filter(is_correct=False)
                for q in wrong_questions:
                    if question_number > max_questions:
                        break

                    similar_questions = q.similar_questions.all()[:2]
                    for similar in similar_questions:
                        if question_number > max_questions:
                            break

                        paper_questions.append({
                            'number': question_number,
                            'stem': similar.question_stem,
                            'type': similar.question_type,
                            'answer': similar.answer,
                            'show_answer': False
                        })
                        question_number += 1

            # 创建试卷记录
            paper_data = {
                'title': f'{request.user.username}的错题练习卷',
                'questions': paper_questions
            }

            paper = GeneratedPaper.objects.create(
                submission=submission,
                user=request.user,
                paper_data=paper_data,
                total_questions=len(paper_questions),
                wrong_question_count=submission.questions.filter(is_correct=False).count(),
                similar_question_count=sum(q.similar_questions.count() for q in submission.questions.all())
            )

            logger.info(f"试卷生成请求成功: paper_id={paper.id}, 用户: {request.user.username}")

            # 同步生成PDF和JPG
            try:
                export_service = ExportService()

                # 生成PDF
                pdf_path = export_service.export_pdf(paper_data, paper.id)
                paper.pdf_file = pdf_path

                # 生成JPG
                jpg_paths = export_service.export_jpg(paper_data, paper.id)
                paper.jpg_files = jpg_paths
                paper.save()

                logger.info(f"试卷生成完成: paper_id={paper.id}")

            except Exception as e:
                logger.error(f"试卷生成失败: {str(e)}", exc_info=True)
                # 删除失败的试卷记录
                paper.delete()

                return Response({
                    'success': False,
                    'error': f'试卷生成失败: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            serializer = self.get_serializer(paper)

            return Response({
                'success': True,
                'data': serializer.data,
                'message': '试卷生成完成'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"生成试卷失败: {str(e)}", exc_info=True)
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_subjects(request):
    """
    获取可用的学科列表

    GET /api/grading/subjects/
    """
    try:
        subjects = SubjectGradingService.get_available_subjects()

        return Response({
            'success': True,
            'subjects': subjects
        })

    except Exception as e:
        logger.error(f"获取学科列表失败: {str(e)}")
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def homework_status(request, task_id):
    """
    获取作业处理状态

    GET /api/homework/status/{task_id}
    """
    try:
        submission = get_object_or_404(
            HomeworkSubmission,
            task_id=task_id,
            user=request.user
        )

        return Response({
            'success': True,
            'status': submission.status,
            'status_display': submission.get_status_display(),
            'progress': {
                'ocr': submission.ocr_completed,
                'matching': submission.matching_completed,
                'grading': submission.grading_completed
            },
            'error': submission.error_message if submission.status == 'failed' else None
        })

    except Exception as e:
        logger.error(f"获取状态失败: {str(e)}")
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
