#!/usr/bin/env python3
"""
最终修复代理配置
"""

def fix_proxy_config():
    """修复代理配置"""
    print("🔧 最终修复代理配置...")
    
    # 读取文件
    with open('apps/users/services/google_auth_proxy.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到__init__方法并替换代理配置
    lines = content.split('\n')
    new_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 找到有问题的代理配置行
        if '# 启用代理配置访问Google OAuth服务        self.proxy_config = {            "http": "http://127.0.0.1:7890",            "https": "http://127.0.0.1:7890"        }' in line:
            # 替换为正确的格式
            new_lines.append('        # 启用代理配置访问Google OAuth服务')
            new_lines.append('        self.proxy_config = {')
            new_lines.append('            "http": "http://127.0.0.1:7890",')
            new_lines.append('            "https": "http://127.0.0.1:7890"')
            new_lines.append('        }')
        else:
            new_lines.append(line)
        i += 1
    
    # 写回文件
    with open('apps/users/services/google_auth_proxy.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ 代理配置已修复")

if __name__ == "__main__":
    fix_proxy_config()
