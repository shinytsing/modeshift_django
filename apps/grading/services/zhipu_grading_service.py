"""
智谱AI GLM-4V批改服务
国内免费AI服务，支持图片识别和批改
"""
import os
import logging
import json
import base64
import re
from typing import Dict, Any
import requests
from PIL import Image

logger = logging.getLogger(__name__)


class ZhipuGradingService:
    """智谱AI批改服务类（GLM-4V）"""

    def __init__(self):
        """初始化智谱AI服务"""
        self.api_key = os.getenv('ZHIPU_API_KEY', '')
        self.api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.use_zhipu = bool(self.api_key)

        if self.use_zhipu:
            logger.info("✅ 使用智谱AI GLM-4V批改作业")
        else:
            logger.warning("⚠️  ZHIPU_API_KEY未配置")

    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self.use_zhipu

    def grade_homework_from_image(self, image_path: str) -> Dict[str, Any]:
        """
        使用GLM-4V批改作业

        Args:
            image_path: 作业图片路径

        Returns:
            批改结果字典
        """
        if not self.is_available():
            raise ValueError("智谱AI服务不可用，请配置ZHIPU_API_KEY")

        try:
            logger.info(f"开始使用智谱AI批改作业: {image_path}")

            # 读取并编码图片
            image_base64 = self._encode_image(image_path)

            # 构建请求
            prompt = self._build_grading_prompt()

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "glm-4v",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个作业批改助手。你必须严格按照JSON格式返回结果，不要添加任何解释性文字。"
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 3000,
                "response_format": {"type": "json_object"}
            }

            logger.info("发送请求到智谱AI...")
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)

            if response.status_code != 200:
                logger.error(f"智谱AI API错误: {response.status_code} - {response.text}")
                raise ValueError(f"智谱AI API错误: {response.status_code}")

            result = response.json()
            logger.info("智谱AI批改完成")

            # 解析响应
            content = result['choices'][0]['message']['content']
            parsed_result = self._parse_response(content)

            return parsed_result

        except Exception as e:
            logger.error(f"智谱AI批改失败: {str(e)}", exc_info=True)
            raise

    def _encode_image(self, image_path: str) -> str:
        """将图片编码为base64"""
        try:
            # 压缩图片（智谱AI限制图片大小）
            img = Image.open(image_path)

            # 如果图片太大，压缩它
            max_size = (1920, 1080)
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                logger.info(f"图片已压缩到 {img.size}")

            # 转换为RGB（如果是RGBA）
            if img.mode == 'RGBA':
                img = img.convert('RGB')

            # 保存到临时文件
            import io
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)

            # 编码为base64
            image_data = base64.b64encode(buffer.read()).decode('utf-8')

            logger.info(f"图片编码完成，大小: {len(image_data)} 字节")

            return image_data

        except Exception as e:
            logger.error(f"图片编码失败: {str(e)}")
            raise

    def _build_grading_prompt(self) -> str:
        """构建批改提示词（改进版：提高识别和判题精度）"""
        return """你是一位经验丰富的教师，请仔细批改这份作业图片。

**核心任务：**
1. **完整识别**：逐题识别，不要遗漏任何题目（包括选择题、填空题、计算题、主观题）
2. **准确判题**：根据题目内容和学生答案，准确判断对错
3. **给出正确答案**：如果学生答错，必须给出完整正确答案
4. **详细解析**：每题给出20-50字的简短解析，说明为什么对或错
5. **识别知识点**：标注每题涉及的知识点（如"分数加减法"、"近义词辨析"、"一元一次方程"等）

**识别要求：**
- 仔细查看图片，识别所有题目（包括题号、题干、选项、学生答案）
- 如果图片中有多页，需要识别所有页面的题目
- 题号格式可能是：1. 或 1、 或 (1) 或 一、 等
- 学生答案可能在题目下方、右侧或题目内部

**判题原则（严格）：**
- **选择题**：
  - 严格匹配答案（A/B/C/D或选项内容）
  - 如果学生写的是选项内容而非字母，需要匹配内容
  - 如果选项有多个正确答案，学生答对任意一个即可
- **填空题**：
  - 允许同义词、相近表达（如"美丽"和"漂亮"）
  - 但必须语义正确，不能有明显错误
  - 数学填空题必须数值准确
- **计算题**：
  - 检查计算过程和最终结果
  - 如果过程正确但结果错误，给部分分
  - 如果过程错误但结果正确，给部分分
- **主观题**：
  - 根据要点给分，部分正确给部分分
  - 检查答案的完整性、准确性、逻辑性

**输出格式（必须严格遵循JSON格式，只返回JSON，不要添加任何解释）：**
{
  "total_score": 总得分数字,
  "max_score": 总满分数字,
  "questions": [
    {
      "question_number": 题号数字,
      "question_type": "choice或fill或subjective或calculation",
      "question_stem": "完整的题目内容（包括选项）",
      "student_answer": "学生写的答案（完整提取，不要遗漏）",
      "correct_answer": "正确答案（如果学生答错，必须给出）",
      "score": 得分数字,
      "max_score": 满分数字,
      "is_correct": true或false布尔值,
      "feedback": "20-50字的解析说明（说明为什么对或错，给出改进建议）",
      "knowledge_point": "知识点名称（如：分数加减法、近义词辨析、一元一次方程等）"
    }
  ]
}

**判题示例：**
{
  "total_score": 85,
  "max_score": 100,
  "questions": [
    {
      "question_number": 1,
      "question_type": "choice",
      "question_stem": "下列哪个是质数？A. 4  B. 5  C. 6  D. 8",
      "student_answer": "B",
      "correct_answer": "B",
      "score": 10,
      "max_score": 10,
      "is_correct": true,
      "feedback": "答案正确。5是质数，只能被1和5整除。",
      "knowledge_point": "质数概念"
    },
    {
      "question_number": 2,
      "question_type": "fill",
      "question_stem": "2+3=___",
      "student_answer": "4",
      "correct_answer": "5",
      "score": 0,
      "max_score": 10,
      "is_correct": false,
      "feedback": "计算错误。2+3=5，不是4。建议加强基础运算练习。",
      "knowledge_point": "整数加法"
    },
    {
      "question_number": 3,
      "question_type": "subjective",
      "question_stem": "请简述春天的特点。",
      "student_answer": "春天温暖，花开了",
      "correct_answer": "春天天气温暖，万物复苏，花朵开放，树木发芽",
      "score": 6,
      "max_score": 10,
      "is_correct": false,
      "feedback": "答案部分正确，提到了温暖和花开，但不够完整。应补充万物复苏、树木发芽等特点。",
      "knowledge_point": "季节特征描述"
    }
  ]
}

**重要提醒：**
1. 必须识别图片中的所有题目，不要遗漏
2. 准确提取学生答案，不要猜测
3. 判题要严格但合理，允许合理的表达差异
4. 每题必须给出知识点标注
5. 只返回JSON格式，不要添加任何解释性文字

**现在请开始批改这份作业，确保识别所有题目并准确判题。**"""

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        解析智谱AI的响应

        Args:
            response_text: 智谱AI返回的文本

        Returns:
            解析后的结果字典
        """
        try:
            logger.info(f"开始解析响应，长度: {len(response_text)}")
            logger.debug(f"原始响应: {response_text[:500]}...")

            # 尝试多种方式提取JSON
            json_text = None

            # 方法1: 提取```json```代码块
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
                logger.info("使用方法1提取JSON（代码块）")

            # 方法2: 提取{}包裹的内容
            if not json_text:
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(0)
                    logger.info("使用方法2提取JSON（大括号）")

            # 方法3: 直接使用原文
            if not json_text:
                json_text = response_text.strip()
                logger.info("使用方法3（原文）")

            # 清理文本
            json_text = json_text.strip()

            # 解析JSON
            result = json.loads(json_text)

            # 验证结果格式
            if not isinstance(result, dict):
                raise ValueError("响应不是字典格式")

            # 如果没有questions字段，创建一个模拟结果
            if 'questions' not in result:
                logger.warning("响应中缺少questions字段，创建模拟结果")
                result = {
                    'total_score': 0,
                    'max_score': 100,
                    'questions': []
                }

            # 确保数值类型正确
            result['total_score'] = float(result.get('total_score', 0))
            result['max_score'] = float(result.get('max_score', 100))

            for q in result.get('questions', []):
                q['question_number'] = int(q.get('question_number', 0))
                q['score'] = float(q.get('score', 0))
                q['max_score'] = float(q.get('max_score', 10))
                q['is_correct'] = bool(q.get('is_correct', False))

                # 确保必需字段存在
                q.setdefault('question_type', 'subjective')
                q.setdefault('question_stem', '')
                q.setdefault('student_answer', '')
                q.setdefault('correct_answer', '')
                q.setdefault('feedback', '')

            logger.info(f"✅ 成功解析智谱AI响应: {len(result['questions'])}道题目")

            return result

        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON解析失败: {str(e)}")
            logger.error(f"原始响应: {response_text[:1000]}")

            # 返回一个友好的错误结果
            return {
                'total_score': 0,
                'max_score': 100,
                'questions': [{
                    'question_number': 1,
                    'question_type': 'subjective',
                    'question_stem': '智谱AI响应格式错误',
                    'student_answer': '',
                    'correct_answer': '',
                    'score': 0,
                    'max_score': 100,
                    'is_correct': False,
                    'feedback': f'AI返回的内容无法解析为JSON格式。原始内容: {response_text[:200]}...'
                }]
            }
        except Exception as e:
            logger.error(f"❌ 响应解析失败: {str(e)}")
            return {
                'total_score': 0,
                'max_score': 100,
                'questions': [{
                    'question_number': 1,
                    'question_type': 'subjective',
                    'question_stem': '批改失败',
                    'student_answer': '',
                    'correct_answer': '',
                    'score': 0,
                    'max_score': 100,
                    'is_correct': False,
                    'feedback': f'批改过程出错: {str(e)}'
                }]
            }
