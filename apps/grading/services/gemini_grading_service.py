"""
Google Gemini Vision批改服务
直接分析作业图片，无需OCR
"""
import os
import logging
import json
import base64
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class GeminiGradingService:
    """Google Gemini Vision批改服务类"""

    def __init__(self):
        """初始化Gemini服务（支持代理）"""
        self.api_key = os.getenv('GEMINI_API_KEY', '')
        self.proxy = os.getenv('HTTPS_PROXY') or os.getenv('HTTP_PROXY', '')
        self.use_gemini = bool(self.api_key)

        if self.use_gemini:
            try:
                import google.generativeai as genai

                # 如果配置了代理，显示提示
                if self.proxy:
                    logger.info(f"🌐 检测到代理配置: {self.proxy}")
                    logger.info("💡 Gemini将通过代理访问")

                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')

                if self.proxy:
                    logger.info("✅ Gemini Vision服务初始化成功（通过代理）")
                else:
                    logger.info("✅ Gemini Vision服务初始化成功")
                    logger.warning("💡 如果在国内无法访问，请配置代理: export HTTPS_PROXY='http://127.0.0.1:7890'")

            except Exception as e:
                logger.error(f"❌ Gemini初始化失败: {str(e)}")
                if self.proxy:
                    logger.warning("💡 请检查代理设置是否正确")
                else:
                    logger.warning("💡 如果在国内，请配置代理或使用智谱AI")
                self.use_gemini = False
        else:
            logger.info("ℹ️  GEMINI_API_KEY未配置，将使用智谱AI")

    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self.use_gemini

    def grade_homework_from_image(self, image_path: str) -> Dict[str, Any]:
        """
        直接从图片批改作业

        Args:
            image_path: 作业图片路径

        Returns:
            批改结果字典
        """
        if not self.is_available():
            raise ValueError("Gemini服务不可用")

        try:
            import google.generativeai as genai
            from PIL import Image

            # 打开图片
            image = Image.open(image_path)

            # 构建提示词
            prompt = self._build_grading_prompt()

            logger.info(f"开始使用Gemini Vision批改作业: {image_path}")

            # 调用Gemini Vision
            response = self.model.generate_content([prompt, image])

            logger.info("Gemini批改完成")
            logger.debug(f"Gemini响应: {response.text[:500]}...")

            # 解析响应
            result = self._parse_gemini_response(response.text)

            return result

        except Exception as e:
            logger.error(f"Gemini批改失败: {str(e)}", exc_info=True)
            raise

    def _build_grading_prompt(self) -> str:
        """构建批改提示词"""
        return """
你是一位专业的教师，请批改这份作业图片。

请按以下步骤操作：
1. 识别图片中的所有题目
2. 识别每道题的学生答案
3. 判断每道题的答案是否正确
4. 给出每道题的得分和反馈
5. 计算总分

请以JSON格式返回结果（只返回JSON，不要其他文字）：
```json
{
  "total_score": 总分（数字）,
  "max_score": 满分（数字）,
  "questions": [
    {
      "question_number": 题号（数字）,
      "question_type": "题目类型（choice/fill/subjective）",
      "question_stem": "题干内容",
      "student_answer": "学生的答案",
      "correct_answer": "正确答案",
      "score": 得分（数字）,
      "max_score": 满分（数字）,
      "is_correct": true或false,
      "feedback": "详细的批改反馈"
    }
  ]
}
```

题目类型说明：
- choice: 选择题（包含A、B、C、D选项）
- fill: 填空题（包含下划线或空白处）
- subjective: 主观题（需要详细回答的问题）

注意事项：
1. 仔细识别每道题的题号
2. 准确提取学生的答案
3. 对于选择题，只比对选项字母（A、B、C、D）
4. 对于填空题，考虑数值容差和表达式等价
5. 对于主观题，根据关键点给分，并提供详细反馈
6. 确保所有数字都是数值类型，不是字符串
7. 确保JSON格式正确，可以被解析
"""

    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """
        解析Gemini的响应

        Args:
            response_text: Gemini返回的文本

        Returns:
            解析后的结果字典
        """
        try:
            # 提取JSON部分
            # Gemini可能会返回包含```json```标记的文本
            import re

            # 尝试提取JSON代码块
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                # 尝试直接解析
                json_text = response_text

            # 解析JSON
            result = json.loads(json_text)

            # 验证结果格式
            if not isinstance(result, dict):
                raise ValueError("响应不是字典格式")

            if 'questions' not in result:
                raise ValueError("响应中缺少questions字段")

            # 确保数值类型正确
            result['total_score'] = float(result.get('total_score', 0))
            result['max_score'] = float(result.get('max_score', 0))

            for q in result['questions']:
                q['question_number'] = int(q.get('question_number', 0))
                q['score'] = float(q.get('score', 0))
                q['max_score'] = float(q.get('max_score', 0))
                q['is_correct'] = bool(q.get('is_correct', False))

            logger.info(f"成功解析Gemini响应: {len(result['questions'])}道题目")

            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {str(e)}")
            logger.error(f"原始响应: {response_text}")
            raise ValueError(f"无法解析Gemini响应: {str(e)}")
        except Exception as e:
            logger.error(f"响应解析失败: {str(e)}")
            raise

    def grade_homework_batch(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """
        批量批改作业

        Args:
            image_paths: 作业图片路径列表

        Returns:
            批改结果列表
        """
        results = []

        for image_path in image_paths:
            try:
                result = self.grade_homework_from_image(image_path)
                results.append({
                    'success': True,
                    'image_path': image_path,
                    'result': result
                })
            except Exception as e:
                logger.error(f"批改失败 {image_path}: {str(e)}")
                results.append({
                    'success': False,
                    'image_path': image_path,
                    'error': str(e)
                })

        return results
