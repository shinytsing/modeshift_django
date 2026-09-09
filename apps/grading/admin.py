"""
作业批改管理后台
"""
from django.contrib import admin
from .models import HomeworkSubmission, QuestionResult, GeneratedPaper, SimilarQuestion


@admin.register(HomeworkSubmission)
class HomeworkSubmissionAdmin(admin.ModelAdmin):
    """作业提交管理"""
    list_display = ['id', 'user', 'task_id', 'status', 'total_score', 'max_score', 'created_at']
    list_filter = ['status', 'file_type', 'created_at']
    search_fields = ['task_id', 'user__username']
    readonly_fields = ['task_id', 'created_at', 'updated_at', 'completed_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'file', 'file_type', 'task_id', 'status')
        }),
        ('批改结果', {
            'fields': ('total_score', 'max_score')
        }),
        ('处理进度', {
            'fields': ('ocr_completed', 'matching_completed', 'grading_completed')
        }),
        ('错误信息', {
            'fields': ('error_message',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )


@admin.register(QuestionResult)
class QuestionResultAdmin(admin.ModelAdmin):
    """题目批改结果管理"""
    list_display = ['id', 'submission', 'question_number', 'question_type', 'is_correct', 'score', 'max_score']
    list_filter = ['question_type', 'is_correct', 'created_at']
    search_fields = ['submission__task_id', 'question_stem', 'student_answer']
    readonly_fields = ['created_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('submission', 'question_number', 'question_type')
        }),
        ('OCR识别', {
            'fields': ('ocr_text', 'ocr_confidence')
        }),
        ('题目内容', {
            'fields': ('question_bank_id', 'question_stem', 'correct_answer', 'student_answer')
        }),
        ('批改结果', {
            'fields': ('is_correct', 'score', 'max_score', 'feedback', 'llm_analysis')
        }),
        ('时间信息', {
            'fields': ('created_at',)
        }),
    )


@admin.register(GeneratedPaper)
class GeneratedPaperAdmin(admin.ModelAdmin):
    """生成试卷管理"""
    list_display = ['id', 'user', 'submission', 'total_questions', 'wrong_question_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'submission__task_id']
    readonly_fields = ['created_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('submission', 'user')
        }),
        ('试卷内容', {
            'fields': ('paper_data',)
        }),
        ('导出文件', {
            'fields': ('pdf_file', 'jpg_files')
        }),
        ('统计信息', {
            'fields': ('total_questions', 'wrong_question_count', 'similar_question_count')
        }),
        ('时间信息', {
            'fields': ('created_at',)
        }),
    )


@admin.register(SimilarQuestion)
class SimilarQuestionAdmin(admin.ModelAdmin):
    """相似题目管理"""
    list_display = ['id', 'question_result', 'question_bank_id', 'question_type', 'similarity_score']
    list_filter = ['question_type', 'difficulty', 'created_at']
    search_fields = ['question_bank_id', 'question_stem']
    readonly_fields = ['created_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('question_result', 'question_bank_id', 'question_type')
        }),
        ('题目内容', {
            'fields': ('question_stem', 'answer')
        }),
        ('题目属性', {
            'fields': ('difficulty', 'knowledge_points', 'similarity_score')
        }),
        ('时间信息', {
            'fields': ('created_at',)
        }),
    )
