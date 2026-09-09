"""
批改结果导出服务
生成批改后的PDF、题目列表等
"""
import os
import logging
from typing import Dict, Any, List
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import textwrap

logger = logging.getLogger(__name__)


class GradingResultExportService:
    """批改结果导出服务"""

    def __init__(self):
        """初始化导出服务"""
        self._register_fonts()

    def _register_fonts(self):
        """注册中文字体"""
        try:
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

    def export_grading_result_pdf(
        self,
        questions: List[Dict[str, Any]],
        total_score: float,
        max_score: float,
        output_path: str
    ) -> str:
        """
        导出批改结果PDF（题目+解析列表）

        Args:
            questions: 题目列表
            total_score: 总分
            max_score: 满分
            output_path: 输出路径

        Returns:
            PDF文件路径
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            c = canvas.Canvas(output_path, pagesize=A4)

            # 设置字体
            try:
                c.setFont('Chinese', 14)
            except:
                c.setFont('Helvetica-Bold', 14)

            # 页边距
            margin_x = 20 * mm
            margin_y = 25 * mm
            y = A4[1] - margin_y
            line_height = 20

            # 标题
            title = "批改结果详情"
            c.setFont('Chinese', 18) if 'Chinese' in [f.fontName for f in pdfmetrics.getRegisteredFontNames()] else c.setFont('Helvetica-Bold', 18)
            c.drawCentredString(A4[0] / 2, y, title)
            y -= 30

            # 分数信息
            try:
                c.setFont('Chinese', 12)
            except:
                c.setFont('Helvetica', 12)
            score_text = f"总分: {total_score} / {max_score}"
            c.drawString(margin_x, y, score_text)
            y -= 30

            # 题目列表
            for q in questions:
                # 检查是否需要换页
                if y < margin_y + 100:
                    c.showPage()
                    try:
                        c.setFont('Chinese', 12)
                    except:
                        c.setFont('Helvetica', 12)
                    y = A4[1] - margin_y

                # 题号
                q_num = q.get('question_number', 0)
                status = "✓ 正确" if q.get('is_correct', False) else "✗ 错误"
                status_color = (0, 0.8, 0) if q.get('is_correct', False) else (0.8, 0, 0)

                header = f"第 {q_num} 题 {status}"
                c.setFont('Helvetica-Bold', 12)
                c.drawString(margin_x, y, header)
                y -= line_height

                # 题干
                try:
                    c.setFont('Chinese', 11)
                except:
                    c.setFont('Helvetica', 11)
                stem = q.get('question_stem', '')
                stem_lines = self._wrap_text_pdf(stem, A4[0] - 2 * margin_x, 11)
                for line in stem_lines:
                    c.drawString(margin_x + 10, y, line)
                    y -= line_height

                # 学生答案
                student_answer = q.get('student_answer', '')
                if student_answer:
                    c.drawString(margin_x + 10, y, f"学生答案: {student_answer}")
                    y -= line_height

                # 正确答案
                correct_answer = q.get('correct_answer', '')
                if correct_answer:
                    c.drawString(margin_x + 10, y, f"正确答案: {correct_answer}")
                    y -= line_height

                # 得分
                score = q.get('score', 0)
                max_q_score = q.get('max_score', 10)
                c.drawString(margin_x + 10, y, f"得分: {score} / {max_q_score}")
                y -= line_height

                # 解析
                feedback = q.get('feedback', q.get('analysis', ''))
                if feedback:
                    c.drawString(margin_x + 10, y, f"解析: {feedback}")
                    y -= line_height

                y -= 10  # 题目间距

            c.save()
            logger.info(f"批改结果PDF导出成功: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"批改结果PDF导出失败: {str(e)}")
            raise

    def _wrap_text_pdf(self, text: str, max_width: float, font_size: int) -> List[str]:
        """PDF文本换行"""
        chars_per_line = int(max_width / font_size * 1.5)
        return textwrap.wrap(text, width=chars_per_line)
