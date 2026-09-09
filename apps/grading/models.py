"""
作业批改数据模型
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class HomeworkSubmission(models.Model):
    """作业提交记录"""
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('ocr_processing', 'OCR识别中'),
        ('matching', '题目匹配中'),
        ('grading', '批改中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='提交用户')
    file = models.FileField(upload_to='homework/%Y/%m/%d/', verbose_name='作业文件')
    file_type = models.CharField(max_length=10, verbose_name='文件类型')  # image, pdf
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='处理状态')
    task_id = models.CharField(max_length=100, unique=True, verbose_name='任务ID')

    # 批改结果
    total_score = models.FloatField(null=True, blank=True, verbose_name='总分')
    max_score = models.FloatField(default=100.0, verbose_name='满分')

    # 处理进度
    ocr_completed = models.BooleanField(default=False, verbose_name='OCR完成')
    matching_completed = models.BooleanField(default=False, verbose_name='匹配完成')
    grading_completed = models.BooleanField(default=False, verbose_name='批改完成')

    # 错误信息
    error_message = models.TextField(blank=True, verbose_name='错误信息')

    # 标记后的图片（带对错标记）
    marked_image = models.FileField(upload_to='homework/marked/%Y/%m/%d/', blank=True, null=True, verbose_name='标记后的图片')

    # OCR结果（JSON格式）
    ocr_result = models.JSONField(null=True, blank=True, verbose_name='OCR识别结果')

    # 批改结果PDF（题目+解析列表）
    grading_result_pdf = models.FileField(upload_to='grading_results/pdf/%Y/%m/%d/', blank=True, null=True, verbose_name='批改结果PDF')
    grading_result_pdf_path = models.CharField(max_length=500, blank=True, verbose_name='批改结果PDF路径')

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')

    class Meta:
        db_table = 'grading_homework_submission'
        verbose_name = '作业提交'
        verbose_name_plural = '作业提交'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.task_id}"


class QuestionResult(models.Model):
    """题目批改结果"""
    QUESTION_TYPE_CHOICES = [
        ('choice', '选择题'),
        ('fill', '填空题'),
        ('subjective', '主观题'),
    ]

    submission = models.ForeignKey(HomeworkSubmission, on_delete=models.CASCADE, related_name='questions', verbose_name='作业提交')
    question_number = models.IntegerField(verbose_name='题号')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, verbose_name='题目类型')

    # OCR识别内容
    ocr_text = models.TextField(verbose_name='OCR识别文本')
    ocr_confidence = models.FloatField(default=0.0, verbose_name='识别置信度')

    # 题库匹配
    question_bank_id = models.CharField(max_length=100, blank=True, verbose_name='题库题目ID')
    question_stem = models.TextField(blank=True, verbose_name='题干')
    correct_answer = models.TextField(blank=True, verbose_name='正确答案')
    student_answer = models.TextField(blank=True, verbose_name='学生答案')

    # 批改结果
    is_correct = models.BooleanField(null=True, blank=True, verbose_name='是否正确')
    score = models.FloatField(default=0.0, verbose_name='得分')
    max_score = models.FloatField(default=10.0, verbose_name='满分')
    feedback = models.TextField(blank=True, verbose_name='批改反馈')

    # LLM批改详情（主观题）
    llm_analysis = models.JSONField(null=True, blank=True, verbose_name='LLM分析结果')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'grading_question_result'
        verbose_name = '题目批改结果'
        verbose_name_plural = '题目批改结果'
        ordering = ['submission', 'question_number']

    def __str__(self):
        return f"题{self.question_number} - {self.get_question_type_display()}"


class GeneratedPaper(models.Model):
    """生成的试卷"""
    submission = models.ForeignKey(HomeworkSubmission, on_delete=models.CASCADE, related_name='generated_papers', verbose_name='原作业')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')

    # 试卷内容
    paper_data = models.JSONField(verbose_name='试卷数据')  # 包含题目列表

    # 导出文件
    pdf_file = models.FileField(upload_to='papers/pdf/%Y/%m/%d/', blank=True, verbose_name='PDF文件')
    jpg_files = models.JSONField(default=list, blank=True, verbose_name='JPG文件列表')

    # 统计信息
    total_questions = models.IntegerField(default=0, verbose_name='题目总数')
    wrong_question_count = models.IntegerField(default=0, verbose_name='错题数量')
    similar_question_count = models.IntegerField(default=0, verbose_name='相似题数量')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'grading_generated_paper'
        verbose_name = '生成试卷'
        verbose_name_plural = '生成试卷'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - 试卷 {self.id}"


class SimilarQuestion(models.Model):
    """相似题目推荐"""
    question_result = models.ForeignKey(QuestionResult, on_delete=models.CASCADE, related_name='similar_questions', verbose_name='原题目')

    # 题库返回的相似题信息
    question_bank_id = models.CharField(max_length=100, verbose_name='题库题目ID')
    question_stem = models.TextField(verbose_name='题干')
    question_type = models.CharField(max_length=20, verbose_name='题目类型')
    answer = models.TextField(blank=True, verbose_name='答案')
    difficulty = models.CharField(max_length=20, blank=True, verbose_name='难度')
    knowledge_points = models.JSONField(default=list, blank=True, verbose_name='知识点')
    similarity_score = models.FloatField(default=0.0, verbose_name='相似度分数')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'grading_similar_question'
        verbose_name = '相似题目'
        verbose_name_plural = '相似题目'
        ordering = ['-similarity_score']

    def __str__(self):
        return f"相似题 - {self.question_bank_id}"
