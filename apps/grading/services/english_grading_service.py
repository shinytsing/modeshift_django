"""
英语批改服务
使用LanguageTool（语法检查）+ Gemini（内容评分）
专注于语法检查、词汇使用、作文评分
"""
import os
import logging
import json
import re
from typing import Dict, Any
from PIL import Image

logger = logging.getLogger(__name__)


class EnglishGradingService:
    """英语批改服务类（LanguageTool + Gemini）"""

    def __init__(self):
        """初始化英语批改服务"""
        # 优先使用腾讯混元（本地已有）
        self.tencent_secret_key = os.getenv('TENCENT_SECRET_KEY', '')
        self.use_tencent = bool(self.tencent_secret_key and self.tencent_secret_key.startswith('sk-'))

        # 备用：智谱GLM
        self.zhipu_api_key = os.getenv('ZHIPU_API_KEY', '')
        self.use_zhipu = bool(self.zhipu_api_key)

        if self.use_tencent:
            logger.info("✅ 使用腾讯混元批改英语")
        elif self.use_zhipu:
            logger.info("✅ 使用智谱GLM-4批改英语")
        else:
            logger.warning("⚠️  英语批改API未配置，请配置TENCENT_SECRET_KEY")

    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self.use_tencent or self.use_zhipu

    def grade_homework_from_image(self, image_path: str) -> Dict[str, Any]:
        """
        批改英语作业

        Args:
            image_path: 作业图片路径

        Returns:
            批改结果字典
        """
        if not self.is_available():
            raise ValueError("英语批改服务不可用")

        logger.info(f"开始批改英语作业: {image_path}")

        # 优先使用腾讯混元
        if self.use_tencent:
            try:
                from .tencent_grading_service import TencentGradingService
                tencent_service = TencentGradingService()
                return tencent_service.grade_homework_from_image(image_path)
            except Exception as e:
                logger.warning(f"腾讯混元批改失败: {str(e)}")

        # 备用：智谱GLM-4
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
                prompt = self._build_english_prompt()

                response = self.model.generate_content([prompt, image])

                logger.info("英语作业批改完成")

                result = self._parse_response(response.text)

                return result

            except Exception as e:
                logger.error(f"英语作业批改失败: {str(e)}", exc_info=True)
                raise

        raise ValueError("没有可用的英语批改服务")

    def _build_english_prompt(self) -> str:
        """构建英语批改提示词"""
        return """
You are a professional English teacher. Please grade this English homework.

Please focus on:
1. **Grammar**: Check grammar errors and sentence structure
2. **Vocabulary**: Evaluate word choice and usage
3. **Spelling**: Check spelling mistakes
4. **Content**: Assess content quality and coherence
5. **Writing Style**: Evaluate writing style and expression

Please return in JSON format (JSON only):
```json
{
  "total_score": total_score,
  "max_score": max_score,
  "questions": [
    {
      "question_number": question_number,
      "question_type": "type (choice/fill/writing/reading)",
      "question_stem": "question text",
      "student_answer": "student's answer",
      "correct_answer": "correct answer",
      "score": score,
      "max_score": max_score,
      "is_correct": true/false,
      "feedback": "detailed feedback",
      "grammar_errors": ["list of grammar errors"],
      "vocabulary_suggestions": ["vocabulary improvement suggestions"],
      "spelling_errors": ["spelling mistakes"]
    }
  ],
  "overall_comment": "Overall evaluation (grammar, vocabulary, writing skills, etc.)"
}
```

Question types:
- choice: Multiple choice questions
- fill: Fill in the blanks
- writing: Essay/composition
- reading: Reading comprehension

Grading criteria:
- Grammar (30%): Tense, voice, sentence structure
- Vocabulary (25%): Word choice, collocation
- Content (25%): Ideas, organization, coherence
- Spelling (10%): Spelling accuracy
- Style (10%): Writing style, expression

Special attention:
- Subject-verb agreement
- Tense consistency
- Article usage (a/an/the)
- Preposition usage
- Word order
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

        logger.info(f"成功解析英语批改结果: {len(result['questions'])}道题")

        return result
