"""
批改逻辑服务
支持选择题、填空题、主观题的自动批改
"""
import os
import logging
import re
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)


class GraderService:
    """批改服务类"""

    # 数值容差
    NUMERIC_TOLERANCE = 0.001

    def __init__(self):
        """初始化批改服务"""
        # 使用项目已有的LLM服务，按优先级尝试：DeepSeek > Groq > Tencent
        from apps.tools.services.llm_service import DeepSeekService, GroqService, TencentService

        self.llm_service = None
        self.use_project_llm = False

        # 1. 尝试DeepSeek
        try:
            deepseek = DeepSeekService()
            if deepseek.is_available():
                self.llm_service = deepseek
                self.use_project_llm = True
                logger.info("✅ 使用DeepSeek LLM服务进行主观题批改")
                return
        except Exception as e:
            logger.debug(f"DeepSeek初始化失败: {str(e)}")

        # 2. 尝试Groq
        try:
            groq = GroqService()
            if groq.is_available():
                self.llm_service = groq
                self.use_project_llm = True
                logger.info("✅ 使用Groq LLM服务进行主观题批改")
                return
        except Exception as e:
            logger.debug(f"Groq初始化失败: {str(e)}")

        # 3. 尝试腾讯混元
        try:
            tencent = TencentService()
            if tencent.is_available():
                self.llm_service = tencent
                self.use_project_llm = True
                logger.info("✅ 使用腾讯混元LLM服务进行主观题批改")
                return
        except Exception as e:
            logger.debug(f"腾讯混元初始化失败: {str(e)}")

        # 如果所有LLM都不可用，使用简单规则批改
        logger.warning("⚠️  所有LLM服务均不可用，主观题将使用简单规则批改")

    def grade_question(
        self,
        question_type: str,
        student_answer: str,
        correct_answer: str,
        question_stem: str = '',
        max_score: float = 10.0
    ) -> Dict[str, Any]:
        """
        批改单个题目

        Args:
            question_type: 题目类型 (choice, fill, subjective)
            student_answer: 学生答案
            correct_answer: 正确答案
            question_stem: 题干
            max_score: 满分

        Returns:
            批改结果字典
        """
        if question_type == 'choice':
            return self._grade_choice(student_answer, correct_answer, max_score)
        elif question_type == 'fill':
            return self._grade_fill(student_answer, correct_answer, max_score)
        elif question_type == 'subjective':
            return self._grade_subjective(student_answer, correct_answer, question_stem, max_score)
        else:
            return {
                'is_correct': False,
                'score': 0.0,
                'max_score': max_score,
                'feedback': f'未知题目类型: {question_type}'
            }

    def _grade_choice(self, student_answer: str, correct_answer: str, max_score: float) -> Dict[str, Any]:
        """
        批改选择题

        Args:
            student_answer: 学生答案
            correct_answer: 正确答案
            max_score: 满分

        Returns:
            批改结果
        """
        # 标准化答案（去除空格、转大写）
        student = self._normalize_choice_answer(student_answer)
        correct = self._normalize_choice_answer(correct_answer)

        is_correct = student == correct
        score = max_score if is_correct else 0.0

        feedback = '回答正确！' if is_correct else f'回答错误。正确答案是: {correct_answer}'

        return {
            'is_correct': is_correct,
            'score': score,
            'max_score': max_score,
            'feedback': feedback
        }

    def _grade_fill(self, student_answer: str, correct_answer: str, max_score: float) -> Dict[str, Any]:
        """
        批改填空题

        Args:
            student_answer: 学生答案
            correct_answer: 正确答案
            max_score: 满分

        Returns:
            批改结果
        """
        # 尝试数值比较
        numeric_result = self._compare_numeric(student_answer, correct_answer)
        if numeric_result is not None:
            is_correct = numeric_result
            score = max_score if is_correct else 0.0
            feedback = '数值正确！' if is_correct else f'数值错误。正确答案是: {correct_answer}'
            return {
                'is_correct': is_correct,
                'score': score,
                'max_score': max_score,
                'feedback': feedback
            }

        # 尝试数学表达式比较
        math_result = self._compare_math_expression(student_answer, correct_answer)
        if math_result is not None:
            is_correct = math_result
            score = max_score if is_correct else 0.0
            feedback = '表达式等价！' if is_correct else f'表达式不等价。正确答案是: {correct_answer}'
            return {
                'is_correct': is_correct,
                'score': score,
                'max_score': max_score,
                'feedback': feedback
            }

        # 字符串比较（标准化标点符号）
        student = self._normalize_text(student_answer)
        correct = self._normalize_text(correct_answer)

        is_correct = student == correct
        score = max_score if is_correct else 0.0

        # 部分匹配给部分分数
        if not is_correct and student in correct:
            score = max_score * 0.5
            feedback = f'部分正确（得分{score}分）。完整答案是: {correct_answer}'
        else:
            feedback = '回答正确！' if is_correct else f'回答错误。正确答案是: {correct_answer}'

        return {
            'is_correct': is_correct,
            'score': score,
            'max_score': max_score,
            'feedback': feedback
        }

    def _grade_subjective(
        self,
        student_answer: str,
        correct_answer: str,
        question_stem: str,
        max_score: float
    ) -> Dict[str, Any]:
        """
        批改主观题（使用项目LLM服务）

        Args:
            student_answer: 学生答案
            correct_answer: 正确答案
            question_stem: 题干
            max_score: 满分

        Returns:
            批改结果
        """
        if not self.use_project_llm:
            logger.warning("LLM服务未配置，使用简单规则批改")
            return self._simple_subjective_grading(student_answer, correct_answer, max_score)

        try:
            # 构建LLM提示词
            prompt = self._build_grading_prompt(question_stem, correct_answer, student_answer, max_score)
            system_prompt = '你是一位专业的教师，负责批改学生作业。'

            # 调用项目LLM服务
            llm_response = self.llm_service.generate_content(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=500
            )

            if llm_response:
                # 解析LLM返回结果
                return self._parse_llm_grading(llm_response, max_score)
            else:
                logger.error("LLM服务返回空结果")
                return self._simple_subjective_grading(student_answer, correct_answer, max_score)

        except Exception as e:
            logger.error(f"LLM批改失败: {str(e)}")
            return self._simple_subjective_grading(student_answer, correct_answer, max_score)

    def _build_grading_prompt(
        self,
        question_stem: str,
        correct_answer: str,
        student_answer: str,
        max_score: float
    ) -> str:
        """
        构建LLM批改提示词

        Args:
            question_stem: 题干
            correct_answer: 标准答案
            student_answer: 学生答案
            max_score: 满分

        Returns:
            提示词
        """
        return f"""请根据标准答案与学生作答进行对比，从以下三个方面给出评分和反馈：

1. 逻辑结构（是否条理清晰）
2. 关键步骤（是否包含重要知识点）
3. 观点准确性（是否符合标准答案）

题目：{question_stem}

标准答案：{correct_answer}

学生答案：{student_answer}

满分：{max_score}分

请按以下格式返回：
得分：X分
评价：[简短评价]
反馈：[详细反馈，指出优点和不足]
"""

    def _parse_llm_grading(self, llm_response: str, max_score: float) -> Dict[str, Any]:
        """
        解析LLM批改结果

        Args:
            llm_response: LLM返回的文本
            max_score: 满分

        Returns:
            批改结果
        """
        # 提取得分
        score_match = re.search(r'得分[：:]\s*(\d+(?:\.\d+)?)', llm_response)
        if score_match:
            score = float(score_match.group(1))
            score = min(score, max_score)  # 确保不超过满分
        else:
            score = max_score * 0.5  # 默认给一半分数

        is_correct = score >= max_score * 0.8  # 80%以上算正确

        # 提取反馈
        feedback_match = re.search(r'反馈[：:]\s*(.+?)(?=\n\n|\Z)', llm_response, re.DOTALL)
        if feedback_match:
            feedback = feedback_match.group(1).strip()
        else:
            feedback = llm_response

        return {
            'is_correct': is_correct,
            'score': score,
            'max_score': max_score,
            'feedback': feedback,
            'llm_analysis': {
                'raw_response': llm_response,
                'score': score,
                'max_score': max_score
            }
        }

    def _simple_subjective_grading(
        self,
        student_answer: str,
        correct_answer: str,
        max_score: float
    ) -> Dict[str, Any]:
        """
        简单的主观题批改（基于关键词匹配）

        Args:
            student_answer: 学生答案
            correct_answer: 正确答案
            max_score: 满分

        Returns:
            批改结果
        """
        # 提取关键词（简单实现：分词后取长度>2的词）
        correct_keywords = set([w for w in re.findall(r'\w+', correct_answer) if len(w) > 2])
        student_keywords = set([w for w in re.findall(r'\w+', student_answer) if len(w) > 2])

        # 计算关键词匹配率
        if not correct_keywords:
            match_rate = 0.5
        else:
            matched = correct_keywords & student_keywords
            match_rate = len(matched) / len(correct_keywords)

        score = max_score * match_rate
        is_correct = match_rate >= 0.8

        feedback = f'关键词匹配率: {match_rate*100:.1f}%。'
        if is_correct:
            feedback += '回答较为完整。'
        elif match_rate >= 0.5:
            feedback += '回答部分正确，但不够完整。'
        else:
            feedback += '回答不够准确，请参考标准答案。'

        return {
            'is_correct': is_correct,
            'score': score,
            'max_score': max_score,
            'feedback': feedback
        }

    def _normalize_choice_answer(self, answer: str) -> str:
        """
        标准化选择题答案

        Args:
            answer: 原始答案

        Returns:
            标准化后的答案
        """
        # 去除空格、转大写、只保留字母
        normalized = ''.join([c.upper() for c in answer if c.isalpha()])
        return normalized

    def _normalize_text(self, text: str) -> str:
        """
        标准化文本（统一标点符号）

        Args:
            text: 原始文本

        Returns:
            标准化后的文本
        """
        # 中文标点转英文标点
        punctuation_map = {
            '，': ',',
            '。': '.',
            '！': '!',
            '？': '?',
            '；': ';',
            '：': ':',
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            '（': '(',
            '）': ')',
            '【': '[',
            '】': ']'
        }

        for cn, en in punctuation_map.items():
            text = text.replace(cn, en)

        # 去除多余空格
        text = ' '.join(text.split())

        return text.strip()

    def _compare_numeric(self, value1: str, value2: str) -> Optional[bool]:
        """
        比较两个数值是否相等（带容差）

        Args:
            value1: 数值1
            value2: 数值2

        Returns:
            是否相等，如果不是数值则返回None
        """
        try:
            num1 = float(value1)
            num2 = float(value2)
            return abs(num1 - num2) <= self.NUMERIC_TOLERANCE
        except (ValueError, TypeError):
            return None

    def _compare_math_expression(self, expr1: str, expr2: str) -> Optional[bool]:
        """
        比较两个数学表达式是否等价

        Args:
            expr1: 表达式1
            expr2: 表达式2

        Returns:
            是否等价，如果无法比较则返回None
        """
        try:
            from sympy import simplify, sympify
            from sympy.parsing.sympy_parser import parse_expr

            # 解析表达式
            parsed1 = parse_expr(expr1)
            parsed2 = parse_expr(expr2)

            # 化简并比较
            diff = simplify(parsed1 - parsed2)
            return diff == 0

        except ImportError:
            logger.debug("sympy未安装，跳过数学表达式比较")
            return None
        except Exception as e:
            logger.debug(f"数学表达式比较失败: {str(e)}")
            return None
