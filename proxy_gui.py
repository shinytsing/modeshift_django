#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代理开关 Mac 应用
功能：一键开启/关闭代理，显示状态
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import os

class ProxySwitchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("代理开关")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        
        # 设置窗口图标（如果有的话）
        try:
            self.root.iconbitmap("proxy_icon.ico")
        except:
            pass
        
        # 状态变量
        self.proxy_enabled = False
        self.clashx_running = False
        
        # 创建界面
        self.create_widgets()
        
        # 初始状态检查
        self.check_status()
        
        # 定时更新状态
        self.update_status()
    
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="代理开关", font=("Arial", 20, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 状态显示区域
        status_frame = ttk.LabelFrame(main_frame, text="状态信息", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # ClashX Pro 状态
        self.clashx_status_label = ttk.Label(status_frame, text="ClashX Pro: 检查中...", font=("Arial", 12))
        self.clashx_status_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # 代理状态
        self.proxy_status_label = ttk.Label(status_frame, text="系统代理: 检查中...", font=("Arial", 12))
        self.proxy_status_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # 当前IP
        self.ip_label = ttk.Label(status_frame, text="当前IP: 获取中...", font=("Arial", 12))
        self.ip_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # 服务器信息
        server_frame = ttk.LabelFrame(main_frame, text="服务器信息", padding="10")
        server_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(server_frame, text="服务器: 47.103.143.152", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(server_frame, text="域名: shenyiqing.xin", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W)
        ttk.Label(server_frame, text="用户: root", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(0, 20))
        
        # 主要操作按钮
        self.main_button = ttk.Button(button_frame, text="检查状态", command=self.check_status, style="Accent.TButton")
        self.main_button.grid(row=0, column=0, padx=5, pady=5)
        
        # 其他功能按钮
        ttk.Button(button_frame, text="测试连接", command=self.test_connection).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="管理界面", command=self.open_management).grid(row=0, column=2, padx=5, pady=5)
        
        # 启动ClashX按钮
        self.start_clashx_button = ttk.Button(button_frame, text="启动 ClashX Pro", command=self.start_clashx)
        self.start_clashx_button.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 日志文本框
        self.log_text = tk.Text(log_frame, height=8, width=50, font=("Courier", 9))
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置网格权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 添加初始日志
        self.log("应用启动完成")
    
    def log(self, message):
        """添加日志"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def run_command(self, command):
        """执行shell命令"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "命令执行超时"
        except Exception as e:
            return False, "", str(e)
    
    def check_status(self):
        """检查代理状态"""
        self.log("检查代理状态...")
        
        # 检查ClashX Pro是否运行
        success, stdout, stderr = self.run_command("pgrep -f 'ClashX Pro'")
        self.clashx_running = success
        
        if self.clashx_running:
            self.clashx_status_label.config(text="ClashX Pro: ✅ 运行中", foreground="green")
        else:
            self.clashx_status_label.config(text="ClashX Pro: ❌ 未运行", foreground="red")
        
        # 检查系统代理设置
        success, stdout, stderr = self.run_command("networksetup -getwebproxy 'Wi-Fi'")
        self.proxy_enabled = success and "Enabled: Yes" in stdout
        
        if self.proxy_enabled:
            self.proxy_status_label.config(text="系统代理: ✅ 已启用", foreground="green")
            self.main_button.config(text="关闭代理")
        else:
            self.proxy_status_label.config(text="系统代理: ❌ 未启用", foreground="red")
            self.main_button.config(text="开启代理")
        
        # 获取当前IP
        self.get_current_ip()
        
        # 更新启动按钮状态
        if self.clashx_running:
            self.start_clashx_button.config(state="disabled")
        else:
            self.start_clashx_button.config(state="normal")
        
        self.log("状态检查完成")
    
    def get_current_ip(self):
        """获取当前IP地址"""
        def get_ip():
            try:
                if self.proxy_enabled:
                    success, stdout, stderr = self.run_command("curl -x http://127.0.0.1:7890 -s https://httpbin.org/ip")
                else:
                    success, stdout, stderr = self.run_command("curl -s https://httpbin.org/ip")
                
                if success and stdout:
                    import json
                    ip_data = json.loads(stdout)
                    ip = ip_data.get('origin', '未知')
                    self.ip_label.config(text=f"当前IP: {ip}", foreground="blue")
                else:
                    self.ip_label.config(text="当前IP: 获取失败", foreground="red")
            except:
                self.ip_label.config(text="当前IP: 获取失败", foreground="red")
        
        # 在后台线程中获取IP
        threading.Thread(target=get_ip, daemon=True).start()
    
    def toggle_proxy(self):
        """切换代理状态"""
        if self.proxy_enabled:
            self.disable_proxy()
        else:
            self.enable_proxy()
    
    def enable_proxy(self):
        """开启代理"""
        self.log("正在开启代理...")
        
        def enable():
            try:
                # 设置系统代理
                commands = [
                    "networksetup -setwebproxy 'Wi-Fi' 127.0.0.1 7890",
                    "networksetup -setsecurewebproxy 'Wi-Fi' 127.0.0.1 7890",
                    "networksetup -setsocksfirewallproxy 'Wi-Fi' 127.0.0.1 7891"
                ]
                
                for cmd in commands:
                    success, stdout, stderr = self.run_command(cmd)
                    if not success:
                        self.log(f"命令执行失败: {cmd}")
                        return False
                
                # 测试连接
                success, stdout, stderr = self.run_command("curl -x http://127.0.0.1:7890 -I https://www.google.com --connect-timeout 5")
                
                if success:
                    self.log("✅ 代理开启成功，Google连接测试通过")
                    messagebox.showinfo("成功", "代理已成功开启！\nGoogle连接测试通过")
                else:
                    self.log("⚠️ 代理已开启，但连接测试失败")
                    messagebox.showwarning("警告", "代理已开启，但连接测试失败\n请检查ClashX Pro配置")
                
                # 更新状态
                self.check_status()
                return True
                
            except Exception as e:
                self.log(f"❌ 开启代理失败: {e}")
                messagebox.showerror("错误", f"开启代理失败：{e}")
                return False
        
        # 在后台线程中执行
        threading.Thread(target=enable, daemon=True).start()
    
    def disable_proxy(self):
        """关闭代理"""
        self.log("正在关闭代理...")
        
        def disable():
            try:
                # 关闭系统代理
                commands = [
                    "networksetup -setwebproxystate 'Wi-Fi' off",
                    "networksetup -setsecurewebproxystate 'Wi-Fi' off",
                    "networksetup -setsocksfirewallproxystate 'Wi-Fi' off"
                ]
                
                for cmd in commands:
                    success, stdout, stderr = self.run_command(cmd)
                    if not success:
                        self.log(f"命令执行失败: {cmd}")
                        return False
                
                # 测试直连
                success, stdout, stderr = self.run_command("curl -I https://www.baidu.com --connect-timeout 5")
                
                if success:
                    self.log("✅ 代理关闭成功，百度连接测试通过")
                    messagebox.showinfo("成功", "代理已成功关闭！\n百度连接测试通过（直连）")
                else:
                    self.log("⚠️ 代理已关闭，但连接测试失败")
                    messagebox.showwarning("警告", "代理已关闭，但连接测试失败")
                
                # 更新状态
                self.check_status()
                return True
                
            except Exception as e:
                self.log(f"❌ 关闭代理失败: {e}")
                messagebox.showerror("错误", f"关闭代理失败：{e}")
                return False
        
        # 在后台线程中执行
        threading.Thread(target=disable, daemon=True).start()
    
    def start_clashx(self):
        """启动ClashX Pro"""
        self.log("正在启动ClashX Pro...")
        
        def start():
            try:
                # 启动ClashX Pro
                success, stdout, stderr = self.run_command("open -a 'ClashX Pro'")
                
                if success:
                    time.sleep(3)  # 等待启动
                    
                    # 检查是否启动成功
                    success, stdout, stderr = self.run_command("pgrep -f 'ClashX Pro'")
                    
                    if success:
                        self.log("✅ ClashX Pro 启动成功")
                        messagebox.showinfo("成功", "ClashX Pro 启动成功！")
                        self.check_status()
                    else:
                        self.log("❌ ClashX Pro 启动失败")
                        messagebox.showerror("失败", "ClashX Pro 启动失败\n请确保ClashX Pro已正确安装")
                else:
                    self.log("❌ 无法启动ClashX Pro")
                    messagebox.showerror("错误", "无法启动ClashX Pro")
                    
            except Exception as e:
                self.log(f"❌ 启动ClashX Pro失败: {e}")
                messagebox.showerror("错误", f"启动ClashX Pro失败：{e}")
        
        # 在后台线程中执行
        threading.Thread(target=start, daemon=True).start()
    
    def test_connection(self):
        """测试连接"""
        self.log("正在测试连接...")
        
        def test():
            try:
                sites = [
                    ("Google", "https://www.google.com"),
                    ("YouTube", "https://www.youtube.com"),
                    ("GitHub", "https://www.github.com")
                ]
                
                results = []
                for name, url in sites:
                    success, stdout, stderr = self.run_command(f"curl -x http://127.0.0.1:7890 -I {url} --connect-timeout 10 --max-time 15")
                    if success:
                        results.append(f"✅ {name}连接成功")
                        self.log(f"✅ {name}连接成功")
                    else:
                        results.append(f"❌ {name}连接失败")
                        self.log(f"❌ {name}连接失败")
                
                # 获取当前IP
                success, stdout, stderr = self.run_command("curl -x http://127.0.0.1:7890 -s https://httpbin.org/ip")
                if success and stdout:
                    import json
                    ip_data = json.loads(stdout)
                    current_ip = ip_data.get('origin', '未知')
                    results.append(f"当前IP: {current_ip}")
                
                messagebox.showinfo("测试结果", "\n".join(results))
                
            except Exception as e:
                self.log(f"❌ 测试连接失败: {e}")
                messagebox.showerror("错误", f"测试连接失败：{e}")
        
        # 在后台线程中执行
        threading.Thread(target=test, daemon=True).start()
    
    def open_management(self):
        """打开管理界面"""
        self.log("打开管理界面...")
        success, stdout, stderr = self.run_command("open http://127.0.0.1:9090")
        if success:
            self.log("✅ 管理界面已打开")
        else:
            self.log("❌ 打开管理界面失败")
            messagebox.showerror("错误", "打开管理界面失败")
    
    def update_status(self):
        """定时更新状态"""
        self.check_status()
        # 每30秒更新一次状态
        self.root.after(30000, self.update_status)

def main():
    root = tk.Tk()
    app = ProxySwitchApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
