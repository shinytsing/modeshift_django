#!/usr/bin/env python
"""
查看验证码脚本
"""
import json
import os
from django.conf import settings

# 设置Django环境
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

def show_verification_codes():
    """显示验证码"""
    codes_file = os.path.join(settings.BASE_DIR, 'verification_codes.json')
    
    try:
        with open(codes_file, 'r', encoding='utf-8') as f:
            codes = json.load(f)
        
        print(f"📋 可用验证码列表 (共 {len(codes)} 个):")
        print("=" * 50)
        
        # 显示前10个验证码
        for i, code in enumerate(codes[:10], 1):
            print(f"{i:2d}. {code}")
        
        if len(codes) > 10:
            print(f"... 还有 {len(codes) - 10} 个验证码")
            
    except FileNotFoundError:
        print("❌ 验证码文件不存在")
    except json.JSONDecodeError:
        print("❌ 验证码文件格式错误")

if __name__ == "__main__":
    show_verification_codes()
