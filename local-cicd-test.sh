#!/bin/bash

# 本地CI/CD测试脚本
# 模拟GitHub Actions环境进行完整测试

set -e

echo "🚀 开始本地CI/CD测试..."

# 1. 代码质量检查
echo "📋 步骤1: 代码质量检查"
echo "运行flake8检查..."
flake8 apps/ --max-line-length=88 --extend-ignore=E203,W503
echo "运行black检查..."
black --check apps/
echo "运行isort检查..."
isort --check-only apps/
echo "运行mypy检查..."
mypy apps/ --ignore-missing-imports
echo "运行bandit安全扫描..."
bandit -r apps/ -f json -o bandit-report.json
echo "运行safety依赖检查..."
safety check --json --output safety-report.json
echo "✅ 代码质量检查通过"

# 2. 启动测试环境
echo "📋 步骤2: 启动测试环境"
echo "停止现有容器..."
docker-compose -f docker-compose.test.yml down
echo "构建并启动测试环境..."
docker-compose -f docker-compose.test.yml up --build -d postgres redis
echo "等待服务启动..."
sleep 20

# 3. 检查服务状态
echo "📋 步骤3: 检查服务状态"
echo "检查PostgreSQL状态..."
docker-compose -f docker-compose.test.yml exec -T postgres pg_isready -U postgres
echo "检查Redis状态..."
docker-compose -f docker-compose.test.yml exec -T redis redis-cli ping
echo "✅ 服务状态检查通过"

# 4. 运行应用测试
echo "📋 步骤4: 运行应用测试"
echo "启动应用容器并运行测试..."
docker-compose -f docker-compose.test.yml up --build app

# 5. 检查测试结果
echo "📋 步骤5: 检查测试结果"
if [ -f "test-results.xml" ]; then
    echo "✅ 测试结果文件生成成功"
    echo "测试报告: test-report.html"
    echo "覆盖率报告: htmlcov/index.html"
else
    echo "❌ 测试结果文件未生成"
    exit 1
fi

echo "🎉 本地CI/CD测试完成！"
echo "📊 测试报告: test-report.html"
echo "📈 覆盖率报告: htmlcov/index.html"
echo "🔒 安全报告: bandit-report.json, safety-report.json"
