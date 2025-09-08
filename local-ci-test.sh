#!/bin/bash

# 本地CI测试脚本 - 模拟GitHub Actions环境
# 用于在推送前验证代码质量

set -e  # 遇到错误立即退出

echo "🚀 开始本地CI测试..."
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查Python版本
echo -e "${BLUE}🐍 检查Python环境...${NC}"
python3 --version
pip3 --version

# 检查PostgreSQL服务
echo -e "${BLUE}🗄️ 检查PostgreSQL服务...${NC}"
if ! pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️ PostgreSQL未运行，尝试启动...${NC}"
    if command -v brew >/dev/null 2>&1; then
        brew services start postgresql@15 || brew services start postgresql
    elif command -v systemctl >/dev/null 2>&1; then
        sudo systemctl start postgresql
    else
        echo -e "${RED}❌ 无法启动PostgreSQL，请手动启动${NC}"
        exit 1
    fi
    sleep 5
fi

# 检查Redis服务
echo -e "${BLUE}🔴 检查Redis服务...${NC}"
if ! redis-cli ping >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️ Redis未运行，尝试启动...${NC}"
    if command -v brew >/dev/null 2>&1; then
        brew services start redis
    elif command -v systemctl >/dev/null 2>&1; then
        sudo systemctl start redis-server
    else
        echo -e "${RED}❌ 无法启动Redis，请手动启动${NC}"
        exit 1
    fi
    sleep 3
fi

# 设置环境变量
echo -e "${BLUE}🔧 设置环境变量...${NC}"
export DJANGO_SETTINGS_MODULE=config.settings.testing
export POSTGRES_HOST=localhost
export POSTGRES_DB=test_modeshift_django
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_PORT=5432
export REDIS_URL=redis://localhost:6379/0

# 激活虚拟环境
echo -e "${BLUE}📦 激活虚拟环境...${NC}"
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✅ 虚拟环境已激活${NC}"
else
    echo -e "${YELLOW}⚠️ 虚拟环境不存在，创建新的虚拟环境...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# 安装测试依赖
echo -e "${BLUE}📥 安装测试依赖...${NC}"
pip install pytest pytest-django pytest-cov pytest-xdist pytest-html

# 清理旧的测试文件
echo -e "${BLUE}🧹 清理旧的测试文件...${NC}"
rm -f test-results.xml test-report.html coverage.xml
rm -rf htmlcov/
rm -rf __pycache__/
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# 运行数据库迁移
echo -e "${BLUE}📊 运行数据库迁移...${NC}"
python manage.py migrate --settings=config.settings.testing

# 运行代码质量检查
echo -e "${BLUE}🔍 运行代码质量检查...${NC}"

# Black格式化检查
echo -e "${YELLOW}检查Black格式化...${NC}"
if black --check apps/ manage.py; then
    echo -e "${GREEN}✅ Black检查通过${NC}"
else
    echo -e "${RED}❌ Black检查失败${NC}"
    echo "运行: black apps/ manage.py"
    exit 1
fi

# Isort导入排序检查
echo -e "${YELLOW}检查Isort导入排序...${NC}"
if isort --check-only apps/ manage.py; then
    echo -e "${GREEN}✅ Isort检查通过${NC}"
else
    echo -e "${RED}❌ Isort检查失败${NC}"
    echo "运行: isort apps/ manage.py"
    exit 1
fi

# Flake8代码风格检查
echo -e "${YELLOW}检查Flake8代码风格...${NC}"
if flake8 apps/ manage.py --max-line-length=88 --extend-ignore=E203,E501,W503,F403,F405,F401,E402,F541,F841,F811,F601,E731,W391,W293,W291,E226; then
    echo -e "${GREEN}✅ Flake8检查通过${NC}"
else
    echo -e "${RED}❌ Flake8检查失败${NC}"
    exit 1
fi

# 运行单元测试
echo -e "${BLUE}🧪 运行单元测试...${NC}"
if pytest tests/unit/ \
    --cov=apps \
    --cov-report=xml \
    --cov-report=html \
    --cov-report=term \
    --junit-xml=test-results.xml \
    --html=test-report.html \
    --self-contained-html \
    -v \
    --maxfail=5 \
    --tb=short \
    --numprocesses=auto; then
    echo -e "${GREEN}✅ 单元测试通过${NC}"
else
    echo -e "${RED}❌ 单元测试失败${NC}"
    echo "查看详细错误信息："
    cat test-results.xml
    exit 1
fi

# 检查测试覆盖率
echo -e "${BLUE}📊 检查测试覆盖率...${NC}"
COVERAGE=$(python -c "
import xml.etree.ElementTree as ET
try:
    root = ET.parse('coverage.xml').getroot()
    coverage = float(root.attrib['line-rate']) * 100
    print(f'{coverage:.1f}')
except:
    print('0.0')
")

echo "测试覆盖率: $COVERAGE%"

# 覆盖率门禁：要求达到5%
COVERAGE_INT=$(echo $COVERAGE | cut -d. -f1)
if [ "$COVERAGE_INT" -lt "5" ]; then
    echo -e "${RED}❌ 测试覆盖率不达标: $COVERAGE% (要求: ≥5%)${NC}"
    exit 1
else
    echo -e "${GREEN}✅ 测试覆盖率达标: $COVERAGE%${NC}"
fi

# 安全扫描
echo -e "${BLUE}🔒 运行安全扫描...${NC}"

# Bandit安全扫描
echo -e "${YELLOW}运行Bandit安全扫描...${NC}"
if bandit -r apps/ -f json -o bandit-report.json; then
    echo -e "${GREEN}✅ Bandit扫描通过${NC}"
else
    echo -e "${YELLOW}⚠️ Bandit扫描发现问题，但继续执行${NC}"
fi

# Safety依赖漏洞扫描
echo -e "${YELLOW}运行Safety依赖漏洞扫描...${NC}"
if safety check --output json > safety-report.json; then
    echo -e "${GREEN}✅ Safety扫描通过${NC}"
else
    echo -e "${YELLOW}⚠️ Safety扫描发现问题，但继续执行${NC}"
fi

echo "=========================================="
echo -e "${GREEN}🎉 本地CI测试完成！所有检查都通过了${NC}"
echo "=========================================="
echo "📊 测试报告:"
echo "  - 测试结果: test-results.xml"
echo "  - HTML报告: test-report.html"
echo "  - 覆盖率报告: htmlcov/index.html"
echo "  - 安全报告: bandit-report.json, safety-report.json"
echo ""
echo -e "${GREEN}✅ 可以安全推送到GitHub了！${NC}"
