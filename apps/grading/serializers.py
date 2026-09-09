"""
作业批改序列化器
"""
from rest_framework import serializers
from .models import HomeworkSubmission, QuestionResult, GeneratedPaper, SimilarQuestion


class SimilarQuestionSerializer(serializers.ModelSerializer):
    """相似题目序列化器"""
    class Meta:
        model = SimilarQuestion
        fields = [
            'id', 'question_bank_id', 'question_stem', 'question_type',
            'answer', 'difficulty', 'knowledge_points', 'similarity_score'
        ]


class QuestionResultSerializer(serializers.ModelSerializer):
    """题目批改结果序列化器"""
    similar_questions = SimilarQuestionSerializer(many=True, read_only=True)
    question_type_display = serializers.CharField(source='get_question_type_display', read_only=True)

    class Meta:
        model = QuestionResult
        fields = [
            'id', 'question_number', 'question_type', 'question_type_display',
            'ocr_text', 'ocr_confidence', 'question_bank_id', 'question_stem',
            'correct_answer', 'student_answer', 'is_correct', 'score', 'max_score',
            'feedback', 'llm_analysis', 'similar_questions', 'created_at'
        ]


class HomeworkSubmissionSerializer(serializers.ModelSerializer):
    """作业提交序列化器"""
    questions = QuestionResultSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    file_url = serializers.SerializerMethodField()
    marked_image_url = serializers.SerializerMethodField()
    graded_image_url = serializers.SerializerMethodField()
    graded_pdf_url = serializers.SerializerMethodField()
    practice_pdf_url = serializers.SerializerMethodField()

    def get_file_url(self, obj):
        """获取原文件URL"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def get_marked_image_url(self, obj):
        """获取标记后的图片URL"""
        if obj.marked_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.marked_image.url)
            return obj.marked_image.url
        return None

    def get_graded_image_url(self, obj):
        """获取批改后的图片URL（兼容字段）"""
        return self.get_marked_image_url(obj)

    def get_graded_pdf_url(self, obj):
        """获取批改后的PDF URL（题目+解析列表）"""
        # 优先返回批改结果PDF
        if obj.grading_result_pdf:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.grading_result_pdf.url)
            return obj.grading_result_pdf.url

        # 如果没有，返回错题再练卷PDF
        paper = obj.generated_papers.first()
        if paper and paper.pdf_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(paper.pdf_file.url)
            return paper.pdf_file.url
        return None

    def get_practice_pdf_url(self, obj):
        """获取错题再练卷PDF URL"""
        paper = obj.generated_papers.first()
        if paper and paper.pdf_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(paper.pdf_file.url)
            return paper.pdf_file.url
        return None

    class Meta:
        model = HomeworkSubmission
        fields = [
            'id', 'user', 'username', 'file', 'file_url', 'file_type', 'status', 'status_display',
            'task_id', 'total_score', 'max_score', 'ocr_completed', 'matching_completed',
            'grading_completed', 'error_message', 'questions', 'marked_image', 'marked_image_url',
            'graded_image_url', 'graded_pdf_url', 'practice_pdf_url', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['task_id', 'status', 'total_score', 'marked_image']


class HomeworkUploadSerializer(serializers.Serializer):
    """作业上传序列化器"""
    file = serializers.FileField(required=True, help_text='作业文件（图片或PDF）')
    student_id = serializers.IntegerField(required=False, help_text='学生ID（可选）')

    def validate_file(self, value):
        """验证文件类型和大小"""
        # 验证文件大小（最大50MB）
        max_size = 50 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError('文件大小不能超过50MB')

        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError('只支持JPG、PNG图片和PDF文件')

        return value


class GeneratedPaperSerializer(serializers.ModelSerializer):
    """生成试卷序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = GeneratedPaper
        fields = [
            'id', 'submission', 'user', 'username', 'paper_data',
            'pdf_file', 'jpg_files', 'total_questions', 'wrong_question_count',
            'similar_question_count', 'created_at'
        ]
        read_only_fields = ['pdf_file', 'jpg_files']


class GeneratePaperRequestSerializer(serializers.Serializer):
    """生成试卷请求序列化器"""
    submission_id = serializers.IntegerField(required=True, help_text='作业提交ID')
    include_wrong_questions = serializers.BooleanField(default=True, help_text='包含错题')
    include_similar_questions = serializers.BooleanField(default=True, help_text='包含相似题')
    max_questions = serializers.IntegerField(default=20, min_value=1, max_value=100, help_text='最大题目数')
