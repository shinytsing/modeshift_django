"""
题库系统交互服务
与外部题库系统进行交互，获取题目信息和相似题推荐
"""
import os
import logging
from typing import Dict, Any, List, Optional
import requests

logger = logging.getLogger(__name__)


class QuestionBankService:
    """题库系统交互服务类"""

    def __init__(self):
        """初始化题库服务"""
        self.api_base_url = os.getenv('QUESTION_BANK_API_URL', 'http://localhost:8080/api/questions')
        self.api_key = os.getenv('QUESTION_BANK_API_KEY', '')
        self.timeout = 30
        # 使用mock模式（题库系统未部署时）
        self.use_mock = os.getenv('USE_MOCK_QUESTION_BANK', 'true').lower() == 'true'

    def match_question(self, question_stem: str, question_type: str = '') -> Optional[Dict[str, Any]]:
        """
        根据题干匹配题库中的题目

        Args:
            question_stem: 题干文本
            question_type: 题目类型（可选）

        Returns:
            匹配到的题目信息，如果未匹配到则返回None
        """
        # 使用mock数据
        if self.use_mock:
            logger.info(f"使用Mock数据匹配题目: {question_stem[:30]}...")
            return self._mock_question_data(question_stem, question_type)

        try:
            url = f"{self.api_base_url}/match"
            headers = self._get_headers()

            payload = {
                'question_stem': question_stem,
                'question_type': question_type
            }

            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)

            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('data'):
                    return result['data']
                else:
                    logger.info(f"未匹配到题目: {question_stem[:50]}...")
                    return None
            else:
                logger.warning(f"题目匹配API返回错误: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"题目匹配请求失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"题目匹配异常: {str(e)}")
            return None

    def get_question_answer(self, question_id: str) -> Optional[Dict[str, Any]]:
        """
        获取题目的正确答案

        Args:
            question_id: 题目ID

        Returns:
            题目答案信息
        """
        try:
            url = f"{self.api_base_url}/{question_id}/answer"
            headers = self._get_headers()

            response = requests.get(url, headers=headers, timeout=self.timeout)

            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('data'):
                    return result['data']
                else:
                    logger.warning(f"未找到题目答案: {question_id}")
                    return None
            else:
                logger.warning(f"获取答案API返回错误: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"获取答案请求失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取答案异常: {str(e)}")
            return None

    def find_similar_questions(
        self,
        question_id: str = '',
        question_stem: str = '',
        knowledge_points: List[str] = None,
        difficulty: str = '',
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        查找相似题目

        Args:
            question_id: 原题目ID（可选）
            question_stem: 题干（可选）
            knowledge_points: 知识点列表（可选）
            difficulty: 难度（可选）
            limit: 返回数量限制

        Returns:
            相似题目列表
        """
        # 使用mock数据
        if self.use_mock:
            logger.info(f"使用Mock数据查询相似题: {question_id or question_stem[:30]}...")
            return self._mock_similar_questions()[:limit]

        try:
            url = f"{self.api_base_url}/similar"
            headers = self._get_headers()

            payload = {
                'question_id': question_id,
                'question_stem': question_stem,
                'knowledge_points': knowledge_points or [],
                'difficulty': difficulty,
                'limit': limit
            }

            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)

            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('data'):
                    return result['data']
                else:
                    logger.info("未找到相似题目")
                    return []
            else:
                logger.warning(f"相似题查询API返回错误: {response.status_code}")
                return []

        except requests.exceptions.RequestException as e:
            logger.error(f"相似题查询请求失败: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"相似题查询异常: {str(e)}")
            return []

    def batch_find_similar_questions(
        self,
        question_ids: List[str],
        limit_per_question: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        批量查找相似题目

        Args:
            question_ids: 题目ID列表
            limit_per_question: 每个题目返回的相似题数量

        Returns:
            字典，key为原题目ID，value为相似题列表
        """
        result = {}

        for question_id in question_ids:
            similar_questions = self.find_similar_questions(
                question_id=question_id,
                limit=limit_per_question
            )
            result[question_id] = similar_questions

        return result

    def _get_headers(self) -> Dict[str, str]:
        """
        获取API请求头

        Returns:
            请求头字典
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        return headers

    def _mock_question_data(self, question_stem: str, question_type: str = '') -> Dict[str, Any]:
        """
        返回模拟的题目数据（用于测试）

        Args:
            question_stem: 题干
            question_type: 题目类型

        Returns:
            模拟的题目数据
        """
        # 根据题干内容返回对应的答案
        import hashlib
        question_hash = hashlib.md5(question_stem.encode()).hexdigest()[:8]

        # 模拟不同类型题目的答案
        if 'Python' in question_stem or '解释型' in question_stem:
            answer = 'B'
        elif '列表' in question_stem or '[]' in question_stem:
            answer = '[]'
        elif '装饰器' in question_stem:
            answer = '装饰器是一种设计模式，用于在不修改原函数代码的情况下增加额外功能。'
        else:
            answer = 'A'

        return {
            'id': f'mock_question_{question_hash}',
            'question_stem': question_stem,
            'question_type': question_type or 'choice',
            'answer': answer,
            'explanation': '这是模拟的答案解析',
            'difficulty': 'medium',
            'knowledge_points': ['Python基础', '数据类型']
        }

    def _mock_similar_questions(self) -> List[Dict[str, Any]]:
        """
        返回模拟的相似题目数据（用于测试）

        Returns:
            模拟的相似题目列表
        """
        return [
            {
                'id': 'similar_001',
                'question_stem': '下列哪个不是Python的数据类型？\nA. list\nB. tuple\nC. array\nD. dict',
                'question_type': 'choice',
                'answer': 'C',
                'difficulty': 'easy',
                'knowledge_points': ['Python基础', '数据类型'],
                'similarity_score': 0.85
            },
            {
                'id': 'similar_002',
                'question_stem': 'Python中哪个关键字用于定义函数？\nA. func\nB. def\nC. function\nD. define',
                'question_type': 'choice',
                'answer': 'B',
                'difficulty': 'easy',
                'knowledge_points': ['Python基础', '函数'],
                'similarity_score': 0.75
            },
            {
                'id': 'similar_003',
                'question_stem': 'Python的缩进通常使用几个空格？\nA. 2\nB. 4\nC. 6\nD. 8',
                'question_type': 'choice',
                'answer': 'B',
                'difficulty': 'easy',
                'knowledge_points': ['Python基础', '代码规范'],
                'similarity_score': 0.65
            }
        ]
