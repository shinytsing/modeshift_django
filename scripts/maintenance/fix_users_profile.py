#!/usr/bin/env python3
"""修复users_profile表问题"""
import os
import sys
from pathlib import Path

import django

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def fix_profile_table():
    """修复users_profile表"""
    print("检查users_profile表...")

    with connection.cursor() as cursor:
        # 检查表是否存在
        if 'sqlite' in connection.settings_dict['ENGINE']:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users_profile';")
        else:
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name='users_profile';")

        table_exists = cursor.fetchone() is not None

        if not table_exists:
            print("❌ users_profile表不存在，创建表...")
            # 运行迁移创建表
            execute_from_command_line(['manage.py', 'migrate', 'users'])
        else:
            print("✅ users_profile表已存在")

        # 检查表结构
        if 'sqlite' in connection.settings_dict['ENGINE']:
            cursor.execute("PRAGMA table_info(users_profile);")
        else:
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='users_profile';")

        columns = cursor.fetchall()
        print(f"表结构: {len(columns)}个字段")

        return True

if __name__ == "__main__":
    fix_profile_table()
