"""
验证码模型
用于存储和管理验证码
"""
from django.db import models
from django.utils import timezone
import uuid


class VerificationCode(models.Model):
    """验证码模型"""
    
    code = models.CharField(max_length=20, unique=True, verbose_name="验证码")
    is_used = models.BooleanField(default=False, verbose_name="是否已使用")
    used_at = models.DateTimeField(null=True, blank=True, verbose_name="使用时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    task_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="任务ID")
    
    class Meta:
        db_table = 'verification_codes'
        verbose_name = "验证码"
        verbose_name_plural = "验证码"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} ({'已使用' if self.is_used else '未使用'})"
    
    def mark_as_used(self, task_id=None):
        """标记为已使用"""
        self.is_used = True
        self.used_at = timezone.now()
        if task_id:
            self.task_id = task_id
        self.save()
    
    @classmethod
    def generate_code(cls):
        """生成新的验证码"""
        return str(uuid.uuid4()).replace('-', '').upper()[:8]
    
    @classmethod
    def create_codes(cls, count=100000):
        """批量创建验证码"""
        codes = []
        for _ in range(count):
            code = cls.generate_code()
            codes.append(cls(code=code))
        
        cls.objects.bulk_create(codes, batch_size=1000)
        return len(codes)
    
    @classmethod
    def get_available_count(cls):
        """获取可用验证码数量"""
        return cls.objects.filter(is_used=False).count()
    
    @classmethod
    def validate_and_consume(cls, code):
        """验证并消费验证码"""
        try:
            verification_code = cls.objects.get(code=code.upper(), is_used=False)
            verification_code.mark_as_used()
            return True, verification_code
        except cls.DoesNotExist:
            return False, None
