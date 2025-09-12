import json
import logging
import os
import tempfile
from datetime import datetime

import defusedxml.ElementTree as ET
import defusedxml.minidom as minidom
import xmind
from django.conf import settings
from django.http import FileResponse, JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class TaskDownloadAPI(APIView):
    """任务结果下载API - 支持多种格式"""
    
    permission_classes = []  # 允许匿名访问
    
    def get(self, request, task_id, format_type):
        """下载任务结果，支持txt、xmind、feishu格式"""
        try:
            # 获取任务详情
            from .async_test_cases_api import TaskStatusAPI
            task_api = TaskStatusAPI()
            task_response = task_api.get(request, task_id)
            
            if task_response.status_code != 200:
                return Response({"error": "任务不存在"}, status=status.HTTP_404_NOT_FOUND)
            
            task_data = task_response.data
            if not task_data.get('success') or not task_data.get('result'):
                return Response({"error": "任务结果为空"}, status=status.HTTP_400_BAD_REQUEST)
            
            content = task_data['result']
            
            # 根据格式类型生成文件
            if format_type == 'txt':
                return self._generate_txt_file(content, task_id)
            elif format_type == 'xmind':
                return self._generate_xmind_file(content, task_id)
            elif format_type == 'feishu':
                return self._generate_feishu_file(content, task_id)
            else:
                return Response({"error": "不支持的格式类型"}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"下载任务结果失败: {str(e)}")
            return Response({"error": f"下载失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_txt_file(self, content, task_id):
        """生成TXT格式文件"""
        filename = f"任务结果_{task_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            response = FileResponse(
                open(tmp_path, 'rb'),
                content_type='text/plain; charset=utf-8',
                as_attachment=True,
                filename=filename
            )
            return response
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def _generate_xmind_file(self, content, task_id):
        """生成XMind格式文件"""
        try:
            # 创建XMind工作簿
            workbook = xmind.load("test_cases.xmind")
            sheet = workbook.getPrimarySheet()
            root_topic = sheet.getRootTopic()
            
            # 设置根主题
            root_topic.setTitle("AI生成测试用例")
            
            # 解析测试用例内容，构建层级结构
            lines = content.split('\n')
            current_module = None
            module_topic = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 检测模块标题
                if line.startswith('## '):
                    current_module = line[3:].strip()
                    module_topic = root_topic.addSubTopic()
                    module_topic.setTitle(current_module)
                # 检测测试用例
                elif line.startswith('### ') and module_topic:
                    test_case = line[4:].strip()
                    case_topic = module_topic.addSubTopic()
                    case_topic.setTitle(test_case)
                # 检测用例详情
                elif line.startswith('- ') and module_topic:
                    detail = line[2:].strip()
                    if module_topic.getSubTopics():
                        last_case = module_topic.getSubTopics()[-1]
                        detail_topic = last_case.addSubTopic()
                        detail_topic.setTitle(detail)
            
            # 保存到临时文件
            filename = f"任务结果_{task_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xmind"
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xmind') as tmp:
                xmind.save(workbook, tmp.name)
                tmp_path = tmp.name
            
            try:
                response = FileResponse(
                    open(tmp_path, 'rb'),
                    content_type='application/vnd.xmind.workbook',
                    as_attachment=True,
                    filename=filename
                )
                return response
            finally:
                # 清理临时文件
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
        except Exception as e:
            logger.error(f"生成XMind文件失败: {str(e)}")
            return Response({"error": f"生成XMind文件失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_feishu_file(self, content, task_id):
        """生成飞书格式文件"""
        try:
            # 生成飞书兼容的Markdown内容
            feishu_content = self._generate_feishu_content(content)
            
            filename = f"任务结果_{task_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_feishu.md"
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.md') as tmp:
                tmp.write(feishu_content)
                tmp_path = tmp.name
            
            try:
                response = FileResponse(
                    open(tmp_path, 'rb'),
                    content_type='text/markdown; charset=utf-8',
                    as_attachment=True,
                    filename=filename
                )
                return response
            finally:
                # 清理临时文件
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
        except Exception as e:
            logger.error(f"生成飞书文件失败: {str(e)}")
            return Response({"error": f"生成飞书文件失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_feishu_content(self, content):
        """生成飞书兼容的Markdown内容"""
        feishu_content = '# 测试用例文档\n\n'
        feishu_content += '> 本文档由AI测试用例生成器自动生成，支持飞书直接导入\n\n'
        
        lines = content.split('\n')
        current_module = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测模块标题
            if line.startswith('## '):
                if current_module:
                    feishu_content += '\n---\n\n'
                current_module = line[3:].strip()
                feishu_content += f'## 📋 {current_module}\n\n'
            # 检测测试用例
            elif line.startswith('### '):
                test_case = line[4:].strip()
                feishu_content += f'### ✅ {test_case}\n\n'
            # 检测用例详情
            elif line.startswith('- '):
                detail = line[2:].strip()
                feishu_content += f'- {detail}\n'
            # 其他内容
            elif line:
                feishu_content += f'{line}\n'
        
        feishu_content += '\n---\n\n'
        feishu_content += '## 📊 文档信息\n\n'
        feishu_content += f'- **生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
        feishu_content += '- **生成工具**: AI测试用例生成器\n'
        feishu_content += '- **格式**: 飞书兼容Markdown\n'
        feishu_content += '- **用途**: 可直接导入飞书文档使用\n\n'
        
        return feishu_content
