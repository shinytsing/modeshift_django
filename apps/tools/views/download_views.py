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
            from ..async_test_cases_api import TaskStatusAPI
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
        """生成飞书格式文件（FreeMind格式）- 包含完整用例信息"""
        try:
            # 解析内容为测试用例结构
            test_cases = self._parse_content_to_structure(content)
            
            # 生成FreeMind格式的XML
            import xml.etree.ElementTree as ET
            import xml.dom.minidom as minidom
            
            # 创建根节点
            map_root = ET.Element("map")
            map_root.set("version", "1.0.1")
            
            # 根主题
            root_topic = ET.SubElement(map_root, "node")
            root_topic.set("TEXT", "测试用例文档")
            root_topic.set("STYLE", "bubble")
            root_topic.set("COLOR", "#000000")
            
            # 处理每个模块
            for module_name, cases in test_cases["structure"].items():
                # 模块节点
                module_node = ET.SubElement(root_topic, "node")
                module_node.set("TEXT", module_name)
                module_node.set("COLOR", "#FF7F50")
                module_node.set("STYLE", "fork")
                
                # 处理每个测试用例
                for case_content in cases:
                    if case_content:
                        # 将用例内容按行分割
                        case_lines = case_content.split('\n')
                        case_title = case_lines[0] if case_lines else "未知用例"
                        
                        # 创建用例节点
                        case_node = ET.SubElement(module_node, "node")
                        case_node.set("TEXT", case_title)
                        case_node.set("COLOR", "#4682B4")
                        case_node.set("STYLE", "bubble")
                        
                        # 为用例的每个部分创建子节点
                        current_section = None
                        section_content = []
                        
                        for line in case_lines[1:]:  # 跳过标题行
                            line = line.strip()
                            if not line:
                                continue
                                
                            # 检测新的部分
                            if line.startswith('测试场景：'):
                                # 保存之前的部分
                                if current_section and section_content:
                                    self._add_section_node(case_node, current_section, section_content)
                                
                                current_section = "测试场景"
                                section_content = [line[5:].strip()]
                            elif line.startswith('前置条件：'):
                                if current_section and section_content:
                                    self._add_section_node(case_node, current_section, section_content)
                                
                                current_section = "前置条件"
                                section_content = [line[5:].strip()]
                            elif line.startswith('测试步骤：'):
                                if current_section and section_content:
                                    self._add_section_node(case_node, current_section, section_content)
                                
                                current_section = "测试步骤"
                                section_content = []
                            elif line.startswith('预期结果：'):
                                if current_section and section_content:
                                    self._add_section_node(case_node, current_section, section_content)
                                
                                current_section = "预期结果"
                                section_content = [line[5:].strip()]
                            elif line.startswith('优先级：'):
                                if current_section and section_content:
                                    self._add_section_node(case_node, current_section, section_content)
                                
                                current_section = "优先级"
                                section_content = [line[4:].strip()]
                            elif line.startswith('测试类型：'):
                                if current_section and section_content:
                                    self._add_section_node(case_node, current_section, section_content)
                                
                                current_section = "测试类型"
                                section_content = [line[5:].strip()]
                            elif current_section == "测试步骤" and (line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. ') or line.startswith('4. ') or line.startswith('5. ')):
                                section_content.append(line)
                            elif current_section and line:
                                section_content.append(line)
                        
                        # 保存最后一个部分
                        if current_section and section_content:
                            self._add_section_node(case_node, current_section, section_content)
            
            # 格式化XML
            rough_string = ET.tostring(map_root, "utf-8")
            reparsed = minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")
            
            # 确保XML声明正确
            if not pretty_xml.startswith("<?xml"):
                pretty_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + pretty_xml
            
            filename = f"任务结果_{task_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_feishu.mm"
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.mm') as tmp:
                tmp.write(pretty_xml)
                tmp_path = tmp.name
            
            try:
                response = FileResponse(
                    open(tmp_path, 'rb'),
                    content_type='application/x-freemind; charset=utf-8',
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
    
    def _add_section_node(self, parent_node, section_name, content_lines):
        """为测试用例添加部分节点"""
        import xml.etree.ElementTree as ET
        
        section_node = ET.SubElement(parent_node, "node")
        section_node.set("TEXT", section_name)
        section_node.set("COLOR", "#32CD32")  # 绿色
        section_node.set("STYLE", "fork")
        
        # 添加内容
        if isinstance(content_lines, list):
            content_text = "\n".join(content_lines)
        else:
            content_text = str(content_lines)
        
        # 如果内容太长，分割成多个子节点
        if len(content_text) > 100:
            lines = content_text.split('\n')
            for i, line in enumerate(lines):
                if line.strip():
                    content_node = ET.SubElement(section_node, "node")
                    content_node.set("TEXT", line.strip())
                    content_node.set("COLOR", "#FFFFFF")
                    content_node.set("STYLE", "bullet")
        else:
            content_node = ET.SubElement(section_node, "node")
            content_node.set("TEXT", content_text)
            content_node.set("COLOR", "#FFFFFF")
            content_node.set("STYLE", "bullet")
    
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
    
    def _parse_content_to_structure(self, content):
        """解析测试用例内容为结构化的数据格式 - 包含完整用例信息"""
        try:
            lines = content.split('\n')
            structure = {}
            current_module = None
            current_cases = []
            current_case = None
            current_case_content = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    if current_case_content:
                        current_case_content.append("")  # 保留空行
                    continue
                
                # 检测模块标题
                if line.startswith('## '):
                    # 保存之前的测试用例
                    if current_case and current_case_content:
                        # 将完整用例内容合并
                        full_case_text = current_case + "\n" + "\n".join(current_case_content)
                        current_cases.append(full_case_text)
                    
                    # 保存之前的模块
                    if current_module and current_cases:
                        structure[current_module] = current_cases
                    
                    # 开始新模块
                    current_module = line[3:].strip()
                    current_cases = []
                    current_case = None
                    current_case_content = []
                    
                    # 跳过"用例结构总结"模块 - 按用户要求移除总结部分
                    if current_module == "用例结构总结":
                        current_module = None
                        current_cases = []
                        current_case = None
                        current_case_content = []
                        continue
                
                # 检测测试用例
                elif line.startswith('### ') and current_module:
                    # 保存之前的测试用例
                    if current_case and current_case_content:
                        full_case_text = current_case + "\n" + "\n".join(current_case_content)
                        current_cases.append(full_case_text)
                    
                    # 开始新测试用例
                    current_case = line[4:].strip()
                    current_case_content = []
                
                # 收集测试用例的所有内容
                elif current_case and line:
                    # 清理格式标记
                    clean_line = line.replace('**', '').strip()
                    current_case_content.append(clean_line)
            
            # 保存最后一个测试用例
            if current_case and current_case_content:
                full_case_text = current_case + "\n" + "\n".join(current_case_content)
                current_cases.append(full_case_text)
            
            # 保存最后一个模块
            if current_module and current_cases:
                structure[current_module] = current_cases
            
            return {
                "title": "测试用例文档",
                "structure": structure
            }
            
        except Exception as e:
            logger.error(f"解析内容结构失败: {e}")
            return {
                "title": "测试用例文档",
                "structure": {"默认模块": ["解析失败"]}
            }
