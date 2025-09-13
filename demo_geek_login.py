#!/usr/bin/env python3
"""
极客风格登录系统演示脚本
展示登录检查系统的各种功能
"""

import requests
import time
import json
from urllib.parse import urljoin

class GeekLoginDemo:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def print_header(self, title):
        """打印极客风格的标题"""
        print("\n" + "="*60)
        print(f"🔐 {title}")
        print("="*60)
        
    def print_status(self, message, status="INFO"):
        """打印状态信息"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] [{status}] {message}")
        
    def test_server_health(self):
        """测试服务器健康状态"""
        self.print_header("服务器健康检查")
        
        try:
            response = self.session.get(f"{self.base_url}/health/")
            if response.status_code == 200:
                health_data = response.json()
                self.print_status(f"服务器状态: {health_data.get('status', 'unknown')}", "SUCCESS")
                self.print_status(f"版本: {health_data.get('version', 'unknown')}", "INFO")
                self.print_status(f"时间戳: {health_data.get('timestamp', 'unknown')}", "INFO")
                return True
            else:
                self.print_status(f"健康检查失败: HTTP {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"连接失败: {str(e)}", "ERROR")
            return False
    
    def test_home_page(self):
        """测试首页加载"""
        self.print_header("首页加载测试")
        
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.print_status("首页加载成功", "SUCCESS")
                
                # 检查是否包含极客登录相关的内容
                content = response.text
                if "geek-login-modal" in content:
                    self.print_status("极客风格登录弹窗已集成", "SUCCESS")
                else:
                    self.print_status("极客风格登录弹窗未找到", "WARNING")
                
                if "login_check.js" in content:
                    self.print_status("登录检查系统已加载", "SUCCESS")
                else:
                    self.print_status("登录检查系统未找到", "WARNING")
                    
                return True
            else:
                self.print_status(f"首页加载失败: HTTP {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"首页加载失败: {str(e)}", "ERROR")
            return False
    
    def test_geek_login_page(self):
        """测试极客登录测试页面"""
        self.print_header("极客登录测试页面")
        
        try:
            response = self.session.get(f"{self.base_url}/test-geek-login/")
            if response.status_code == 200:
                self.print_status("极客登录测试页面加载成功", "SUCCESS")
                
                content = response.text
                
                # 检查关键元素
                checks = [
                    ("极客风格登录弹窗测试", "页面标题"),
                    ("login-btn", "登录按钮"),
                    ("tool-btn", "工具按钮"),
                    ("showGeekLoginModal", "极客登录函数"),
                    ("checkLoginStatus", "登录状态检查"),
                    ("loginCheckSystem", "登录检查系统")
                ]
                
                for check_text, description in checks:
                    if check_text in content:
                        self.print_status(f"{description} 已找到", "SUCCESS")
                    else:
                        self.print_status(f"{description} 未找到", "WARNING")
                
                return True
            else:
                self.print_status(f"测试页面加载失败: HTTP {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"测试页面加载失败: {str(e)}", "ERROR")
            return False
    
    def test_static_files(self):
        """测试静态文件加载"""
        self.print_header("静态文件检查")
        
        static_files = [
            "/static/js/login_check.js",
            "/static/favicon.svg",
            "/static/favicon.ico"
        ]
        
        success_count = 0
        for file_path in static_files:
            try:
                response = self.session.get(f"{self.base_url}{file_path}")
                if response.status_code == 200:
                    self.print_status(f"静态文件 {file_path} 加载成功", "SUCCESS")
                    success_count += 1
                else:
                    self.print_status(f"静态文件 {file_path} 加载失败: HTTP {response.status_code}", "WARNING")
            except Exception as e:
                self.print_status(f"静态文件 {file_path} 加载失败: {str(e)}", "ERROR")
        
        return success_count > 0
    
    def test_user_endpoints(self):
        """测试用户相关端点"""
        self.print_header("用户端点测试")
        
        endpoints = [
            ("/users/login/", "登录页面"),
            ("/users/register/", "注册页面"),
            ("/users/api/login/", "登录API"),
            ("/users/api/register/", "注册API")
        ]
        
        success_count = 0
        for endpoint, description in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code in [200, 405]:  # 405表示方法不允许，但端点存在
                    self.print_status(f"{description} 端点可访问", "SUCCESS")
                    success_count += 1
                else:
                    self.print_status(f"{description} 端点访问失败: HTTP {response.status_code}", "WARNING")
            except Exception as e:
                self.print_status(f"{description} 端点访问失败: {str(e)}", "ERROR")
        
        return success_count > 0
    
    def generate_report(self):
        """生成测试报告"""
        self.print_header("测试报告生成")
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "base_url": self.base_url,
            "tests": [
                "服务器健康检查",
                "首页加载测试", 
                "极客登录测试页面",
                "静态文件检查",
                "用户端点测试"
            ],
            "status": "测试完成"
        }
        
        report_file = f"geek_login_test_report_{int(time.time())}.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            self.print_status(f"测试报告已保存: {report_file}", "SUCCESS")
        except Exception as e:
            self.print_status(f"保存测试报告失败: {str(e)}", "ERROR")
    
    def run_all_tests(self):
        """运行所有测试"""
        self.print_header("极客风格登录系统演示")
        self.print_status("开始系统测试...", "INFO")
        
        tests = [
            self.test_server_health,
            self.test_home_page,
            self.test_geek_login_page,
            self.test_static_files,
            self.test_user_endpoints
        ]
        
        passed = 0
        total = len(tests)
        
        for i, test in enumerate(tests):
            try:
                if test():
                    passed += 1
                else:
                    self.print_status(f"测试 {i+1} 失败", "ERROR")
            except Exception as e:
                self.print_status(f"测试 {i+1} 执行失败: {str(e)}", "ERROR")
        
        self.print_header("测试结果汇总")
        self.print_status(f"总测试数: {total}", "INFO")
        self.print_status(f"通过测试: {passed}", "SUCCESS" if passed == total else "WARNING")
        self.print_status(f"失败测试: {total - passed}", "ERROR" if total - passed > 0 else "SUCCESS")
        
        if passed == total:
            self.print_status("🎉 所有测试通过！极客风格登录系统运行正常", "SUCCESS")
        else:
            self.print_status("⚠️  部分测试失败，请检查系统配置", "WARNING")
        
        self.generate_report()
        
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
    
    🔐 极客风格登录系统演示
    ⚡ ModeShift Terminal v2.0.1-alpha
    """)
    
    demo = GeekLoginDemo()
    success = demo.run_all_tests()
    
    if success:
        print("\n🚀 系统就绪！请访问以下链接测试极客风格登录系统：")
        print(f"   📱 测试页面: {demo.base_url}/test-geek-login/")
        print(f"   🏠 首页: {demo.base_url}/")
        print(f"   🔐 登录页面: {demo.base_url}/users/login/")
        print("\n⌨️  键盘快捷键:")
        print("   L - 切换到登录标签")
        print("   R - 切换到注册标签") 
        print("   G - Google一键登录")
        print("   ESC - 关闭登录弹窗")
    else:
        print("\n❌ 系统测试失败，请检查配置后重试")

if __name__ == "__main__":
    main()
