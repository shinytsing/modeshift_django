#!/usr/bin/env python3
"""
测试搜索条件是否正确传递
"""
import os
import sys
import django

# 添加项目路径
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.services.java_boss_interface_service import java_boss_service

def test_search_conditions():
    """测试搜索条件"""
    test_input = {
        'greeting': '您好，我对这个职位很感兴趣',
        'city': '不限',  # 测试不限选项
        'position': 'Java开发工程师',
        'experience': '不限',  # 测试不限选项
        'minSalary': 20,
        'maxSalary': 50,
        'education': '不限'  # 测试不限选项
    }
    
    print("测试搜索条件传递...")
    print(f"输入: {test_input}")
    
    # 创建配置
    config_file = java_boss_service.create_boss_config(test_input)
    
    # 读取并显示配置内容
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
        print("生成的配置:")
        print(content)

if __name__ == '__main__':
    test_search_conditions()
