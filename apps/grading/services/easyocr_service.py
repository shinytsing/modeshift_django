"""
EasyOCR服务
完全免费的OCR服务，支持80+种语言，中文识别效果好
"""
import os
import logging
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


class EasyOCRService:
    """EasyOCR服务类 - 完全免费，无需API密钥"""

    def __init__(self):
        """初始化EasyOCR服务"""
        self.ocr_reader = None
        self.languages = ['ch_sim', 'en']  # 简体中文和英文
        self._initialize_ocr()

    def _initialize_ocr(self):
        """初始化OCR读取器"""
        try:
            import easyocr
            logger.info("正在初始化EasyOCR（首次使用会下载模型，请稍候）...")
            # 首次使用会下载模型，可能需要一些时间
            self.ocr_reader = easyocr.Reader(self.languages, gpu=False)
            logger.info("✅ EasyOCR初始化成功")
        except ImportError:
            logger.warning("EasyOCR未安装，请运行: pip install easyocr")
            self.ocr_reader = None
        except Exception as e:
            logger.error(f"EasyOCR初始化失败: {str(e)}")
            self.ocr_reader = None

    def recognize_text(self, image_path: str) -> Dict[str, Any]:
        """
        识别图片中的文字

        Args:
            image_path: 图片路径

        Returns:
            识别结果，包含文字内容和位置信息
        """
        if not self.ocr_reader:
            raise ValueError("EasyOCR未初始化，请检查安装")

        try:
            # 调用EasyOCR识别
            results = self.ocr_reader.readtext(image_path)

            # 格式化结果（改进版：按位置排序，确保顺序正确）
            words_result = []
            full_text = []

            for detection in results:
                bbox = detection[0]  # 边界框坐标
                text = detection[1]   # 识别的文字
                confidence = detection[2]  # 置信度

                # 计算边界框的左上角和宽高
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]

                left = int(min(x_coords))
                top = int(min(y_coords))
                width = int(max(x_coords) - min(x_coords))
                height = int(max(y_coords) - min(y_coords))

                words_result.append({
                    'words': text,
                    'location': {
                        'left': left,
                        'top': top,
                        'width': width,
                        'height': height
                    },
                    'confidence': confidence,
                    'bbox_points': bbox  # 保存原始坐标点
                })

                full_text.append(text)

            # 按位置排序（从上到下，从左到右）
            words_result.sort(key=lambda x: (x['location']['top'], x['location']['left']))

            result = {
                'words_result': words_result,
                'full_text': '\n'.join(full_text),
                'word_count': len(words_result)
            }

            logger.info(f"EasyOCR识别成功，识别到{len(words_result)}个文字区域")
            return result

        except Exception as e:
            logger.error(f"EasyOCR识别失败: {str(e)}")
            raise

    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self.ocr_reader is not None
