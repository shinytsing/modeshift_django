#!/bin/bash

echo "🔍 开始调试部署..."

# 设置详细输出
set -x

# 1. 检查基本环境
echo "=== 环境检查 ==="
whoami
pwd
ls -la

# 2. 检查Python环境
echo "=== Python环境检查 ==="
python3 --version || echo "Python3未安装"
pip3 --version || echo "pip3未安装"

# 3. 检查系统服务
echo "=== 系统服务检查 ==="
systemctl status postgresql || echo "PostgreSQL未运行"
systemctl status redis-server || echo "Redis未运行"

# 4. 检查网络连接
echo "=== 网络连接检查 ==="
ping -c 3 8.8.8.8 || echo "网络连接失败"
curl -I https://github.com || echo "GitHub连接失败"

# 5. 检查磁盘空间
echo "=== 磁盘空间检查 ==="
df -h

# 6. 检查内存使用
echo "=== 内存使用检查 ==="
free -h

# 7. 检查进程
echo "=== 进程检查 ==="
ps aux | grep -E "(python|gunicorn|postgres|redis)" | head -10

echo "🔍 调试信息收集完成"
