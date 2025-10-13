# 核心任务执行模块 (core/tasks.py)

import subprocess
import json
import time
import threading
import os
import logging
from datetime import datetime
from pathlib import Path
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

class TestExecutor:
    """测试执行器"""
    
    def __init__(self):
        self.is_running = False
        self.progress = 0
        self.current_test = ""
        self.test_results = {}
        self.channel_layer = get_channel_layer()
        self.test_start_time = None
        self.test_end_time = None
        
    def send_progress_update(self, progress, current_test="", status="running"):
        """发送进度更新到前端"""
        if self.channel_layer:
            async_to_sync(self.channel_layer.group_send)(
                "test_progress",
                {
                    "type": "test_progress_update",
                    "progress": progress,
                    "current_test": current_test,
                    "status": status,
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def update_progress(self, progress, current_test=""):
        """更新测试进度"""
        self.progress = progress
        self.current_test = current_test
        self.send_progress_update(progress, current_test)
        logger.info(f"测试进度: {progress}% - {current_test}")
    
    def run_pytest_command(self, test_path="", test_type=""):
        """执行pytest命令"""
        try:
            # 构建pytest命令
            cmd = [
                "pytest",
                "--alluredir", str(settings.ALLURE_RESULTS_DIR),
                "--tb=short",
                "-v"
            ]
            
            if test_path:
                cmd.append(test_path)
            
            if test_type:
                cmd.extend(["-m", test_type])
            
            logger.info(f"执行命令: {' '.join(cmd)}")
            
            # 执行测试
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=settings.BASE_DIR
            )
            
            # 实时读取输出并更新进度
            total_tests = 0
            completed_tests = 0
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                
                if output:
                    line = output.strip()
                    logger.info(f"pytest输出: {line}")
                    
                    # 解析测试进度
                    if "test session starts" in line:
                        self.update_progress(5, "测试会话开始")
                    elif "collected" in line and "item" in line:
                        # 提取测试总数
                        try:
                            total_tests = int(line.split()[1])
                            self.update_progress(10, f"收集到 {total_tests} 个测试")
                        except:
                            pass
                    elif "PASSED" in line or "FAILED" in line or "ERROR" in line:
                        completed_tests += 1
                        if total_tests > 0:
                            progress = 10 + int((completed_tests / total_tests) * 80)
                            test_name = line.split()[0] if " " in line else "测试执行中"
                            self.update_progress(progress, test_name)
                    
                    # 发送实时输出到前端
                    self.send_test_output(line)
            
            return process.returncode == 0
            
        except Exception as e:
            logger.error(f"执行pytest命令失败: {str(e)}")
            self.send_progress_update(0, "", "error")
            return False
    
    def generate_allure_report(self):
        """生成Allure报告"""
        try:
            self.update_progress(90, "生成测试报告")
            
            # 确保报告目录存在
            settings.ALLURE_REPORT_DIR.mkdir(parents=True, exist_ok=True)
            
            # 生成Allure报告
            cmd = [
                "allure",
                "generate",
                str(settings.ALLURE_RESULTS_DIR),
                "-o",
                str(settings.ALLURE_REPORT_DIR),
                "--clean"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.update_progress(95, "报告生成完成")
                return True
            else:
                logger.error(f"生成Allure报告失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"生成Allure报告异常: {str(e)}")
            return False
    
    def parse_test_results(self):
        """解析测试结果"""
        try:
            # 读取Allure结果文件
            results_dir = settings.ALLURE_RESULTS_DIR
            if not results_dir.exists():
                return {}
            
            test_results = {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "broken": 0,
                "categories": {
                    "functional": {"passed": 0, "failed": 0, "total": 0},
                    "api": {"passed": 0, "failed": 0, "total": 0},
                    "performance": {"passed": 0, "failed": 0, "total": 0},
                    "security": {"passed": 0, "failed": 0, "total": 0},
                    "ui": {"passed": 0, "failed": 0, "total": 0}
                },
                "duration": 0,
                "timestamp": datetime.now().isoformat()
            }
            
            # 解析JSON结果文件
            for json_file in results_dir.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    test_results["total"] += 1
                    
                    # 统计测试状态
                    status = data.get("status", "unknown")
                    if status == "passed":
                        test_results["passed"] += 1
                    elif status == "failed":
                        test_results["failed"] += 1
                    elif status == "skipped":
                        test_results["skipped"] += 1
                    elif status == "broken":
                        test_results["broken"] += 1
                    
                    # 按类别统计
                    test_name = data.get("name", "")
                    if "functional" in test_name.lower():
                        category = "functional"
                    elif "api" in test_name.lower():
                        category = "api"
                    elif "performance" in test_name.lower():
                        category = "performance"
                    elif "security" in test_name.lower():
                        category = "security"
                    elif "ui" in test_name.lower():
                        category = "ui"
                    else:
                        category = "functional"  # 默认分类
                    
                    test_results["categories"][category]["total"] += 1
                    if status == "passed":
                        test_results["categories"][category]["passed"] += 1
                    else:
                        test_results["categories"][category]["failed"] += 1
                    
                    # 计算执行时间
                    if "start" in data and "stop" in data:
                        duration = data["stop"] - data["start"]
                        test_results["duration"] += duration
                        
                except Exception as e:
                    logger.error(f"解析测试结果文件失败 {json_file}: {str(e)}")
                    continue
            
            return test_results
            
        except Exception as e:
            logger.error(f"解析测试结果失败: {str(e)}")
            return {}
    
    def send_test_output(self, output):
        """发送测试输出到前端"""
        if self.channel_layer:
            async_to_sync(self.channel_layer.group_send)(
                "test_output",
                {
                    "type": "test_output_update",
                    "output": output,
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def run_all_tests(self):
        """执行所有测试"""
        if self.is_running:
            return False
        
        self.is_running = True
        self.progress = 0
        self.test_start_time = datetime.now()
        
        try:
            logger.info("开始执行测试")
            self.update_progress(0, "准备测试环境")
            
            # 清理之前的测试结果
            if settings.ALLURE_RESULTS_DIR.exists():
                import shutil
                shutil.rmtree(settings.ALLURE_RESULTS_DIR)
            settings.ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
            
            # 执行测试
            success = self.run_pytest_command()
            
            if success:
                # 生成报告
                self.generate_allure_report()
                
                # 解析结果
                self.test_results = self.parse_test_results()
                
                self.update_progress(100, "测试完成")
                self.send_progress_update(100, "测试完成", "completed")
                
            else:
                self.send_progress_update(0, "测试执行失败", "failed")
            
            self.test_end_time = datetime.now()
            return success
            
        except Exception as e:
            logger.error(f"执行测试异常: {str(e)}")
            self.send_progress_update(0, f"测试异常: {str(e)}", "error")
            return False
        finally:
            self.is_running = False
    
    def run_specific_tests(self, test_types):
        """执行特定类型的测试"""
        if self.is_running:
            return False
        
        self.is_running = True
        self.progress = 0
        
        try:
            logger.info(f"开始执行特定测试: {test_types}")
            
            for test_type in test_types:
                test_path = f"tests/{test_type}/"
                success = self.run_pytest_command(test_path, test_type)
                
                if not success:
                    break
            
            # 生成报告
            self.generate_allure_report()
            self.test_results = self.parse_test_results()
            
            self.update_progress(100, "测试完成")
            return True
            
        except Exception as e:
            logger.error(f"执行特定测试异常: {str(e)}")
            return False
        finally:
            self.is_running = False
    
    def get_status(self):
        """获取当前状态"""
        return {
            "is_running": self.is_running,
            "progress": self.progress,
            "current_test": self.current_test,
            "test_results": self.test_results,
            "start_time": self.test_start_time.isoformat() if self.test_start_time else None,
            "end_time": self.test_end_time.isoformat() if self.test_end_time else None
        }

# 全局测试执行器实例
test_executor = TestExecutor()
