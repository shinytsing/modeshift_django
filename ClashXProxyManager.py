#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ClashX Pro 代理管理器
功能：一键开启/关闭代理，配置管理，状态监控
适用于Mac系统，可打包分发给朋友使用
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import subprocess
import threading
import time
import os
import sys
import json
import shutil
from pathlib import Path

class ClashXProxyManager:
    def __init__(self, root):
        self.root = root
        self.root.title("ClashX Pro 代理管理器")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # 设置窗口居中
        self.center_window()
        
        # 状态变量
        self.proxy_enabled = False
        self.clashx_running = False
        self.current_config = None
        self.config_path = None
        
        # 配置文件路径
        self.clashx_config_dir = Path.home() / ".config" / "clash"
        self.clashx_config_file = self.clashx_config_dir / "config.yaml"
        
        # 创建界面
        self.create_widgets()
        
        # 初始状态检查
        self.check_status()
        
        # 定时更新状态
        self.update_status()
    
    def center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="ClashX Pro 代理管理器", font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 15))
        
        # 创建选项卡
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 状态监控选项卡
        self.create_status_tab(notebook)
        
        # 配置管理选项卡
        self.create_config_tab(notebook)
        
        # 日志查看选项卡
        self.create_log_tab(notebook)
    
    def create_status_tab(self, parent):
        """创建状态监控选项卡"""
        status_frame = ttk.Frame(parent)
        parent.add(status_frame, text="状态监控")
        
        # 状态显示区域
        status_info_frame = ttk.LabelFrame(status_frame, text="系统状态", padding="10")
        status_info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # ClashX Pro 状态
        self.clashx_status_label = ttk.Label(status_info_frame, text="ClashX Pro: 检查中...", font=("Arial", 12))
        self.clashx_status_label.pack(anchor=tk.W, pady=2)
        
        # 代理状态
        self.proxy_status_label = ttk.Label(status_info_frame, text="系统代理: 检查中...", font=("Arial", 12))
        self.proxy_status_label.pack(anchor=tk.W, pady=2)
        
        # 当前IP
        self.ip_label = ttk.Label(status_info_frame, text="当前IP: 获取中...", font=("Arial", 12))
        self.ip_label.pack(anchor=tk.W, pady=2)
        
        # 网络接口
        self.interface_label = ttk.Label(status_info_frame, text="网络接口: 获取中...", font=("Arial", 12))
        self.interface_label.pack(anchor=tk.W, pady=2)
        
        # 操作按钮区域
        button_frame = ttk.LabelFrame(status_frame, text="快速操作", padding="10")
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 主要操作按钮
        self.main_button = ttk.Button(button_frame, text="检查状态", command=self.check_status, style="Accent.TButton")
        self.main_button.pack(side=tk.LEFT, padx=5)
        
        # 其他功能按钮
        ttk.Button(button_frame, text="测试连接", command=self.test_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="管理界面", command=self.open_management).pack(side=tk.LEFT, padx=5)
        
        # 启动ClashX按钮
        self.start_clashx_button = ttk.Button(button_frame, text="启动 ClashX Pro", command=self.start_clashx)
        self.start_clashx_button.pack(side=tk.LEFT, padx=5)
        
        # 服务器信息区域
        server_frame = ttk.LabelFrame(status_frame, text="服务器信息", padding="10")
        server_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(server_frame, text="服务器: 47.103.143.152", font=("Arial", 10)).pack(anchor=tk.W)
        ttk.Label(server_frame, text="域名: shenyiqing.xin", font=("Arial", 10)).pack(anchor=tk.W)
        ttk.Label(server_frame, text="用户: root", font=("Arial", 10)).pack(anchor=tk.W)
    
    def create_config_tab(self, parent):
        """创建配置管理选项卡"""
        config_frame = ttk.Frame(parent)
        parent.add(config_frame, text="配置管理")
        
        # 配置文件信息
        config_info_frame = ttk.LabelFrame(config_frame, text="配置文件信息", padding="10")
        config_info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.config_path_label = ttk.Label(config_info_frame, text=f"配置文件路径: {self.clashx_config_file}", font=("Arial", 10))
        self.config_path_label.pack(anchor=tk.W)
        
        self.config_status_label = ttk.Label(config_info_frame, text="配置文件状态: 检查中...", font=("Arial", 10))
        self.config_status_label.pack(anchor=tk.W)
        
        # 配置操作按钮
        config_button_frame = ttk.Frame(config_frame)
        config_button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(config_button_frame, text="导入配置文件", command=self.import_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(config_button_frame, text="导出配置文件", command=self.export_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(config_button_frame, text="重置配置", command=self.reset_config).pack(side=tk.LEFT, padx=5)
        
        # 配置文件预览
        preview_frame = ttk.LabelFrame(config_frame, text="配置文件预览", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.config_preview = scrolledtext.ScrolledText(preview_frame, height=15, font=("Courier", 9))
        self.config_preview.pack(fill=tk.BOTH, expand=True)
        
        # 加载配置文件预览
        self.load_config_preview()
    
    def create_log_tab(self, parent):
        """创建日志查看选项卡"""
        log_frame = ttk.Frame(parent)
        parent.add(log_frame, text="操作日志")
        
        # 日志控制按钮
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(log_control_frame, text="清除日志", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_control_frame, text="保存日志", command=self.save_log).pack(side=tk.LEFT, padx=5)
        
        # 日志显示区域
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, font=("Courier", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 添加初始日志
        self.log("应用启动完成")
    
    def log(self, message):
        """添加日志"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
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
            self.main_button.config(text="关闭代理", command=self.disable_proxy)
        else:
            self.proxy_status_label.config(text="系统代理: ❌ 未启用", foreground="red")
            self.main_button.config(text="开启代理", command=self.enable_proxy)
        
        # 获取当前IP
        self.get_current_ip()
        
        # 获取网络接口信息
        self.get_network_interface()
        
        # 更新启动按钮状态
        if self.clashx_running:
            self.start_clashx_button.config(state="disabled")
        else:
            self.start_clashx_button.config(state="normal")
        
        # 检查配置文件状态
        self.check_config_status()
        
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
    
    def get_network_interface(self):
        """获取网络接口信息"""
        def get_interface():
            try:
                success, stdout, stderr = self.run_command("networksetup -listallhardwareports")
                if success:
                    # 解析网络接口信息
                    lines = stdout.split('\n')
                    for line in lines:
                        if 'Hardware Port:' in line and 'Wi-Fi' in line:
                            self.interface_label.config(text="网络接口: Wi-Fi", foreground="blue")
                            return
                    self.interface_label.config(text="网络接口: 未知", foreground="orange")
                else:
                    self.interface_label.config(text="网络接口: 获取失败", foreground="red")
            except:
                self.interface_label.config(text="网络接口: 获取失败", foreground="red")
        
        # 在后台线程中获取接口信息
        threading.Thread(target=get_interface, daemon=True).start()
    
    def check_config_status(self):
        """检查配置文件状态"""
        if self.clashx_config_file.exists():
            self.config_status_label.config(text="配置文件状态: ✅ 存在", foreground="green")
        else:
            self.config_status_label.config(text="配置文件状态: ❌ 不存在", foreground="red")
    
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
    
    def import_config(self):
        """导入配置文件"""
        file_path = filedialog.askopenfilename(
            title="选择ClashX配置文件",
            filetypes=[("YAML files", "*.yaml"), ("YML files", "*.yml"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # 确保配置目录存在
                self.clashx_config_dir.mkdir(parents=True, exist_ok=True)
                
                # 复制配置文件
                shutil.copy2(file_path, self.clashx_config_file)
                
                self.log(f"✅ 配置文件导入成功: {file_path}")
                messagebox.showinfo("成功", "配置文件导入成功！")
                
                # 更新配置预览
                self.load_config_preview()
                self.check_config_status()
                
            except Exception as e:
                self.log(f"❌ 配置文件导入失败: {e}")
                messagebox.showerror("错误", f"配置文件导入失败：{e}")
    
    def export_config(self):
        """导出配置文件"""
        if not self.clashx_config_file.exists():
            messagebox.showwarning("警告", "配置文件不存在，无法导出")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存ClashX配置文件",
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("YML files", "*.yml"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                shutil.copy2(self.clashx_config_file, file_path)
                self.log(f"✅ 配置文件导出成功: {file_path}")
                messagebox.showinfo("成功", "配置文件导出成功！")
                
            except Exception as e:
                self.log(f"❌ 配置文件导出失败: {e}")
                messagebox.showerror("错误", f"配置文件导出失败：{e}")
    
    def reset_config(self):
        """重置配置"""
        if messagebox.askyesno("确认", "确定要重置配置文件吗？这将删除当前的ClashX配置。"):
            try:
                if self.clashx_config_file.exists():
                    self.clashx_config_file.unlink()
                    self.log("✅ 配置文件已重置")
                    messagebox.showinfo("成功", "配置文件已重置！")
                    
                    # 更新配置预览
                    self.load_config_preview()
                    self.check_config_status()
                else:
                    messagebox.showinfo("提示", "配置文件不存在，无需重置")
                    
            except Exception as e:
                self.log(f"❌ 重置配置文件失败: {e}")
                messagebox.showerror("错误", f"重置配置文件失败：{e}")
    
    def load_config_preview(self):
        """加载配置文件预览"""
        self.config_preview.delete(1.0, tk.END)
        
        if self.clashx_config_file.exists():
            try:
                with open(self.clashx_config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.config_preview.insert(1.0, content)
            except Exception as e:
                self.config_preview.insert(1.0, f"读取配置文件失败: {e}")
        else:
            self.config_preview.insert(1.0, "配置文件不存在")
    
    def clear_log(self):
        """清除日志"""
        self.log_text.delete(1.0, tk.END)
        self.log("日志已清除")
    
    def save_log(self):
        """保存日志"""
        file_path = filedialog.asksaveasfilename(
            title="保存日志文件",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log(f"✅ 日志保存成功: {file_path}")
                messagebox.showinfo("成功", "日志保存成功！")
                
            except Exception as e:
                self.log(f"❌ 日志保存失败: {e}")
                messagebox.showerror("错误", f"日志保存失败：{e}")
    
    def update_status(self):
        """定时更新状态"""
        self.check_status()
        # 每30秒更新一次状态
        self.root.after(30000, self.update_status)

def main():
    # 检查Python版本
    if sys.version_info < (3, 6):
        messagebox.showerror("错误", "需要Python 3.6或更高版本")
        return
    
    # 检查tkinter
    try:
        import tkinter
    except ImportError:
        messagebox.showerror("错误", "tkinter未安装，请安装tkinter")
        return
    
    root = tk.Tk()
    app = ClashXProxyManager(root)
    
    # 设置窗口图标（如果有的话）
    try:
        root.iconbitmap("proxy_icon.ico")
    except:
        pass
    
    root.mainloop()

if __name__ == "__main__":
    main()
