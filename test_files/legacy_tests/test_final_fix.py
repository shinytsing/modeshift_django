#!/usr/bin/env python3
"""
最终修复验证脚本
验证ID冲突修复和字体优化效果
"""

import requests
import time
import re
from urllib.parse import urljoin

class FinalFixValidator:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def print_header(self, title):
        """打印标题"""
        print("\n" + "="*60)
        print(f"🔧 {title}")
        print("="*60)
        
    def print_status(self, message, status="INFO"):
        """打印状态信息"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] [{status}] {message}")
        
    def test_id_conflicts(self):
        """测试ID冲突修复"""
        self.print_header("ID冲突修复验证")
        
        try:
            response = self.session.get(f"{self.base_url}/test-geek-login/")
            if response.status_code == 200:
                content = response.text
                
                # 检查极客风格弹窗的ID
                geek_ids = [
                    'geekLoginFormElement',
                    'geekRegisterFormElement', 
                    'geekRegisterPasswordInput',
                    'geekRegisterPasswordStrength',
                    'geekRegisterStrengthFill',
                    'geekRegisterStrengthText'
                ]
                
                found_ids = []
                for geek_id in geek_ids:
                    if geek_id in content:
                        found_ids.append(geek_id)
                        self.print_status(f"找到极客风格ID: {geek_id}", "SUCCESS")
                
                # 检查是否还有旧的ID冲突
                old_ids = [
                    'id="loginFormElement"',
                    'id="registerFormElement"',
                    'id="registerPasswordInput"'
                ]
                
                conflicts = []
                for old_id in old_ids:
                    matches = content.count(old_id)
                    if matches > 1:
                        conflicts.append(old_id)
                        self.print_status(f"发现ID冲突: {old_id} (出现{matches}次)", "ERROR")
                    elif matches == 1:
                        self.print_status(f"现代化弹窗ID正常: {old_id}", "SUCCESS")
                
                if not conflicts:
                    self.print_status("✅ 无ID冲突，修复成功！", "SUCCESS")
                    return True
                else:
                    self.print_status(f"❌ 仍有{len(conflicts)}个ID冲突", "ERROR")
                    return False
                    
            else:
                self.print_status(f"页面加载失败: HTTP {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.print_status(f"测试失败: {str(e)}", "ERROR")
            return False
    
    def test_font_optimization(self):
        """测试字体优化效果"""
        self.print_header("字体优化验证")
        
        try:
            response = self.session.get(f"{self.base_url}/test-geek-login/")
            if response.status_code == 200:
                content = response.text
                
                # 检查字体优化相关的CSS
                font_checks = [
                    ("font-size: 16px", "主要文字大小优化"),
                    ("font-size: 14px", "次要文字大小优化"),
                    ("font-size: 6px", "ASCII艺术字体优化"),
                    ("font-family: 'Courier New', 'Monaco', 'Menlo', monospace", "字体家族统一"),
                    ("letter-spacing: 0.5px", "字符间距优化"),
                    ("letter-spacing: 1px", "重要文字间距"),
                    ("font-weight: bold", "字体加粗"),
                    ("font-weight: 500", "中等字体权重")
                ]
                
                found_optimizations = 0
                for check_pattern, description in font_checks:
                    if check_pattern in content:
                        found_optimizations += 1
                        self.print_status(f"✅ {description}", "SUCCESS")
                    else:
                        self.print_status(f"❌ 缺少: {description}", "WARNING")
                
                # 检查弹窗尺寸优化
                size_checks = [
                    ("width: 700px", "弹窗宽度优化"),
                    ("max-width: 90vw", "响应式宽度"),
                    ("max-height: 85vh", "响应式高度"),
                    ("margin: auto", "居中显示")
                ]
                
                for check_pattern, description in size_checks:
                    if check_pattern in content:
                        self.print_status(f"✅ {description}", "SUCCESS")
                    else:
                        self.print_status(f"❌ 缺少: {description}", "WARNING")
                
                if found_optimizations >= 6:
                    self.print_status("✅ 字体优化效果良好", "SUCCESS")
                    return True
                else:
                    self.print_status(f"⚠️ 字体优化不完整 ({found_optimizations}/8)", "WARNING")
                    return False
                    
            else:
                self.print_status(f"页面加载失败: HTTP {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.print_status(f"测试失败: {str(e)}", "ERROR")
            return False
    
    def test_geek_modal_integration(self):
        """测试极客风格弹窗集成"""
        self.print_header("极客风格弹窗集成验证")
        
        try:
            response = self.session.get(f"{self.base_url}/test-geek-login/")
            if response.status_code == 200:
                content = response.text
                
                # 检查关键组件
                components = [
                    ("geek-login-modal", "极客风格弹窗容器"),
                    ("matrix-background", "矩阵背景"),
                    ("particles-background", "粒子背景"),
                    ("terminal-header", "终端标题栏"),
                    ("ascii-logo", "ASCII艺术Logo"),
                    ("command-prompt", "命令行提示符"),
                    ("terminal-messages", "终端消息区域"),
                    ("geek-btn", "极客风格按钮"),
                    ("geek-input", "极客风格输入框"),
                    ("password-strength", "密码强度指示器")
                ]
                
                found_components = 0
                for component_class, description in components:
                    if component_class in content:
                        found_components += 1
                        self.print_status(f"✅ {description}", "SUCCESS")
                    else:
                        self.print_status(f"❌ 缺少: {description}", "ERROR")
                
                # 检查JavaScript函数
                js_functions = [
                    "showGeekLoginModal",
                    "closeGeekLoginModal", 
                    "submitGeekLoginForm",
                    "submitGeekRegisterForm",
                    "switchAuthTab",
                    "updatePasswordStrength"
                ]
                
                js_found = 0
                for js_func in js_functions:
                    if js_func in content:
                        js_found += 1
                        self.print_status(f"✅ JavaScript函数: {js_func}", "SUCCESS")
                    else:
                        self.print_status(f"❌ 缺少JavaScript函数: {js_func}", "ERROR")
                
                if found_components >= 8 and js_found >= 5:
                    self.print_status("✅ 极客风格弹窗集成完整", "SUCCESS")
                    return True
                else:
                    self.print_status(f"⚠️ 集成不完整 (组件:{found_components}/10, JS:{js_found}/6)", "WARNING")
                    return False
                    
            else:
                self.print_status(f"页面加载失败: HTTP {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.print_status(f"测试失败: {str(e)}", "ERROR")
            return False
    
    def test_server_health(self):
        """测试服务器健康状态"""
        self.print_header("服务器健康检查")
        
        try:
            response = self.session.get(f"{self.base_url}/health/")
            if response.status_code == 200:
                health_data = response.json()
                self.print_status(f"服务器状态: {health_data.get('status', 'unknown')}", "SUCCESS")
                self.print_status(f"版本: {health_data.get('version', 'unknown')}", "INFO")
                return True
            else:
                self.print_status(f"健康检查失败: HTTP {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"连接失败: {str(e)}", "ERROR")
            return False
    
    def generate_final_report(self):
        """生成最终报告"""
        self.print_header("最终验证报告")
        
        tests = [
            ("服务器健康检查", self.test_server_health()),
            ("ID冲突修复验证", self.test_id_conflicts()),
            ("字体优化验证", self.test_font_optimization()),
            ("极客风格弹窗集成验证", self.test_geek_modal_integration())
        ]
        
        passed = sum(1 for _, result in tests if result)
        total = len(tests)
        
        self.print_status(f"总测试数: {total}", "INFO")
        self.print_status(f"通过测试: {passed}", "SUCCESS" if passed == total else "WARNING")
        self.print_status(f"失败测试: {total - passed}", "ERROR" if total - passed > 0 else "SUCCESS")
        
        if passed == total:
            self.print_status("🎉 所有测试通过！极客风格登录系统完全正常", "SUCCESS")
            self.print_status("", "INFO")
            self.print_status("🚀 现在可以正常使用以下功能：", "INFO")
            self.print_status("   📱 访问测试页面: http://localhost:8000/test-geek-login/", "INFO")
            self.print_status("   🔐 极客风格登录弹窗", "INFO")
            self.print_status("   ⌨️ 键盘快捷键支持", "INFO")
            self.print_status("   🎨 优化的字体显示", "INFO")
            self.print_status("   🚫 无ID冲突问题", "INFO")
        else:
            self.print_status("⚠️ 部分测试失败，请检查系统配置", "WARNING")
        
        return passed == total

def main():
    """主函数"""
    print("""
    ███╗   ███╗ ██████╗ ██████╗ ███████╗███████╗██╗  ██╗██╗████████╗
    ████╗ ████║██╔═══██╗██╔══██╗██╔════╝██╔════╝██║  ██║██║╚══██╔══╝
    ██╔████╔██║██║   ██║██║  ██║█████╗  ███████╗███████║██║   ██║   
    ██║╚██╔╝██║██║   ██║██║  ██║██╔══╝  ╚════██║██╔══██║██║   ██║   
    ██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗███████║██║  ██║██║   ██║   
    ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝
    
    🔧 最终修复验证
    ⚡ ModeShift Terminal v2.0.1-alpha
    """)
    
    validator = FinalFixValidator()
    success = validator.generate_final_report()
    
    if success:
        print("\n🎯 验证完成！极客风格登录系统已完全就绪！")
    else:
        print("\n❌ 验证失败，请检查上述问题后重试")

if __name__ == "__main__":
    main()
