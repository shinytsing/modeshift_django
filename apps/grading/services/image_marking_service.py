"""
图片标记服务
在原图上绘制打钩/打叉标记，标明学生答对或答错
"""
import os
import logging
from typing import List, Dict, Any, Tuple
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class ImageMarkingService:
    """图片标记服务类"""

    def __init__(self):
        """初始化图片标记服务"""
        self.mark_size = 40  # 标记大小（像素）
        self.mark_thickness = 5  # 标记线条粗细

    def mark_image(
        self,
        image_path: str,
        questions: List[Dict[str, Any]],
        output_path: str = None
    ) -> str:
        """
        在图片上标记题目的对错

        Args:
            image_path: 原始图片路径
            questions: 题目列表，每个题目包含：
                - question_number: 题号
                - is_correct: 是否正确
                - region: 题目区域坐标 [(x1, y1), (x2, y2), ...] 或 bbox: {'left', 'top', 'width', 'height'}
            output_path: 输出图片路径，如果为None则自动生成

        Returns:
            标记后的图片路径
        """
        try:
            # 打开原始图片
            image = Image.open(image_path)
            draw = ImageDraw.Draw(image)

            # 加载字体（用于显示题号）
            try:
                font = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 20)
            except:
                try:
                    font = ImageFont.truetype('arial.ttf', 20)
                except:
                    font = ImageFont.load_default()

            # 为每道题绘制标记
            for question in questions:
                is_correct = question.get('is_correct', False)
                question_number = question.get('question_number', 0)

                if question_number == 0:
                    continue  # 跳过无效题号

                region = question.get('region')
                bbox = question.get('bbox')

                # 确定标记位置（优先级：region > bbox > 估算位置）
                # 改进：标记位置应该在题目的左上角或题号位置
                x, y = None, None

                if region and isinstance(region, list) and len(region) >= 1:
                    # 使用区域坐标的第一个点作为标记位置（题目的左上角）
                    if isinstance(region[0], dict):
                        x, y = region[0].get('x', 0), region[0].get('y', 0)
                    elif isinstance(region[0], (list, tuple)) and len(region[0]) >= 2:
                        x, y = int(region[0][0]), int(region[0][1])

                if x is None or y is None:
                    if bbox:
                        # 使用边界框的左上角，稍微偏移到左侧（标记在题目左侧）
                        x = max(0, bbox.get('left', 0) - 50)  # 标记在题目左侧，留出足够空间
                        y = bbox.get('top', 0) + 10  # 稍微下移，避免遮挡题号
                    else:
                        # 如果没有坐标信息，根据题号估算位置
                        x, y = self._estimate_position(image.size, question_number)

                # 确保坐标在图片范围内
                x = max(10, min(x, image.size[0] - 50))
                y = max(10, min(y, image.size[1] - 50))

                # 绘制标记
                self._draw_mark(draw, x, y, is_correct, question_number, font)

            # 保存标记后的图片
            if output_path is None:
                # 自动生成输出路径
                image_dir = Path(image_path).parent
                image_name = Path(image_path).stem
                output_path = str(image_dir / f"{image_name}_marked.jpg")

            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # 保存图片
            image.save(output_path, 'JPEG', quality=95)
            logger.info(f"图片标记完成: {output_path}")

            return output_path

        except Exception as e:
            logger.error(f"图片标记失败: {str(e)}")
            raise

    def _draw_mark(
        self,
        draw: ImageDraw.ImageDraw,
        x: int,
        y: int,
        is_correct: bool,
        question_number: int,
        font: ImageFont.ImageFont
    ):
        """
        绘制单个标记（改进版：更清晰的标记）

        Args:
            draw: 绘图对象
            x: X坐标
            y: Y坐标
            is_correct: 是否正确
            question_number: 题号
            font: 字体对象
        """
        # 标记颜色（更鲜明的颜色）
        if is_correct:
            color = (34, 139, 34)  # 深绿色，更醒目
            mark_symbol = '✓'
        else:
            color = (220, 20, 60)  # 深红色，更醒目
            mark_symbol = '✗'

        # 绘制圆形背景（带白色边框，更清晰）
        circle_radius = self.mark_size // 2
        circle_bbox = [
            x - circle_radius,
            y - circle_radius,
            x + circle_radius,
            y + circle_radius
        ]

        # 先绘制白色边框
        draw.ellipse(circle_bbox, fill='white', outline='white', width=3)
        # 再绘制彩色圆圈
        draw.ellipse(circle_bbox, fill=color, outline=color, width=2)

        # 绘制标记符号（使用更大的字体）
        try:
            # 尝试使用更大的字体
            large_font = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 28)
        except:
            try:
                large_font = ImageFont.truetype('arial.ttf', 28)
            except:
                large_font = font

        # 获取文字大小以居中
        bbox = draw.textbbox((0, 0), mark_symbol, font=large_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = x - text_width // 2
        text_y = y - text_height // 2 - 2  # 稍微上移，视觉上更居中

        # 绘制标记符号（白色，更清晰）
        draw.text((text_x, text_y), mark_symbol, fill='white', font=large_font)

        # 可选：在标记旁边显示题号（小字）
        if question_number > 0:
            try:
                small_font = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 14)
            except:
                small_font = font

            number_text = f"#{question_number}"
            number_bbox = draw.textbbox((0, 0), number_text, font=small_font)
            number_width = number_bbox[2] - number_bbox[0]
            number_x = x + circle_radius + 8
            number_y = y - (number_bbox[3] - number_bbox[1]) // 2

            # 绘制题号背景（半透明白色）
            padding = 4
            number_bg = [
                number_x - padding,
                number_y - padding,
                number_x + number_width + padding,
                number_y + (number_bbox[3] - number_bbox[1]) + padding
            ]
            # 使用半透明背景（需要RGBA模式）
            # 简化：直接绘制白色背景
            draw.rectangle(number_bg, fill='white', outline=color, width=1)
            draw.text((number_x, number_y), number_text, fill=color, font=small_font)

    def _estimate_position(self, image_size: Tuple[int, int], question_number: int) -> Tuple[int, int]:
        """
        估算题目位置（当没有坐标信息时）

        Args:
            image_size: 图片尺寸 (width, height)
            question_number: 题号

        Returns:
            估算的坐标 (x, y)
        """
        width, height = image_size

        # 假设题目从上到下排列，每道题大约占用100像素高度
        y = 50 + (question_number - 1) * 100

        # X坐标在左侧
        x = 30

        # 确保坐标在图片范围内
        y = min(y, height - 50)
        x = min(x, width - 50)

        return (x, y)

    def mark_multiple_images(
        self,
        image_paths: List[str],
        questions_by_image: List[List[Dict[str, Any]]],
        output_dir: str = None
    ) -> List[str]:
        """
        批量标记多张图片

        Args:
            image_paths: 图片路径列表
            questions_by_image: 每张图片对应的题目列表
            output_dir: 输出目录

        Returns:
            标记后的图片路径列表
        """
        marked_images = []

        for i, image_path in enumerate(image_paths):
            questions = questions_by_image[i] if i < len(questions_by_image) else []

            if output_dir:
                image_name = Path(image_path).stem
                output_path = os.path.join(output_dir, f"{image_name}_marked.jpg")
            else:
                output_path = None

            marked_path = self.mark_image(image_path, questions, output_path)
            marked_images.append(marked_path)

        return marked_images
