#!/bin/bash

# ModeShift Django 快速本地测试脚本
# 快速验证代码质量和基本功能
# 使用方法: ./quick-local-test.sh

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

echo -e "${BLUE}🚀 开始快速本地测试...${NC}"

# 1. 安装依赖
log_info "安装依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 2. 代码格式检查
log_info "检查代码格式..."
black --check . || log_warning "Black检查失败"
isort --check-only . || log_warning "isort检查失败"

# 3. 代码质量检查
log_info "检查代码质量..."
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || log_warning "Flake8发现严重问题"

# 4. 安全扫描
log_info "安全扫描..."
bandit -r apps/ --skip B110,B311,B404,B603,B607,B112,B108 --exit-zero || log_warning "Bandit发现安全问题"

# 5. 依赖漏洞扫描
log_info "依赖漏洞扫描..."
safety check || log_warning "Safety发现依赖漏洞"

# 6. 运行测试
log_info "运行测试..."
export DJANGO_SETTINGS_MODULE=config.settings.testing
pytest tests/ -v --tb=short --maxfail=5 || log_warning "测试失败"

log_success "快速测试完成！"
