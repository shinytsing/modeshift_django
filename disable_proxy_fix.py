#!/usr/bin/env python3
"""
禁用代理修复脚本
"""

def disable_proxy():
    """禁用代理配置"""
    print("🔧 禁用代理配置...")
    
    # 读取文件
    with open('apps/users/services/google_auth_proxy.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换代理配置
    old_proxy_config = """        self.proxy_config = {
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890'
        }"""
    
    new_proxy_config = """        # 禁用代理配置，直接连接Google OAuth服务
        self.proxy_config = None"""
    
    if old_proxy_config in content:
        content = content.replace(old_proxy_config, new_proxy_config)
        print("✅ 代理配置已禁用")
    else:
        print("⚠️  未找到代理配置")
    
    # 写回文件
    with open('apps/users/services/google_auth_proxy.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 文件已更新")

if __name__ == "__main__":
    disable_proxy()
