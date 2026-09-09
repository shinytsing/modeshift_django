"""
百度OCR服务
支持调用百度OCR API进行文字识别
"""
import os
import logging
import base64
import requests
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


class BaiduOCRService:
    """百度OCR服务类"""

    def __init__(self):
        """初始化百度OCR服务"""
        self.api_key = os.getenv('BAIDU_OCR_API_KEY', '')
        self.secret_key = os.getenv('BAIDU_OCR_SECRET_KEY', '')
        self.access_token = None

        if self.api_key and self.secret_key:
            self.access_token = self._get_access_token()
            logger.info("百度OCR服务已初始化")
        else:
            logger.warning("百度OCR API密钥未配置，将无法使用百度OCR")

    def _get_access_token(self) -> str:
        """
        获取百度OCR访问令牌

        Returns:
            访问令牌
        """
        if not self.api_key or not self.secret_key:
            return None

        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }

        try:
            response = requests.post(url, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            access_token = result.get("access_token")
            logger.info("百度OCR访问令牌获取成功")
            return access_token
        except Exception as e:
            logger.error(f"获取百度OCR访问令牌失败: {str(e)}")
            return None

    def recognize_text(self, image_path: str) -> Dict[str, Any]:
        """
        识别图片中的文字

        Args:
            image_path: 图片路径

        Returns:
            识别结果，包含文字内容和位置信息
        """
        if not self.access_token:
            raise ValueError("百度OCR访问令牌未获取，请检查API密钥配置")

        # 读取图片并转换为base64
        with open(image_path, 'rb') as f:
            image_data = f.read()

        image_base64 = base64.b64encode(image_data).decode('utf-8')

        # 调用百度OCR API
        url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token={self.access_token}"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'image': image_base64
        }

        try:
            response = requests.post(url, headers=headers, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()

            if 'error_code' in result:
                error_msg = result.get('error_msg', '未知错误')
                logger.error(f"百度OCR识别失败: {error_msg}")
                raise Exception(f"百度OCR识别失败: {error_msg}")

            logger.info(f"百度OCR识别成功，识别到{len(result.get('words_result', []))}个文字区域")
            return result

        except Exception as e:
            logger.error(f"百度OCR API调用失败: {str(e)}")
            raise

    def recognize_handwriting(self, image_path: str) -> Dict[str, Any]:
        """
        识别手写文字（适用于作业批改）
        使用高精度手写识别API，返回详细的位置信息

        Args:
            image_path: 图片路径

        Returns:
            识别结果，包含words_result和详细位置信息
        """
        if not self.access_token:
            raise ValueError("百度OCR访问令牌未获取，请检查API密钥配置")

        # 读取图片并转换为base64
        with open(image_path, 'rb') as f:
            image_data = f.read()

        image_base64 = base64.b64encode(image_data).decode('utf-8')

        # 调用百度手写OCR API（高精度版）
        # 使用高精度手写识别，返回详细位置信息
        url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/handwriting?access_token={self.access_token}"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'image': image_base64,
            'recognize_granularity': 'big',  # 大粒度识别，适合整题识别
            'words_type': 'handwriting',  # 手写识别
            'probability': 'true',  # 返回置信度
            'location': 'true'  # 返回位置信息
        }

        try:
            response = requests.post(url, headers=headers, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()

            if 'error_code' in result:
                error_msg = result.get('error_msg', '未知错误')
                logger.error(f"百度手写OCR识别失败: {error_msg}")
                raise Exception(f"百度手写OCR识别失败: {error_msg}")

            words_count = len(result.get('words_result', []))
            logger.info(f"百度手写OCR识别成功，识别到{words_count}个文字区域")
            return result

        except Exception as e:
            logger.error(f"百度手写OCR API调用失败: {str(e)}")
            raise

    def recognize_accurate(self, image_path: str) -> Dict[str, Any]:
        """
        高精度文字识别（适用于印刷体+手写混合）
        使用通用高精度识别API

        Args:
            image_path: 图片路径

        Returns:
            识别结果
        """
        if not self.access_token:
            raise ValueError("百度OCR访问令牌未获取，请检查API密钥配置")

        # 读取图片并转换为base64
        with open(image_path, 'rb') as f:
            image_data = f.read()

        image_base64 = base64.b64encode(image_data).decode('utf-8')

        # 调用百度高精度OCR API
        url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token={self.access_token}"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'image': image_base64,
            'detect_direction': 'true',  # 检测方向
            'paragraph': 'true',  # 返回段落信息
            'probability': 'true'  # 返回置信度
        }

        try:
            response = requests.post(url, headers=headers, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()

            if 'error_code' in result:
                error_msg = result.get('error_msg', '未知错误')
                logger.error(f"百度高精度OCR识别失败: {error_msg}")
                raise Exception(f"百度高精度OCR识别失败: {error_msg}")

            words_count = len(result.get('words_result', []))
            logger.info(f"百度高精度OCR识别成功，识别到{words_count}个文字区域")
            return result

        except Exception as e:
            logger.error(f"百度高精度OCR API调用失败: {str(e)}")
            raise

    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self.access_token is not None
