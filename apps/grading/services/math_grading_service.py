"""
数学批改服务
使用Google Gemini Pro Vision
专注于公式识别、计算验证、解题步骤分析
"""
import os
import logging
import json
import re
from typing import Dict, Any
from PIL import Image

logger = logging.getLogger(__name__)


class MathGradingService:
    """数学批改服务类（Gemini Vision）"""

    def __init__(self):
        """初始化数学批改服务"""
        # 优先使用腾讯混元（本地已有）
        self.tencent_secret_key = os.getenv('TENCENT_SECRET_KEY', '')
        self.use_tencent = bool(self.tencent_secret_key and self.tencent_secret_key.startswith('sk-'))

        # 备用：智谱GLM
        self.zhipu_api_key = os.getenv('ZHIPU_API_KEY', '')
        self.use_zhipu = bool(self.zhipu_api_key)

        if self.use_tencent:
            logger.info("✅ 使用腾讯混元批改数学")
        elif self.use_zhipu:
            logger.info("✅ 使用智谱GLM-4V批改数学")
        else:
            logger.warning("⚠️  数学批改API未配置，请配置TENCENT_SECRET_KEY")

    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self.use_tencent or self.use_zhipu

    def grade_homework_from_image(self, image_path: str) -> Dict[str, Any]:
        """
        批改数学作业

        Args:
            image_path: 作业图片路径

        Returns:
            批改结果字典
        """
        if not self.is_available():
            raise ValueError("数学批改服务不可用")

        logger.info(f"开始批改数学作业: {image_path}")

        # 优先使用腾讯混元
        if self.use_tencent:
            try:
                from .tencent_grading_service import TencentGradingService
                tencent_service = TencentGradingService()
                return tencent_service.grade_homework_from_image(image_path)
            except Exception as e:
                logger.warning(f"腾讯混元批改失败: {str(e)}")

        # 备用：智谱GLM-4V
        if self.use_zhipu:
            try:
                from .zhipu_grading_service import ZhipuGradingService
                zhipu_service = ZhipuGradingService()
                return zhipu_service.grade_homework_from_image(image_path)
            except Exception as e:
                logger.warning(f"智谱GLM批改失败: {str(e)}")

        # 降级到Gemini（如果配置了）
        if self.use_gemini:
            try:
                import google.generativeai as genai
                from PIL import Image

                image = Image.open(image_path)
                prompt = self._build_math_prompt()

                response = self.model.generate_content([prompt, image])

                logger.info("数学作业批改完成")

                result = self._parse_response(response.text)

                return result

            except Exception as e:
                logger.error(f"数学作业批改失败: {str(e)}", exc_info=True)
                raise

        raise ValueError("没有可用的数学批改服务")

    def _build_math_prompt(self) -> str:
        """构建数学批改提示词"""
        return """
你是一位专业的数学教师，请批改这份数学作业。

请特别关注：
1. **公式识别**：准确识别数学公式和符号
2. **计算验证**：验证计算过程和结果
3. **解题步骤**：检查解题思路和步骤完整性
4. **答案准确性**：判断最终答案是否正确

请以JSON格式返回（只返回JSON）：
```json
{
  "total_score": 总分,
  "max_score": 满分,
  "questions": [
    {
      "question_number": 题号,
      "question_type": "题目类型（choice/calculation/proof/application）",
      "question_stem": "题干（包括数学公式）",
      "student_answer": "学生答案",
      "correct_answer": "正确答案",
      "score": 得分,
      "max_score": 满分,
      "is_correct": true/false,
      "feedback": "详细反馈",
      "calculation_steps": "计算步骤分析",
      "error_type": "错误类型（如：计算错误、公式错误、步骤缺失等）"
    }
  ],
  "overall_comment": "总体评价（计算能力、解题思路、知识掌握等）"
}
```

数学题目类型：
- choice: 选择题
- calculation: 计算题
- proof: 证明题
- application: 应用题

批改要点：
- 计算题：每步计算都要验证
- 证明题：逻辑严密性、步骤完整性
- 应用题：建模能力、实际应用
- 选择题：答案准确性

特别注意：
- 数学符号识别准确性
- 分数、根号、指数的正确性
- 单位换算的准确性
- 小数点位置
"""

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """解析API响应"""
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

        logger.info(f"成功解析数学批改结果: {len(result['questions'])}道题")

        return result
