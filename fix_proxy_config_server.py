#!/usr/bin/env python3
"""
修复服务器上的代理配置问题
"""

def fix_proxy_config():
    """修复代理配置"""
    print("🔧 修复代理配置...")
    
    # 读取文件
    with open('apps/users/services/google_auth_proxy.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并替换有问题的代理配置
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        if '# 禁用代理配置，直接连接Google OAuth服务        self.proxy_config = None' in line:
            # 修复这一行
            new_lines.append('        # 禁用代理配置，直接连接Google OAuth服务')
            new_lines.append('        self.proxy_config = None')
        else:
            new_lines.append(line)
    
    # 写回文件
    with open('apps/users/services/google_auth_proxy.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ 代理配置已修复")

if __name__ == "__main__":
    fix_proxy_config()
