"""
验证码管理系统
使用文件存储10万个验证码，使用一个删除一个
"""
import json
import os
import uuid
import logging
from typing import List, Tuple, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class VerificationCodeManager:
    """验证码管理器"""
    
    def __init__(self):
        self.codes_file = os.path.join(settings.BASE_DIR, 'verification_codes.json')
        self.used_codes_file = os.path.join(settings.BASE_DIR, 'used_codes.json')
        self.ensure_files_exist()
    
    def ensure_files_exist(self):
        """确保文件存在"""
        if not os.path.exists(self.codes_file):
            self.generate_codes(100000)
        
        if not os.path.exists(self.used_codes_file):
            with open(self.used_codes_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def generate_code(self) -> str:
        """生成8位验证码"""
        return str(uuid.uuid4()).replace('-', '').upper()[:8]
    
    def generate_codes(self, count: int = 100000) -> int:
        """生成指定数量的验证码"""
        logger.info(f"开始生成 {count} 个验证码...")
        
        codes = []
        for i in range(count):
            code = self.generate_code()
            codes.append(code)
            
            if (i + 1) % 10000 == 0:
                logger.info(f"已生成 {i + 1} 个验证码")
        
        # 保存到文件
        with open(self.codes_file, 'w', encoding='utf-8') as f:
            json.dump(codes, f, ensure_ascii=False, indent=2)
        
        logger.info(f"验证码生成完成，共 {len(codes)} 个")
        return len(codes)
    
    def load_codes(self) -> List[str]:
        """加载所有验证码"""
        try:
            with open(self.codes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def load_used_codes(self) -> List[str]:
        """加载已使用的验证码"""
        try:
            with open(self.used_codes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_used_code(self, code: str):
        """保存已使用的验证码"""
        used_codes = self.load_used_codes()
        used_codes.append(code)
        
        with open(self.used_codes_file, 'w', encoding='utf-8') as f:
            json.dump(used_codes, f, ensure_ascii=False, indent=2)
    
    def remove_code(self, code: str):
        """从可用列表中移除验证码"""
        codes = self.load_codes()
        if code in codes:
            codes.remove(code)
            
            with open(self.codes_file, 'w', encoding='utf-8') as f:
                json.dump(codes, f, ensure_ascii=False, indent=2)
    
    def validate_and_consume(self, code: str) -> Tuple[bool, Optional[str]]:
        """验证并消费验证码"""
        code = code.upper().strip()
        
        # 检查是否已使用
        used_codes = self.load_used_codes()
        if code in used_codes:
            return False, "验证码已使用"
        
        # 检查是否在可用列表中
        codes = self.load_codes()
        if code not in codes:
            return False, "验证码无效"
        
        # 消费验证码
        self.remove_code(code)
        self.save_used_code(code)
        
        logger.info(f"验证码 {code} 验证成功并已消费")
        return True, None
    
    def get_available_count(self) -> int:
        """获取可用验证码数量"""
        codes = self.load_codes()
        return len(codes)
    
    def get_used_count(self) -> int:
        """获取已使用验证码数量"""
        used_codes = self.load_used_codes()
        return len(used_codes)
    
    def get_total_count(self) -> int:
        """获取总验证码数量"""
        return self.get_available_count() + self.get_used_count()
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            'total': self.get_total_count(),
            'available': self.get_available_count(),
            'used': self.get_used_count(),
            'usage_rate': round(self.get_used_count() / max(self.get_total_count(), 1) * 100, 2)
        }


# 全局验证码管理器实例
verification_manager = VerificationCodeManager()
