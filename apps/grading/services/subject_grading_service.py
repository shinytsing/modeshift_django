"""
学科专用批改服务
根据不同学科选择最佳AI API
"""
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class SubjectGradingService:
    """学科批改服务统一入口"""

    # 学科映射
    SUBJECTS = {
        'chinese': '语文',
        'math': '数学',
        'english': '英语',
        'physics': '物理',
        'chemistry': '化学',
        'biology': '生物',
        'history': '历史',
        'geography': '地理',
        'politics': '政治'
    }

    def __init__(self, subject: str = 'chinese'):
        """
        初始化学科批改服务

        Args:
            subject: 学科代码 (chinese/math/english等)
        """
        self.subject = subject
        self.subject_name = self.SUBJECTS.get(subject, '未知学科')
        self.service = self._get_service_for_subject(subject)

        logger.info(f"初始化{self.subject_name}批改服务")

    def _get_service_for_subject(self, subject: str):
        """根据学科选择最佳批改服务"""
        if subject == 'chinese':
            from .chinese_grading_service import ChineseGradingService
            return ChineseGradingService()
        elif subject == 'math':
            from .math_grading_service import MathGradingService
            return MathGradingService()
        elif subject == 'english':
            from .english_grading_service import EnglishGradingService
            return EnglishGradingService()
        else:
            # 默认使用Gemini Vision
            from .gemini_grading_service import GeminiGradingService
            return GeminiGradingService()

    def grade_homework(self, image_path: str) -> Dict[str, Any]:
        """
        批改作业

        Args:
            image_path: 作业图片路径

        Returns:
            批改结果字典
        """
        logger.info(f"开始批改{self.subject_name}作业: {image_path}")

        try:
            result = self.service.grade_homework_from_image(image_path)

            # 添加学科信息
            result['subject'] = self.subject
            result['subject_name'] = self.subject_name
            result['grading_engine'] = self.service.__class__.__name__

            logger.info(f"{self.subject_name}作业批改完成")

            return result

        except Exception as e:
            logger.error(f"{self.subject_name}作业批改失败: {str(e)}")
            raise

    def is_available(self) -> bool:
        """检查服务是否可用"""
        return hasattr(self.service, 'is_available') and self.service.is_available()

    @classmethod
    def get_available_subjects(cls) -> Dict[str, Dict[str, str]]:
        """
        获取所有可用的学科及其配置

        Returns:
            学科配置字典
        """
        subjects_config = {
            'chinese': {
                'name': '语文',
                'icon': '📖',
                'engine': '智谱GLM-4（国产免费）',
                'features': ['中文理解', '作文批改', '古诗文鉴赏'],
                'free': True
            },
            'math': {
                'name': '数学',
                'icon': '🔢',
                'engine': '智谱GLM-4V（国产免费）',
                'features': ['公式识别', '计算验证', '解题步骤'],
                'free': True
            },
            'english': {
                'name': '英语',
                'icon': '🔤',
                'engine': '智谱GLM-4（国产免费）',
                'features': ['语法检查', '词汇建议', '作文评分'],
                'free': True
            },
            'physics': {
                'name': '物理',
                'icon': '⚛️',
                'engine': '智谱GLM-4V（国产免费）',
                'features': ['公式识别', '实验分析', '概念理解'],
                'free': True
            },
            'chemistry': {
                'name': '化学',
                'icon': '🧪',
                'engine': '智谱GLM-4V（国产免费）',
                'features': ['化学式识别', '方程式配平', '实验分析'],
                'free': True
            }
        }

        return subjects_config
