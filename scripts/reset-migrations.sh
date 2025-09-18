#!/bin/bash

# 重置迁移脚本
echo "=== 重置服务器迁移状态 ==="

# 1. 停止服务
echo "1. 停止Gunicorn服务..."
pkill -f gunicorn || true
sleep 2

# 2. 备份当前数据库
echo "2. 备份当前数据库..."
cd /root/modeshift_django
source venv/bin/activate
python manage.py dumpdata --natural-foreign --natural-primary > /root/db_backup_$(date +%Y%m%d_%H%M%S).json

# 3. 删除迁移记录表
echo "3. 重置迁移记录..."
python manage.py shell << 'PYTHON_EOF'
from django.db import connection

with connection.cursor() as cursor:
    # 删除django_migrations表中的用户应用记录
    cursor.execute("DELETE FROM django_migrations WHERE app = 'users'")
    print("已删除users应用的迁移记录")
    
    # 删除相关表（如果存在）
    tables_to_drop = [
        'users_userstatus',
        'users_userrole', 
        'users_usermembership',
        'users_useractionlog',
        'users_useractivitylog',
        'users_usersessionstats',
        'users_apiusagestats',
        'users_usertheme',
        'users_usermodepreference'
    ]
    
    for table in tables_to_drop:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
            print(f"已删除表: {table}")
        except Exception as e:
            print(f"删除表 {table} 失败: {e}")

PYTHON_EOF

# 4. 重新运行迁移
echo "4. 重新运行所有迁移..."
python manage.py migrate --fake-initial
python manage.py migrate

# 5. 检查表是否创建成功
echo "5. 检查表创建状态..."
python manage.py shell << 'PYTHON_EOF'
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE 'users_%'
        ORDER BY table_name;
    """)
    
    tables = cursor.fetchall()
    print('用户相关表:')
    for table in tables:
        print(f'  ✅ {table[0]}')

PYTHON_EOF

# 6. 重启服务
echo "6. 重启Gunicorn服务..."
cd /root/modeshift_django
source venv/bin/activate
nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --access-logfile logs/gunicorn_access.log --error-logfile logs/gunicorn_error.log config.wsgi:application > /dev/null 2>&1 &

sleep 3

# 7. 测试服务
echo "7. 测试服务状态..."
curl -I http://localhost:8000/ | head -1

echo "=== 迁移重置完成 ==="
