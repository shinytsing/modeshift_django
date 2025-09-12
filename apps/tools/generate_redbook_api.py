import base64
import json
import logging
import os
import tempfile
from datetime import datetime

import pillow_heif  # 添加HEIC支持
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ToolUsageLog
from .services.llm_service import generate_redbook_content

# 配置日志
logger = logging.getLogger(__name__)


# API接口视图
class GenerateRedBookAPI(APIView):
    permission_classes = []  # 允许匿名用户访问

    def post(self, request):
        """处理多图片上传、文案生成和小红书发布"""
        try:
            # 调试信息
            logger.info(f"请求文件: {list(request.FILES.keys())}")
            logger.info(f"请求数据: {list(request.data.keys()) if hasattr(request, 'data') else 'No data'}")

            # 检测用户设备类型
            user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
            is_mobile = any(device in user_agent for device in ["mobile", "android", "iphone", "ipad"])

            # 1. 验证图片上传
            if "images" not in request.FILES:
                logger.error("未找到images字段")
                return Response({"error": "请上传图片"}, status=status.HTTP_400_BAD_REQUEST)

            image_files = request.FILES.getlist("images")
            logger.info(f"获取到 {len(image_files)} 张图片")
            if not image_files:
                return Response({"error": "请上传至少一张图片"}, status=status.HTTP_400_BAD_REQUEST)

            # 2. 验证所有图片文件类型和大小
            for image_file in image_files:
                if not self._validate_image(image_file):
                    return Response({"error": f"图片 {image_file.name} 格式不支持或文件过大"}, status=status.HTTP_400_BAD_REQUEST)

            # 3. 保存所有图片到临时文件
            temp_image_paths = []
            for image_file in image_files:
                temp_path = self._save_temp_image(image_file)
                temp_image_paths.append(temp_path)

            # 4. 调用DeepSeek生成文案（支持多图）
            try:
                generated_content = self._generate_content_with_multiple_images(temp_image_paths)
            except Exception as e:
                logger.warning(f"图片识别失败，使用通用文案: {str(e)}")
                # 如果图片识别失败，生成通用文案
                generated_content = self._generate_generic_content(len(image_files))

            # 5. 解析生成结果
            parsed_result = self._parse_redbook_response(generated_content)

            # 6. 记录使用日志
            image_names = [f.name for f in image_files]
            self._log_usage(request.user if request.user.is_authenticated else None, ", ".join(image_names), parsed_result)

            # 7. 根据设备类型返回不同的发布链接
            if is_mobile:
                # 手机端：使用小红书App的深度链接
                redbook_login_url = self._get_redbook_app_login_url(parsed_result)
                redbook_publish_url = self._get_redbook_app_publish_url(parsed_result)
                publish_guide = self._get_mobile_publish_guide(parsed_result)
            else:
                # 电脑端：使用网页版
                redbook_login_url = self._get_redbook_login_url()
                redbook_publish_url = self._get_redbook_publish_url(parsed_result)
                publish_guide = self._get_desktop_publish_guide(parsed_result)

            # 8. 返回结果
            return Response(
                {
                    "success": True,
                    "title": parsed_result["title"],
                    "content": parsed_result["content"],
                    "tags": parsed_result["tags"],
                    "redbook_login_url": redbook_login_url,
                    "redbook_publish_url": redbook_publish_url,
                    "publish_guide": publish_guide,
                    "is_mobile": is_mobile,
                    "message": "文案生成成功！请登录小红书后发布",
                    "image_count": len(image_files),
                }
            )

        except Exception as e:
            logger.error(f"小红书文案生成失败: {str(e)}", exc_info=True)
            return Response({"error": f"生成失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _validate_image(self, image_file):
        """验证图片文件"""
        # 检查文件类型（包括content_type和文件名）
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp", "image/heic", "image/heif"]
        allowed_extensions = [".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"]

        # 检查content_type
        if image_file.content_type in allowed_types:
            pass
        # 检查文件名扩展名
        elif any(image_file.name.lower().endswith(ext) for ext in allowed_extensions):
            pass
        else:
            return False

        # 检查文件大小（最大100MB）
        if image_file.size > 100 * 1024 * 1024:
            return False

        return True

    def _save_temp_image(self, image_file):
        """保存图片到临时文件"""
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                for chunk in image_file.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name

            # 检查是否为HEIC文件（通过content_type和文件名）
            is_heic = image_file.content_type in ["image/heic", "image/heif"] or image_file.name.lower().endswith(
                (".heic", ".heif")
            )

            if is_heic:
                logger.info(f"检测到HEIC文件，正在转换为JPEG: {image_file.name}")
                converted_path = self._convert_heic_to_jpeg(temp_path)
                # 删除原始临时文件
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                return converted_path

            return temp_path
        except Exception as e:
            logger.error(f"保存临时图片失败: {str(e)}")
            raise

    def _convert_heic_to_jpeg(self, heic_path):
        """将HEIC文件转换为JPEG格式"""
        try:
            from PIL import Image

            # 注册HEIF解码器
            pillow_heif.register_heif_opener()

            logger.info(f"开始转换HEIC文件: {heic_path}")

            # 打开HEIC文件
            with Image.open(heic_path) as img:
                logger.info(f"HEIC文件打开成功，尺寸: {img.size}, 模式: {img.mode}")

                # 创建新的临时文件用于保存JPEG
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as jpeg_file:
                    # 转换为RGB模式（HEIC可能是RGBA）
                    if img.mode in ("RGBA", "LA", "P"):
                        img = img.convert("RGB")
                        logger.info("转换为RGB模式")

                    # 保存为JPEG格式
                    img.save(jpeg_file.name, "JPEG", quality=95)
                    logger.info(f"HEIC转换成功，保存到: {jpeg_file.name}")
                    return jpeg_file.name

        except Exception as e:
            logger.error(f"HEIC转换失败: {str(e)}")
            logger.error(f"文件路径: {heic_path}")
            logger.error(f"文件是否存在: {os.path.exists(heic_path)}")

            # 如果转换失败，尝试直接返回原始文件
            if os.path.exists(heic_path):
                logger.info("转换失败，返回原始文件")
                return heic_path
            else:
                raise Exception(f"HEIC文件不存在: {heic_path}")

    def _generate_content_with_multiple_images(self, image_paths):
        """使用DeepSeek生成多图文案"""
        try:
            # 读取所有图片并转为Base64
            image_base64_list = []
            for image_path in image_paths:
                with open(image_path, "rb") as f:
                    image_data = f.read()
                    image_base64 = base64.b64encode(image_data).decode("utf-8")
                    image_base64_list.append(image_base64)

            # 构建多图提示词
            prompt = self._build_multiple_images_prompt(image_base64_list)

            # 调用DeepSeek
            response = generate_redbook_content(prompt)

            # 清理所有临时文件
            for image_path in image_paths:
                if os.path.exists(image_path):
                    os.unlink(image_path)

            return response

        except Exception:
            # 确保清理所有临时文件
            for image_path in image_paths:
                if os.path.exists(image_path):
                    os.unlink(image_path)
            raise

    def _generate_content_with_deepseek(self, image_path):
        """使用DeepSeek生成单图文案（保留兼容性）"""
        return self._generate_content_with_multiple_images([image_path])

    def _generate_generic_content(self, image_count):
        """生成通用文案（当图片识别失败时使用）"""
        try:
            # 构建通用提示词
            prompt = f"""
请为{image_count}张图片生成一个吸引人的小红书文案。

要求：
1. 标题要吸引人，有爆款潜质
2. 内容要有感染力，能引起共鸣
3. 包含3-5个相关标签
4. 适合{image_count}张图片的展示

请按以下格式返回：
标题：xxx
内容：xxx
标签：#xxx #xxx #xxx
"""

            # 调用DeepSeek
            response = generate_redbook_content(prompt)

            return response

        except Exception as e:
            logger.error(f"生成通用文案失败: {str(e)}")
            # 返回默认文案
            return f"""标题：分享{image_count}张美图，记录美好时光
内容：今天拍了{image_count}张照片，每一张都承载着不同的故事和情感。生活就是这样，总有一些瞬间值得被记录，总有一些美好值得被分享。希望这些照片能带给你一些温暖和感动。

标签：#生活记录 #美好时光 #摄影分享 #日常随拍 #生活美学"""

    def _build_multiple_images_prompt(self, image_base64_list):
        """构建多图小红书文案生成提示词"""
        images_info = ""
        for i, img_base64 in enumerate(image_base64_list, 1):
            images_info += f"图片{i} Base64数据：{img_base64[:100]}...（已省略）\n"

        return f"""请分析这{len(image_base64_list)}张图片并生成小红书风格的爆款文案。

## 要求：
1. **标题**：吸引眼球，有话题性，15字以内
2. **正文**：活泼亲切，有代入感，200-300字，可以描述多张图片的内容
3. **话题标签**：3-5个相关话题，格式为#话题名
4. **风格**：符合小红书用户喜好，有分享欲
5. **多图处理**：如果有多张图片，请描述图片间的关联性和整体故事

## 输出格式：
标题：[生成的标题]

正文：[生成的正文内容，可以描述多张图片]

话题标签：
#[话题1] #[话题2] #[话题3]

{images_info}

请根据所有图片内容生成符合小红书风格的爆款文案。"""

    def _build_redbook_prompt(self, image_base64):
        """构建单图小红书文案生成提示词"""
        return self._build_multiple_images_prompt([image_base64])

    def _parse_redbook_response(self, raw_response):
        """解析DeepSeek返回的文案"""
        try:
            lines = raw_response.strip().split("\n")
            title = ""
            content = ""
            tags = []

            current_section = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.startswith("标题："):
                    title = line.replace("标题：", "").strip()
                elif line.startswith("正文："):
                    current_section = "content"
                elif line.startswith("话题标签："):
                    current_section = "tags"
                elif line.startswith("#") and current_section == "tags":
                    tags.append(line.strip())
                elif current_section == "content" and not line.startswith("话题标签："):
                    content += line + "\n"

            # 如果没有解析到，使用默认格式
            if not title:
                title = lines[0] if lines else "发现美好生活"
            if not content:
                content = "\n".join(lines[1:]) if len(lines) > 1 else "分享生活中的美好瞬间"
            if not tags:
                tags = ["#生活分享", "#美好时光", "#日常记录"]

            return {"title": title, "content": content.strip(), "tags": tags}

        except Exception as e:
            logger.error(f"解析文案失败: {str(e)}")
            return {
                "title": "发现美好生活",
                "content": "分享生活中的美好瞬间，记录每一个值得珍藏的回忆。",
                "tags": ["#生活分享", "#美好时光", "#日常记录"],
            }

    def _get_redbook_login_url(self):
        """获取小红书登录链接（带回调参数）"""
        # 使用小红书电脑端登录页面，会显示二维码
        # 添加回调参数，登录成功后自动跳转到发布页面
        import urllib.parse

        callback_url = urllib.parse.quote("https://www.xiaohongshu.com/mobile/publish")
        return f"https://www.xiaohongshu.com/login?callback={callback_url}"

    def _get_redbook_publish_url(self, content_data):
        """获取小红书发布链接（带预填充内容）"""
        # 构建发布URL，包含预填充的文案
        title = content_data.get("title", "")
        content = content_data.get("content", "")
        tags = " ".join(content_data.get("tags", []))

        # 编码文案内容
        import urllib.parse

        encoded_title = urllib.parse.quote(title)
        encoded_content = urllib.parse.quote(content)
        encoded_tags = urllib.parse.quote(tags)

        # 使用小红书移动端发布页面，支持预填充内容
        # 添加更多参数以支持自动填充
        publish_url = (
            f"https://www.xiaohongshu.com/mobile/publish?"
            f"title={encoded_title}&"
            f"content={encoded_content}&"
            f"tags={encoded_tags}&"
            "auto_fill=true&"
            "source=web_tool"
        )

        return publish_url

    def _get_redbook_app_login_url(self, content_data):
        """获取小红书App登录链接（深度链接）"""
        # 构建深度链接URL，包含预填充的文案
        title = content_data.get("title", "")
        content = content_data.get("content", "")
        tags = " ".join(content_data.get("tags", []))

        # 编码文案内容
        import urllib.parse

        encoded_title = urllib.parse.quote(title)
        encoded_content = urllib.parse.quote(content)
        encoded_tags = urllib.parse.quote(tags)

        # 使用小红书App的深度链接，支持预填充内容
        # 添加更多参数以支持自动填充
        app_url = (
            f"xiaohongshu://publish?"
            f"title={encoded_title}&"
            f"content={encoded_content}&"
            f"tags={encoded_tags}&"
            "auto_fill=true&"
            "source=web_tool"
        )

        return app_url

    def _get_redbook_app_publish_url(self, content_data):
        """获取小红书App发布链接（深度链接）"""
        # 构建深度链接URL，包含预填充的文案
        title = content_data.get("title", "")
        content = content_data.get("content", "")
        tags = " ".join(content_data.get("tags", []))

        # 编码文案内容
        import urllib.parse

        encoded_title = urllib.parse.quote(title)
        encoded_content = urllib.parse.quote(content)
        encoded_tags = urllib.parse.quote(tags)

        # 使用小红书App的深度链接，支持预填充内容
        # 添加更多参数以支持自动填充
        app_url = (
            f"xiaohongshu://publish?"
            f"title={encoded_title}&"
            f"content={encoded_content}&"
            f"tags={encoded_tags}&"
            "auto_fill=true&"
            "source=web_tool"
        )

        return app_url

    def _get_desktop_publish_guide(self, result):
        """获取电脑端发布指南"""
        return """
## 💻 电脑端发布步骤：

### 🚀 一键发布（推荐）
1. 点击上方"电脑端扫码登录"按钮
2. 使用小红书App扫描二维码
3. 登录成功后会自动跳转到发布页面
4. 文案和标签会自动填充到编辑器中
5. 上传您的图片，点击发布即可

### 📋 手动发布
1. 点击上方"电脑端扫码登录"按钮
2. 登录后点击"+"号发布新笔记
3. 复制以下文案：

**标题：**
{result['title']}

**正文：**
{result['content']}

**话题标签：**
{' '.join(result['tags'])}

4. 粘贴到小红书编辑器中
5. 上传图片，点击发布

### 💡 智能功能：
- ✅ 扫码登录后自动跳转到发布页面
- ✅ 文案和标签自动填充，无需手动复制
- ✅ 支持多图上传，最多9张图片
- ✅ 支持HEIC格式图片上传
- ✅ 智能文案生成，提升发布效率

### 🔄 如果自动填充不生效：
1. 确保已登录小红书账号
2. 刷新发布页面
3. 手动复制文案内容
4. 联系客服获取帮助
        """

    def _get_mobile_publish_guide(self, result):
        """获取手机端发布指南"""
        return """
## 📱 手机端发布步骤：

### 🚀 一键发布（推荐）
1. 点击上方"打开小红书App"按钮
2. 如果已安装小红书App，会自动打开并填充文案
3. 如果未安装，会引导您下载小红书App
4. 文案和标签会自动填充到编辑器中
5. 上传您的图片，点击发布即可

### 📱 App内发布
1. 打开小红书App
2. 点击"+"号发布新笔记
3. 复制以下文案：

**标题：**
{result['title']}

**正文：**
{result['content']}

**话题标签：**
{' '.join(result['tags'])}

4. 粘贴到小红书编辑器中
5. 上传图片，点击发布

### 💡 智能功能：
- ✅ 自动检测设备类型，提供最佳体验
- ✅ 深度链接直接打开小红书App
- ✅ 文案和标签自动填充，无需手动复制
- ✅ 支持多图上传，最多9张图片
- ✅ 支持HEIC格式图片上传
- ✅ 智能文案生成，提升发布效率

### 🔄 如果App未打开：
1. 确保已安装小红书App
2. 点击"下载小红书App"按钮
3. 安装完成后重新尝试
4. 手动复制文案内容

### 📲 下载小红书App：
- iOS：App Store搜索"小红书"
- Android：应用商店搜索"小红书"
        """

    def _log_usage(self, user, image_name, result):
        """记录使用日志"""
        try:
            # 创建临时文件用于记录输出
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
                json.dump(result, temp_file, ensure_ascii=False, indent=2)
                temp_file_path = temp_file.name

            # 创建Django文件对象
            from django.core.files import File

            with open(temp_file_path, "rb") as f:
                django_file = File(f, name=f'redbook_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')

                # 处理匿名用户的情况
                if user is None:
                    # 对于匿名用户，不记录到数据库，只记录到日志
                    logger.info(f"匿名用户使用红书生成器 - 图片: {image_name}, 标题: {result['title']}")
                else:
                    ToolUsageLog.objects.create(
                        user=user,
                        tool_type="REDBOOK",
                        input_data=json.dumps(
                            {"image_name": image_name, "generated_title": result["title"], "generated_tags": result["tags"]},
                            ensure_ascii=False,
                        ),
                        output_file=django_file,
                        raw_response=json.dumps(result, ensure_ascii=False),
                    )

            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

        except Exception as e:
            logger.error(f"记录使用日志失败: {str(e)}")
