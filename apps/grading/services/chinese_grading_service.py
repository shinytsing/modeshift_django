"""
语文批改服务
使用讯飞星火3.5 + 智谱GLM-4
专注于中文理解、作文批改、古诗文鉴赏
"""
import os
import logging
import json
from typing import Dict, Any
from PIL import Image

logger = logging.getLogger(__name__)


class ChineseGradingService:
    """语文批改服务类（讯飞星火）"""

    def __init__(self):
        """初始化语文批改服务"""
        # 优先使用腾讯混元（本地已有）
        self.tencent_secret_key = os.getenv('TENCENT_SECRET_KEY', '')
        self.use_tencent = bool(self.tencent_secret_key and self.tencent_secret_key.startswith('sk-'))

        # 备用：智谱GLM
        self.zhipu_api_key = os.getenv('ZHIPU_API_KEY', '')
        self.use_zhipu = bool(self.zhipu_api_key)

        if self.use_tencent:
            logger.info("✅ 使用腾讯混元批改语文")
        elif self.use_zhipu:
            logger.info("✅ 使用智谱GLM批改语文")
        else:
            logger.warning("⚠️  语文批改API未配置，请配置TENCENT_SECRET_KEY或ZHIPU_API_KEY")

    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self.use_tencent or self.use_zhipu

    def grade_homework_from_image(self, image_path: str) -> Dict[str, Any]:
        """
        批改语文作业

        Args:
            image_path: 作业图片路径

        Returns:
            批改结果字典
        """
        logger.info(f"开始批改语文作业: {image_path}")

        # 优先级：腾讯混元 > 智谱GLM
        if self.use_tencent:
            try:
                return self._grade_with_tencent(image_path)
            except Exception as e:
                logger.warning(f"腾讯混元批改失败: {str(e)}")

        if self.use_zhipu:
            try:
                return self._grade_with_zhipu(image_path)
            except Exception as e:
                logger.warning(f"智谱GLM批改失败: {str(e)}")

        raise ValueError("没有可用的语文批改API，请配置TENCENT_SECRET_KEY或ZHIPU_API_KEY")

    def _grade_with_xunfei(self, image_path: str) -> Dict[str, Any]:
        """使用讯飞星火批改"""
        # TODO: 实现讯飞星火API调用
        # 讯飞星火需要WebSocket连接，这里先使用Gemini
        logger.info("讯飞星火API实现中，降级到Gemini")
        return self._grade_with_gemini(image_path)

    def _grade_with_tencent(self, image_path: str) -> Dict[str, Any]:
        """使用腾讯混元批改"""
        from .tencent_grading_service import TencentGradingService
        tencent_service = TencentGradingService()
        return tencent_service.grade_homework_from_image(image_path)

    def _grade_with_zhipu(self, image_path: str) -> Dict[str, Any]:
        """使用智谱GLM批改"""
        from .zhipu_grading_service import ZhipuGradingService
        zhipu_service = ZhipuGradingService()
        return zhipu_service.grade_homework_from_image(image_path)

    def _grade_with_gemini(self, image_path: str) -> Dict[str, Any]:
        """使用Gemini批改（备用方案）"""
        try:
            import google.generativeai as genai
            from PIL import Image

            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')

            image = Image.open(image_path)

            prompt = self._build_chinese_prompt()

            response = model.generate_content([prompt, image])

            # 解析响应
            result = self._parse_response(response.text)

            return result

        except Exception as e:
            logger.error(f"Gemini批改失败: {str(e)}")
            raise

    def _build_chinese_prompt(self) -> str:
        """构建语文批改提示词"""
        return """
你是一位专业的语文教师，请批改这份语文作业。

请特别关注：
1. **作文批改**：结构、语言、修辞、立意
2. **阅读理解**：理解准确性、答案完整性
3. **古诗文**：理解深度、文学素养
4. **基础知识**：字词、语法、标点

请以JSON格式返回（只返回JSON）：
```json
{
  "total_score": 总分,
  "max_score": 满分,
  "questions": [
    {
      "question_number": 题号,
      "question_type": "题目类型",
      "question_stem": "题干",
      "student_answer": "学生答案",
      "correct_answer": "参考答案",
      "score": 得分,
      "max_score": 满分,
      "is_correct": true/false,
      "feedback": "详细反馈（包括：优点、不足、改进建议）"
    }
  ],
  "overall_comment": "总体评价（语言表达、思想深度、文学素养等）"
}
```

语文批改要点：
- 作文：结构10分、语言20分、内容20分
- 阅读：理解准确性、答案完整性
- 古诗文：意境理解、情感把握
- 基础：字词准确、语法正确
"""

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """解析API响应"""
        import re

        # 提取JSON
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
        else:
            json_text = response_text

        result = json.loads(json_text)

        # 确保数值类型
        result['total_score'] = float(result.get('total_score', 0))
        result['max_score'] = float(result.get('max_score', 0))

        for q in result['questions']:
            q['question_number'] = int(q.get('question_number', 0))
            q['score'] = float(q.get('score', 0))
            q['max_score'] = float(q.get('max_score', 0))
            q['is_correct'] = bool(q.get('is_correct', False))

        return result
