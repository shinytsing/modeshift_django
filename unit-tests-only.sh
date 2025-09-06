#!/bin/bash

# ModeShift Django 单元测试专用脚本
# 跳过E2E测试，只运行单元测试
# 使用方法: ./unit-tests-only.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查虚拟环境
if [[ "$VIRTUAL_ENV" == "" ]]; then
    log_warning "未激活虚拟环境，尝试激活..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        log_success "虚拟环境已激活"
    else
        log_error "未找到虚拟环境，请先创建: python3 -m venv venv"
        exit 1
    fi
fi

echo -e "${BLUE}🧪 开始单元测试...${NC}"

# 设置测试环境变量
export DJANGO_SETTINGS_MODULE=config.settings.testing

# 运行单元测试（跳过E2E测试）
log_info "运行单元测试（跳过E2E测试）..."
pytest tests/ \
    --ignore=tests/e2e/ \
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
    --durations=10

# 提取覆盖率
COVERAGE=$(python -c "
import xml.etree.ElementTree as ET
try:
    root = ET.parse('coverage.xml').getroot()
    coverage = float(root.attrib['line-rate']) * 100
    print(f'{coverage:.1f}')
except:
    print('0.0')
")

log_info "测试覆盖率: $COVERAGE%"

# 覆盖率门禁
COVERAGE_INT=$(echo $COVERAGE | cut -d. -f1)
if [ "$COVERAGE_INT" -lt "5" ]; then
    log_error "测试覆盖率不达标: $COVERAGE% (要求: ≥5%)"
    exit 1
else
    log_success "测试覆盖率达标: $COVERAGE%"
fi

log_success "单元测试完成！"
echo -e "${BLUE}📊 测试报告: test-report.html${NC}"
echo -e "${BLUE}📈 覆盖率报告: htmlcov/index.html${NC}"
