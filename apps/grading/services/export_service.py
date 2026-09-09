"""
试卷导出服务
支持导出为PDF和JPG格式
"""
import os
import logging
from typing import List, Dict, Any, Tuple
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import textwrap

logger = logging.getLogger(__name__)


class ExportService:
    """试卷导出服务类"""

    # A4纸张尺寸（像素，300 DPI）
    A4_WIDTH_PX = 2480
    A4_HEIGHT_PX = 3508

    # PDF页面尺寸
    PAGE_WIDTH, PAGE_HEIGHT = A4

    # 页边距
    MARGIN_LEFT = 20 * mm
    MARGIN_RIGHT = 20 * mm
    MARGIN_TOP = 25 * mm
    MARGIN_BOTTOM = 25 * mm

    def __init__(self):
        """初始化导出服务"""
        self._register_fonts()

    def _register_fonts(self):
        """注册中文字体"""
        try:
            # 尝试注册常见的中文字体
            font_paths = [
                '/System/Library/Fonts/PingFang.ttc',  # macOS
                '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',  # Linux
                'C:\\Windows\\Fonts\\simhei.ttf',  # Windows
            ]

            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('Chinese', font_path))
                    logger.info(f"成功注册中文字体: {font_path}")
                    return

            logger.warning("未找到中文字体，将使用默认字体")

        except Exception as e:
            logger.error(f"注册字体失败: {str(e)}")

    def export_to_pdf(self, paper_data: Dict[str, Any], output_path: str) -> str:
        """
        导出试卷为PDF

        Args:
            paper_data: 试卷数据
            output_path: 输出文件路径

        Returns:
            生成的PDF文件路径
        """
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # 创建PDF
            c = canvas.Canvas(output_path, pagesize=A4)

            # 设置字体
            try:
                c.setFont('Chinese', 12)
            except:
                c.setFont('Helvetica', 12)

            # 渲染试卷内容
            self._render_paper_to_pdf(c, paper_data)

            # 保存PDF
            c.save()

            logger.info(f"PDF导出成功: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"PDF导出失败: {str(e)}")
            raise

    def export_to_jpg(self, paper_data: Dict[str, Any], output_dir: str) -> List[str]:
        """
        导出试卷为JPG（多页）

        Args:
            paper_data: 试卷数据
            output_dir: 输出目录

        Returns:
            生成的JPG文件路径列表
        """
        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)

            # 渲染试卷为图片
            images = self._render_paper_to_images(paper_data)

            # 保存图片
            jpg_files = []
            for i, img in enumerate(images):
                jpg_path = os.path.join(output_dir, f'page_{i+1}.jpg')
                img.save(jpg_path, 'JPEG', quality=95)
                jpg_files.append(jpg_path)
                logger.info(f"JPG导出成功: {jpg_path}")

            return jpg_files

        except Exception as e:
            logger.error(f"JPG导出失败: {str(e)}")
            raise

    def _render_paper_to_pdf(self, c: canvas.Canvas, paper_data: Dict[str, Any]):
        """
        将试卷内容渲染到PDF

        Args:
            c: PDF画布对象
            paper_data: 试卷数据
        """
        title = paper_data.get('title', '错题练习卷')
        questions = paper_data.get('questions', [])

        # 当前Y坐标
        y = self.PAGE_HEIGHT - self.MARGIN_TOP

        # 绘制标题
        try:
            c.setFont('Chinese', 18)
        except:
            c.setFont('Helvetica-Bold', 18)

        c.drawCentredString(self.PAGE_WIDTH / 2, y, title)
        y -= 30

        # 绘制副标题（知识点）
        subtitle = paper_data.get('subtitle', '')
        if subtitle:
            try:
                c.setFont('Chinese', 12)
            except:
                c.setFont('Helvetica', 12)
            c.drawCentredString(self.PAGE_WIDTH / 2, y, subtitle)
            y -= 25

        # 绘制题目
        try:
            c.setFont('Chinese', 12)
        except:
            c.setFont('Helvetica', 12)

        for i, question in enumerate(questions):
            # 检查是否需要换页
            if y < self.MARGIN_BOTTOM + 100:
                c.showPage()
                try:
                    c.setFont('Chinese', 12)
                except:
                    c.setFont('Helvetica', 12)
                y = self.PAGE_HEIGHT - self.MARGIN_TOP

            # 绘制题号
            question_number = question.get('number', i + 1)
            y = self._draw_question_pdf(c, question, question_number, y)

    def _draw_question_pdf(
        self,
        c: canvas.Canvas,
        question: Dict[str, Any],
        number: int,
        y: float
    ) -> float:
        """
        在PDF上绘制单个题目

        Args:
            c: PDF画布
            question: 题目数据
            number: 题号
            y: 当前Y坐标

        Returns:
            更新后的Y坐标
        """
        x = self.MARGIN_LEFT
        line_height = 20

        # 题号和题干
        stem = question.get('stem', '')
        question_text = f"{number}. {stem}"

        # 分行绘制
        max_width = self.PAGE_WIDTH - self.MARGIN_LEFT - self.MARGIN_RIGHT
        lines = self._wrap_text(question_text, max_width, 12)

        for line in lines:
            c.drawString(x, y, line)
            y -= line_height

        # 选项（如果是选择题）
        choices = question.get('choices', [])
        if choices:
            y -= 5
            for choice in choices:
                c.drawString(x + 20, y, choice)
                y -= line_height

        # 答案（可选）
        if question.get('show_answer'):
            y -= 5
            answer = question.get('answer', '')
            c.drawString(x, y, f"答案：{answer}")
            y -= line_height

        # 题目间距
        y -= 10

        return y

    def _render_paper_to_images(self, paper_data: Dict[str, Any]) -> List[Image.Image]:
        """
        将试卷内容渲染为图片列表

        Args:
            paper_data: 试卷数据

        Returns:
            图片列表
        """
        title = paper_data.get('title', '错题练习卷')
        questions = paper_data.get('questions', [])

        images = []
        current_image = Image.new('RGB', (self.A4_WIDTH_PX, self.A4_HEIGHT_PX), 'white')
        draw = ImageDraw.Draw(current_image)

        # 加载字体
        try:
            title_font = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 60)
            content_font = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 40)
        except:
            try:
                title_font = ImageFont.truetype('arial.ttf', 60)
                content_font = ImageFont.truetype('arial.ttf', 40)
            except:
                title_font = ImageFont.load_default()
                content_font = ImageFont.load_default()

        # 页边距（像素）
        margin_x = 200
        margin_y = 250
        y = margin_y
        line_height = 60

        # 绘制标题
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (self.A4_WIDTH_PX - title_width) // 2
        draw.text((title_x, y), title, fill='black', font=title_font)
        y += 150

        # 绘制题目
        for i, question in enumerate(questions):
            # 检查是否需要换页
            if y > self.A4_HEIGHT_PX - margin_y - 300:
                images.append(current_image)
                current_image = Image.new('RGB', (self.A4_WIDTH_PX, self.A4_HEIGHT_PX), 'white')
                draw = ImageDraw.Draw(current_image)
                y = margin_y

            # 绘制题号和题干
            question_number = question.get('number', i + 1)
            stem = question.get('stem', '')
            question_text = f"{question_number}. {stem}"

            # 分行绘制
            max_width = self.A4_WIDTH_PX - 2 * margin_x
            lines = self._wrap_text_image(question_text, max_width, content_font, draw)

            for line in lines:
                draw.text((margin_x, y), line, fill='black', font=content_font)
                y += line_height

            # 选项
            choices = question.get('choices', [])
            if choices:
                y += 20
                for choice in choices:
                    draw.text((margin_x + 50, y), choice, fill='black', font=content_font)
                    y += line_height

            # 答案
            if question.get('show_answer'):
                y += 20
                answer = question.get('answer', '')
                draw.text((margin_x, y), f"答案：{answer}", fill='blue', font=content_font)
                y += line_height

            y += 40  # 题目间距

        # 添加最后一页
        if y > margin_y:
            images.append(current_image)

        return images

    def _wrap_text(self, text: str, max_width: float, font_size: int) -> List[str]:
        """
        文本自动换行（PDF）

        Args:
            text: 文本内容
            max_width: 最大宽度
            font_size: 字体大小

        Returns:
            分行后的文本列表
        """
        # 简单实现：按字符数估算
        chars_per_line = int(max_width / font_size * 1.5)
        return textwrap.wrap(text, width=chars_per_line)

    def _wrap_text_image(
        self,
        text: str,
        max_width: int,
        font: ImageFont.ImageFont,
        draw: ImageDraw.ImageDraw
    ) -> List[str]:
        """
        文本自动换行（图片）

        Args:
            text: 文本内容
            max_width: 最大宽度（像素）
            font: 字体对象
            draw: 绘图对象

        Returns:
            分行后的文本列表
        """
        lines = []
        words = text.split()
        current_line = ''

        for word in words:
            test_line = current_line + ' ' + word if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines if lines else [text]
