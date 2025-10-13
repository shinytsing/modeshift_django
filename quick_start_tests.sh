#!/bin/bash

# 🚀 Django网站全维度测试体系 - 快速启动脚本
# 项目：shenyiqing.xin
# 功能：快速启动测试环境并执行测试

echo "🚀 Django网站全维度测试体系启动中..."
echo "=========================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 未安装，请先安装pip3"
    exit 1
fi

# 进入项目根目录
cd /Users/gaojie/Desktop/PycharmProjects/modeshift_django

# 安装测试依赖
echo "📦 安装测试依赖包..."
pip3 install -r tests/requirements.txt

# 检查Django项目
if [ ! -f "manage.py" ]; then
    echo "❌ 未找到Django项目，请确保在正确的项目目录中"
    exit 1
fi

# 创建必要的目录
echo "📁 创建测试目录..."
mkdir -p tests/{data,utils,functional,api,performance,security,ui,reports,artifacts/{logs,screenshots,backup}}

# 设置环境变量
export DJANGO_SETTINGS_MODULE=config.settings.development

# 运行数据库迁移
echo "🗄️ 运行数据库迁移..."
python3 manage.py migrate

# 创建测试数据
echo "📊 创建测试数据..."
python3 manage.py shell << EOF
from django.contrib.auth.models import User
User.objects.get_or_create(username='testuser', defaults={'email': 'test@example.com', 'is_active': True})
User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True})
print("测试用户创建完成")
EOF

# 启动Django开发服务器（后台运行）
echo "🌐 启动Django开发服务器..."
python3 manage.py runserver 8000 &
DJANGO_PID=$!

# 等待服务器启动
echo "⏳ 等待服务器启动..."
sleep 5

# 检查服务器是否启动成功
if ! curl -s http://localhost:8000 > /dev/null; then
    echo "❌ Django服务器启动失败"
    kill $DJANGO_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Django服务器启动成功"

# 执行测试
echo "🧪 开始执行测试..."
cd tests
bash run_tests.sh

# 停止Django服务器
echo "🛑 停止Django服务器..."
kill $DJANGO_PID 2>/dev/null || true

echo "=========================================="
echo "✅ 测试执行完成！"
echo ""
echo "📁 查看报告："
echo "   - 技术报告: tests/reports/网站全维度测试报告.md"
echo "   - 展示报告: tests/reports/网站全维度测试展示版.md"
echo "   - Allure报告: tests/reports/allure-report/index.html"
echo "   - HTML报告: tests/reports/report.html"
echo ""
echo "🎯 面试展示："
echo "   - 查看 tests/README_for_interview.md 了解面试讲解要点"
echo "   - 展示报告可直接用于简历和作品集"
echo "=========================================="
