#!/bin/bash

# 模拟GitHub Actions环境的完整CI/CD测试
# 严格按照GitHub Actions的步骤和配置

set -e

echo "🚀 开始模拟GitHub Actions CI/CD测试..."

# 设置环境变量（模拟GitHub Actions环境）
export DJANGO_SETTINGS_MODULE=config.settings.testing
export POSTGRES_HOST=localhost
export POSTGRES_DB=test_modeshift_django
export POSTGRES_USER=$(whoami)
export POSTGRES_PASSWORD=postgres
export POSTGRES_PORT=5432
export REDIS_URL=redis://localhost:6379/0

echo "📋 步骤1: 代码质量检查"
echo "运行flake8检查（宽松模式）..."
flake8 apps/ --max-line-length=88 --extend-ignore=E203,W503,F401,F841,F541,E402,E304,W291,W293,W391,F601 || {
    echo "⚠️ flake8检查有警告，但继续执行"
}

echo "运行bandit安全扫描..."
bandit -r apps/ -f json -o bandit-report.json || {
    echo "⚠️ bandit检查有警告，但继续执行"
}

echo "运行safety依赖检查..."
safety check --json --output safety-report.json || {
    echo "⚠️ safety检查有警告，但继续执行"
}

echo "✅ 代码质量检查完成（宽松模式）"

echo "📋 步骤2: 启动PostgreSQL和Redis服务"
echo "启动PostgreSQL..."
brew services start postgresql@15 || {
    echo "❌ PostgreSQL启动失败"
    exit 1
}

echo "启动Redis..."
brew services start redis || {
    echo "❌ Redis启动失败"
    exit 1
}

echo "等待服务启动..."
sleep 10

echo "📋 步骤3: 检查服务状态"
echo "检查PostgreSQL状态..."
pg_isready -h localhost -p 5432 -U $(whoami) || {
    echo "❌ PostgreSQL未就绪"
    exit 1
}

echo "检查Redis状态..."
redis-cli -h localhost -p 6379 ping || {
    echo "❌ Redis未就绪"
    exit 1
}

echo "✅ 服务状态检查通过"

echo "📋 步骤4: 检查数据库连接"
echo "检查PostgreSQL连接..."
python -c "
import psycopg
try:
    conn = psycopg.connect(
        host='localhost',
        dbname='test_modeshift_django',
        user='$(whoami)',
        password='',
        port=5432
    )
    print('数据库连接成功')
    conn.close()
except Exception as e:
    print(f'数据库连接失败: {e}')
    exit(1)
" || {
    echo "❌ 数据库连接失败"
    exit 1
}

echo "✅ 数据库连接检查通过"

echo "📋 步骤5: 运行数据库迁移"
echo "运行数据库迁移..."
python manage.py migrate --settings=config.settings.testing --verbosity=2 || {
    echo "❌ 数据库迁移失败"
    exit 1
}

echo "✅ 数据库迁移完成"

echo "📋 步骤6: 运行单元测试"
echo "运行单元测试..."
pytest tests/ \
  --cov=apps \
  --cov-report=xml \
  --cov-report=html \
  --cov-report=term \
  --junit-xml=test-results.xml \
  --html=test-report.html \
  --self-contained-html \
  -v \
  --maxfail=10 \
  --tb=short \
  --durations=10 || {
    echo "❌ 单元测试失败"
    exit 1
}

echo "✅ 单元测试通过"

echo "🎉 模拟GitHub Actions CI/CD测试完成！"
echo "📊 测试报告: test-report.html"
echo "📈 覆盖率报告: htmlcov/index.html"
echo "🔒 安全报告: bandit-report.json, safety-report.json"
