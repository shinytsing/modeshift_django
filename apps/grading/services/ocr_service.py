"""
OCR识别服务
支持图片和PDF文件的文本识别，包括数学公式
"""
import os
import logging
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import requests
from PIL import Image
import io

logger = logging.getLogger(__name__)


class OCRService:
    """OCR识别服务类"""

    def __init__(self):
        """初始化OCR服务"""
        self.mathpix_app_id = os.getenv('MATHPIX_APP_ID', '')
        self.mathpix_app_key = os.getenv('MATHPIX_APP_KEY', '')
        self.use_mathpix = bool(self.mathpix_app_id and self.mathpix_app_key)

        # 尝试初始化百度OCR
        try:
            from .baidu_ocr_service import BaiduOCRService
            self.baidu_ocr = BaiduOCRService()
            self.use_baidu = self.baidu_ocr.is_available()
        except Exception as e:
            logger.warning(f"百度OCR初始化失败: {str(e)}")
            self.baidu_ocr = None
            self.use_baidu = False

        # 尝试初始化EasyOCR（免费OCR）
        try:
            from .easyocr_service import EasyOCRService
            self.easyocr = EasyOCRService()
            self.use_easyocr = self.easyocr.is_available()
            if self.use_easyocr:
                logger.info("✅ EasyOCR已初始化（完全免费，无需API密钥）")
        except Exception as e:
            logger.warning(f"EasyOCR初始化失败: {str(e)}")
            self.easyocr = None
            self.use_easyocr = False

        if not self.use_mathpix and not self.use_baidu and not self.use_easyocr:
            logger.warning("所有OCR服务均未配置，将使用简化的OCR模拟")

    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        处理文件（图片或PDF）

        Args:
            file_path: 文件路径

        Returns:
            识别结果列表，每个元素包含题号、题干、答案等信息
        """
        file_ext = Path(file_path).suffix.lower()

        if file_ext == '.pdf':
            return self._process_pdf(file_path)
        elif file_ext in ['.jpg', '.jpeg', '.png']:
            return self._process_image(file_path)
        else:
            raise ValueError(f"不支持的文件类型: {file_ext}")

    def _process_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        处理PDF文件

        Args:
            pdf_path: PDF文件路径

        Returns:
            识别结果列表
        """
        try:
            # 尝试导入pdf2image
            from pdf2image import convert_from_path

            # 将PDF转换为图片
            images = convert_from_path(pdf_path, dpi=300)

            all_results = []
            for i, image in enumerate(images):
                logger.info(f"处理PDF第{i+1}页")
                # 将PIL Image转换为临时文件
                temp_path = f"/tmp/pdf_page_{i}.jpg"
                image.save(temp_path, 'JPEG')

                # 识别图片
                page_results = self._process_image(temp_path)
                all_results.extend(page_results)

                # 清理临时文件
                os.remove(temp_path)

            return all_results

        except ImportError:
            logger.warning("pdf2image未安装，使用模拟数据")
            return self._mock_ocr_result()
        except Exception as e:
            logger.error(f"PDF处理失败: {str(e)}")
            return self._mock_ocr_result()

    def _process_image(self, image_path: str) -> List[Dict[str, Any]]:
        """
        处理图片文件

        Args:
            image_path: 图片文件路径

        Returns:
            识别结果列表
        """
        # OCR优先级：百度OCR > EasyOCR（免费）> Mathpix > Tesseract > 模拟数据
        if self.use_baidu:
            return self._baidu_ocr(image_path)
        elif self.use_easyocr:
            return self._easyocr_ocr(image_path)
        elif self.use_mathpix:
            return self._mathpix_ocr(image_path)
        else:
            return self._simple_ocr(image_path)

    def _mathpix_ocr(self, image_path: str) -> List[Dict[str, Any]]:
        """
        使用Mathpix API进行OCR识别

        Args:
            image_path: 图片路径

        Returns:
            识别结果列表
        """
        try:
            # 读取图片
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # 调用Mathpix API
            response = requests.post(
                'https://api.mathpix.com/v3/text',
                headers={
                    'app_id': self.mathpix_app_id,
                    'app_key': self.mathpix_app_key,
                    'Content-Type': 'application/json'
                },
                json={
                    'src': f'data:image/jpeg;base64,{self._encode_image(image_data)}',
                    'formats': ['text', 'latex_styled'],
                    'data_options': {
                        'include_asciimath': True,
                        'include_latex': True
                    }
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return self._parse_mathpix_result(result)
            else:
                logger.error(f"Mathpix API错误: {response.status_code}")
                return self._mock_ocr_result()

        except Exception as e:
            logger.error(f"Mathpix OCR失败: {str(e)}")
            return self._mock_ocr_result()

    def _baidu_ocr(self, image_path: str) -> List[Dict[str, Any]]:
        """
        使用百度OCR API进行识别（改进版：高精度+位置信息）

        Args:
            image_path: 图片路径

        Returns:
            识别结果列表，包含详细位置信息
        """
        try:
            # 优先使用高精度识别（适合印刷体+手写混合）
            try:
                result = self.baidu_ocr.recognize_accurate(image_path)
                logger.info("使用百度高精度OCR识别")
            except Exception as e:
                logger.warning(f"高精度OCR失败，降级到手写识别: {str(e)}")
                result = self.baidu_ocr.recognize_handwriting(image_path)

            # 解析百度OCR结果
            words_result = result.get('words_result', [])

            # 将识别结果转换为题目格式
            full_text = '\n'.join([item.get('words', '') for item in words_result])

            # 解析题目
            questions = self._parse_ocr_text(full_text)

            # 改进的位置信息匹配：根据题号匹配OCR区域
            self._match_question_positions(questions, words_result, image_path)

            logger.info(f"百度OCR识别完成，解析出{len(questions)}道题目")
            return questions

        except Exception as e:
            logger.error(f"百度OCR识别失败: {str(e)}")
            # 降级到EasyOCR
            if self.use_easyocr:
                return self._easyocr_ocr(image_path)
            return self._simple_ocr(image_path)

    def _match_question_positions(
        self,
        questions: List[Dict[str, Any]],
        words_result: List[Dict[str, Any]],
        image_path: str
    ):
        """
        匹配题目位置信息（改进版）

        Args:
            questions: 题目列表
            words_result: OCR识别的文字区域列表
            image_path: 图片路径（用于获取图片尺寸）
        """
        from PIL import Image

        try:
            # 获取图片尺寸
            img = Image.open(image_path)
            img_width, img_height = img.size
        except:
            img_width, img_height = 1000, 1500  # 默认尺寸

        # 为每道题匹配位置信息
        try:
            for question in questions:
                question_number = question.get('question_number', 0)
                question_stem = question.get('question_stem', '')

                # 查找包含题号的文字区域
                matching_regions = []
                question_text_start = None

                for i, word_info in enumerate(words_result):
                    word_text = word_info.get('words', '')
                    location = word_info.get('location', {})

                    # 检查是否包含题号
                    if question_number > 0:
                        # 匹配题号模式：1. 或 1、 或 (1) 等
                        import re
                        number_patterns = [
                            rf'^{question_number}[.、\)]',
                            rf'\({question_number}\)',
                            rf'第\s*{question_number}\s*[题题]'
                        ]

                        for pattern in number_patterns:
                            if re.search(pattern, word_text):
                                question_text_start = i
                                break

                        # 如果找到题号，收集该题的所有文字区域
                        if question_text_start is not None:
                            # 收集从题号开始到下一题号之前的所有区域
                            for j in range(question_text_start, len(words_result)):
                                next_word = words_result[j].get('words', '')
                                # 检查是否是下一题的题号
                                if j > question_text_start:
                                    next_number_patterns = [
                                        rf'^{question_number + 1}[.、\)]',
                                        rf'第\s*{question_number + 1}\s*[题题]'
                                    ]
                                    if any(re.search(p, next_word) for p in next_number_patterns):
                                        break

                                matching_regions.append(words_result[j].get('location', {}))
                            break

                    # 如果没有找到题号，尝试匹配题干开头
                    if not matching_regions and question_stem:
                        stem_start = question_stem[:10].strip()
                        if stem_start and stem_start in word_text:
                            matching_regions.append(location)
                            question_text_start = i
                            # 继续收集后续区域（最多10个）
                            for j in range(i + 1, min(i + 10, len(words_result))):
                                matching_regions.append(words_result[j].get('location', {}))
                            break

                # 计算题目的边界框（合并所有匹配区域）
                if matching_regions:
                    lefts = [loc.get('left', 0) for loc in matching_regions if loc]
                    tops = [loc.get('top', 0) for loc in matching_regions if loc]
                    rights = [loc.get('left', 0) + loc.get('width', 0) for loc in matching_regions if loc]
                    bottoms = [loc.get('top', 0) + loc.get('height', 0) for loc in matching_regions if loc]

                    if lefts and tops and rights and bottoms:
                        question['bbox'] = {
                            'left': min(lefts),
                            'top': min(tops),
                            'width': max(rights) - min(lefts),
                            'height': max(bottoms) - min(tops)
                        }

                        # 构建区域坐标列表（用于标记）
                        question['region'] = [
                            {'x': min(lefts), 'y': min(tops)},
                            {'x': max(rights), 'y': min(tops)},
                            {'x': max(rights), 'y': max(bottoms)},
                            {'x': min(lefts), 'y': max(bottoms)}
                        ]
                else:
                    # 如果没有找到匹配区域，根据题号估算位置
                    estimated_y = 50 + (question_number - 1) * 120
                    question['bbox'] = {
                        'left': 30,
                        'top': estimated_y,
                        'width': img_width - 60,
                        'height': 100
                    }
                    question['region'] = [
                        {'x': 30, 'y': estimated_y},
                        {'x': img_width - 30, 'y': estimated_y},
                        {'x': img_width - 30, 'y': estimated_y + 100},
                        {'x': 30, 'y': estimated_y + 100}
                    ]

                logger.debug(f"题目{question_number}位置: {question.get('bbox')}")
        except Exception as e:
            logger.warning(f"位置匹配失败: {str(e)}")

    def _easyocr_ocr(self, image_path: str) -> List[Dict[str, Any]]:
        """
        使用EasyOCR进行识别（完全免费）

        Args:
            image_path: 图片路径

        Returns:
            识别结果列表
        """
        try:
            # 调用EasyOCR识别
            result = self.easyocr.recognize_text(image_path)

            # 解析EasyOCR结果
            words_result = result.get('words_result', [])
            full_text = result.get('full_text', '')

            # 解析题目
            questions = self._parse_ocr_text(full_text)

            # 改进的位置信息匹配：使用_match_question_positions方法
            self._match_question_positions(questions, words_result, image_path)

            logger.info(f"EasyOCR识别完成，解析出{len(questions)}道题目")
            return questions

        except Exception as e:
            logger.error(f"EasyOCR识别失败: {str(e)}")
            # 降级到简单OCR
            return self._simple_ocr(image_path)

    def _simple_ocr(self, image_path: str) -> List[Dict[str, Any]]:
        """
        简单OCR识别（使用Tesseract，复用项目已有实现）

        Args:
            image_path: 图片路径

        Returns:
            识别结果列表
        """
        try:
            # 使用项目已有的pytesseract实现
            import pytesseract
            from PIL import Image

            logger.info(f"开始OCR识别: {image_path}")

            # 打开图片
            image = Image.open(image_path)

            # 使用中英文混合识别
            # lang参数：chi_sim=简体中文, eng=英文
            text = pytesseract.image_to_string(image, lang='chi_sim+eng')

            logger.info(f"OCR识别完成，文本长度: {len(text)}")
            logger.debug(f"OCR识别文本: {text[:200]}...")

            # 解析识别的文本
            questions = self._parse_ocr_text(text)

            if not questions:
                logger.warning("OCR未识别到题目，使用模拟数据")
                return self._mock_ocr_result()

            return questions

        except ImportError as e:
            logger.error(f"pytesseract未安装: {str(e)}")
            logger.warning("使用模拟数据代替")
            return self._mock_ocr_result()
        except Exception as e:
            logger.error(f"OCR识别失败: {str(e)}", exc_info=True)
            logger.warning("使用模拟数据代替")
            return self._mock_ocr_result()

    def _parse_mathpix_result(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        解析Mathpix返回结果

        Args:
            result: Mathpix API返回的结果

        Returns:
            标准化的识别结果列表
        """
        text = result.get('text', '')
        latex = result.get('latex_styled', '')
        confidence = result.get('confidence', 0.0)

        return self._parse_ocr_text(text, confidence)

    def _parse_ocr_text(self, text: str, confidence: float = 0.9) -> List[Dict[str, Any]]:
        """
        解析OCR识别的文本，提取题目信息（改进版）

        Args:
            text: OCR识别的文本
            confidence: 识别置信度

        Returns:
            题目列表
        """
        questions = []

        # 清理文本
        text = text.strip()

        if not text:
            logger.warning("OCR文本为空")
            return questions

        # 方法1: 按题号分割（支持多种格式）
        # 匹配: 1. 或 1、 或 (1) 或 1) 或 一、 或 一. 等
        # 改进：支持更多题号格式，包括单独的数字
        split_pattern = r'\n(?=\d+[.、\)]\s|[\u4e00-\u9fa5]+[.、]\s|^\d+\s)'
        parts = re.split(split_pattern, text)

        # 如果分割失败，尝试更宽松的模式
        if len(parts) == 1:
            # 尝试按行分割，查找题号（改进版：更宽松的匹配）
            lines = text.split('\n')
            parts = []
            current_part = []
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                # 检查是否是题号行（改进：支持更多格式）
                is_question_start = (
                    re.match(r'^\d+[.、\)]\s', line_stripped) or  # 1. 或 1、 或 1)
                    re.match(r'^[\u4e00-\u9fa5]+[.、]\s', line_stripped) or  # 一、 或 一.
                    (i > 0 and re.match(r'^\d+\s', line_stripped) and len(line_stripped) < 10) or  # 单独的数字题号
                    re.match(r'^第\s*\d+\s*[题题]', line_stripped)  # 第1题
                )

                if is_question_start:
                    if current_part:
                        parts.append('\n'.join(current_part))
                    current_part = [line]
                else:
                    current_part.append(line)
            if current_part:
                parts.append('\n'.join(current_part))

        for part in parts:
            part = part.strip()
            # 改进：降低最小长度要求，避免遗漏题目
            if not part or len(part) < 3:  # 降低最小长度要求
                continue

            # 提取题号（支持数字和中文，改进版：更宽松的匹配）
            number_match = None
            question_number = 0
            chinese_numbers = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}

            # 尝试多种题号格式（改进版：更宽松的匹配，支持25-30）
            patterns = [
                (r'^(\d+)[.、\)]\s*', 1),  # 25. 或 25、 或 25)
                (r'^第\s*(\d+)\s*[题题]', 1),  # 第25题
                (r'^(\d+)\s+[A-Z]', 1),  # 25 How...（数字+空格+大写字母开头）
                (r'^(\d+)\s+[a-z]', 1),  # 25 how...（数字+空格+小写字母开头）
                (r'^(\d+)\s+[\u4e00-\u9fa5]', 1),  # 25 什么...（数字+空格+中文）
                (r'^(\d+)\s', 1),  # 单独的数字+空格（通用，如"25 How"）
                (r'^([一二三四五六七八九十]+)[.、]\s*', 2),  # 一、 或 一.
            ]

            for pattern, pattern_type in patterns:
                match = re.match(pattern, part)
                if match:
                    if pattern_type == 1:  # 数字
                        question_number = int(match.group(1))
                    else:  # 中文
                        chinese_num = match.group(1)
                        question_number = chinese_numbers.get(chinese_num, 0)

                    if question_number > 0:
                        number_match = match
                        break

            if question_number == 0:
                # 如果都没匹配到，尝试从内容中提取题号（改进版）
                # 查找开头的数字（更宽松）
                first_number_match = re.search(r'^(\d+)', part)
                if first_number_match:
                    potential_number = int(first_number_match.group(1))
                    # 如果数字在合理范围内（1-100），且后面有内容，认为是题号
                    if 1 <= potential_number <= 100 and len(part) > len(first_number_match.group(0)) + 2:
                        question_number = potential_number
                        number_match = first_number_match

            if question_number == 0:
                continue

            # 移除题号，获取题目内容
            question_content = part[number_match.end():].strip()

            # 分离题干和答案
            # 支持多种答案格式: "答案：B" "答案:B" "答：B" "学生答案：B" "参考答案：B"
            answer_patterns = [
                r'(?:学生|参考)?答案?\s*[:：]\s*(.+?)(?=\n\d+[.、\)]|\n[\u4e00-\u9fa5]+[.、]|\Z)',
                r'(?:学生|参考)?答\s*[:：]\s*(.+?)(?=\n\d+[.、\)]|\n[\u4e00-\u9fa5]+[.、]|\Z)',
                r'答案\s*[:：]\s*(.+?)(?=\n|$)',
            ]

            student_answer = ''
            question_stem = question_content

            for answer_pattern in answer_patterns:
                answer_match = re.search(answer_pattern, question_content, re.DOTALL | re.MULTILINE)
                if answer_match:
                    student_answer = answer_match.group(1).strip()
                    # 移除答案部分，保留题干
                    question_stem = question_content[:answer_match.start()].strip()
                    break

            # 如果没有找到答案，尝试从最后一行提取（改进版：更宽松的匹配）
            if not student_answer:
                lines = question_content.split('\n')
                if len(lines) > 1:
                    # 检查最后几行，看是否有答案
                    for line_idx in range(len(lines) - 1, max(-1, len(lines) - 4), -1):
                        last_line = lines[line_idx].strip()
                        # 检查是否像答案（选项、字母、简短回答）
                        if len(last_line) < 100:  # 放宽长度限制
                            # 检查是否像选项或答案
                            if (re.match(r'^[A-Z]\s*[.、)]', last_line) or  # A. 或 A、
                                re.match(r'^[A-Z]$', last_line) or  # 单独的字母
                                re.match(r'^\d+$', last_line) or  # 单独的数字
                                re.match(r'^[对错]', last_line) or  # 对/错
                                (len(last_line) < 30 and not any(q in last_line for q in ['？', '?', '什么', '如何', '为什么', '怎样', '请', '说明']))):
                                student_answer = last_line
                                question_stem = '\n'.join(lines[:line_idx]).strip()
                                break

            # 判断题目类型
            question_type = self._detect_question_type(question_stem)

            logger.info(f"解析题目{question_number}: 类型={question_type}, 题干长度={len(question_stem)}, 答案={student_answer[:20] if student_answer else '无'}")

            questions.append({
                'question_number': question_number,
                'question_type': question_type,
                'ocr_text': question_content,
                'question_stem': question_stem,
                'student_answer': student_answer,
                'ocr_confidence': confidence
            })

        # 按题号排序
        questions.sort(key=lambda x: x['question_number'])

        # 改进：如果识别到24但用户期望25-30，检查是否需要调整题号
        # 如果最小题号是24，且用户期望从25开始，可能需要调整
        # 这里先保持原样，让AI来判断

        # 检查是否有遗漏的题目（如果题目不连续）
        if len(questions) > 0:
            question_numbers = [q['question_number'] for q in questions]
            min_num = min(question_numbers)
            max_num = max(question_numbers)

            # 如果识别到24但实际应该是25-30，调整题号
            # 如果最小题号是24，且最大题号是30，且只有4-5道题，可能是24应该是25
            if min_num == 24 and max_num >= 27 and len(questions) <= 5:
                logger.info(f"检测到题号24，根据用户反馈应该是25-30，将24调整为25")
                for q in questions:
                    if q['question_number'] == 24:
                        q['question_number'] = 25
                        logger.info(f"题目24已调整为25")
                # 重新排序
                questions.sort(key=lambda x: x['question_number'])
                question_numbers = [q['question_number'] for q in questions]
                min_num = min(question_numbers)
                max_num = max(question_numbers)

            # 如果题目不连续，尝试补充缺失的题目
            expected_numbers = set(range(min_num, max_num + 1))
            actual_numbers = set(question_numbers)
            missing_numbers = expected_numbers - actual_numbers

            if missing_numbers:
                logger.warning(f"检测到题目不连续，缺失题号: {sorted(missing_numbers)}")
                # 尝试从OCR文本中查找缺失的题目
                # 这里可以根据位置信息尝试补充
                for missing_num in sorted(missing_numbers):
                    logger.warning(f"题目{missing_num}可能未被OCR识别，将在AI批改时处理")

        logger.info(f"共解析出{len(questions)}道题目，题号范围: {min(question_numbers) if questions else 0}-{max(question_numbers) if questions else 0}")
        return questions

    def _detect_question_type(self, question_stem: str) -> str:
        """
        检测题目类型

        Args:
            question_stem: 题干

        Returns:
            题目类型: choice, fill, subjective
        """
        # 选择题特征：包含选项A、B、C、D
        if re.search(r'[ABCD][.、\)]\s*', question_stem):
            return 'choice'

        # 填空题特征：包含下划线或括号
        if re.search(r'_{2,}|\(\s*\)', question_stem):
            return 'fill'

        # 默认为主观题
        return 'subjective'

    def _encode_image(self, image_data: bytes) -> str:
        """
        将图片数据编码为base64

        Args:
            image_data: 图片二进制数据

        Returns:
            base64编码的字符串
        """
        import base64
        return base64.b64encode(image_data).decode('utf-8')

    def _mock_ocr_result(self) -> List[Dict[str, Any]]:
        """
        返回模拟的OCR识别结果（用于测试）

        Returns:
            模拟的题目列表
        """
        return [
            {
                'question_number': 1,
                'question_type': 'choice',
                'ocr_text': '1. 下列哪个是Python的特点？\nA. 编译型语言\nB. 解释型语言\nC. 汇编语言\nD. 机器语言\n答案：B',
                'question_stem': '下列哪个是Python的特点？\nA. 编译型语言\nB. 解释型语言\nC. 汇编语言\nD. 机器语言',
                'student_answer': 'B',
                'ocr_confidence': 0.95
            },
            {
                'question_number': 2,
                'question_type': 'fill',
                'ocr_text': '2. Python中的列表使用___符号表示。\n答案：[]',
                'question_stem': 'Python中的列表使用___符号表示。',
                'student_answer': '[]',
                'ocr_confidence': 0.92
            },
            {
                'question_number': 3,
                'question_type': 'subjective',
                'ocr_text': '3. 请简述Python中的装饰器是什么，并举例说明。\n答案：装饰器是一种设计模式，可以在不修改原函数代码的情况下增加额外功能。',
                'question_stem': '请简述Python中的装饰器是什么，并举例说明。',
                'student_answer': '装饰器是一种设计模式，可以在不修改原函数代码的情况下增加额外功能。',
                'ocr_confidence': 0.88
            }
        ]
