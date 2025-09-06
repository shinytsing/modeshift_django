#!/bin/bash

# QAToolBox 生产级本地CI/CD脚本
# 模拟GitHub Actions的完整流程，确保代码质量

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 清理函数
cleanup() {
    log_info "清理临时文件..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -name ".coverage" -delete 2>/dev/null || true
    find . -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
    find . -name "coverage.xml" -delete 2>/dev/null || true
    find . -name "test-results.xml" -delete 2>/dev/null || true
    find . -name "test-report.html" -delete 2>/dev/null || true
    find . -name "mypy-report.xml" -delete 2>/dev/null || true
    find . -name "bandit-report.json" -delete 2>/dev/null || true
}

# 1. 环境检查
check_environment() {
    log_info "=== 1. 环境检查 ==="
    
    # 检查Python版本
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    log_info "Python版本: $PYTHON_VERSION"
    
    # 检查虚拟环境
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        log_success "虚拟环境已激活: $VIRTUAL_ENV"
    else
        log_warning "建议在虚拟环境中运行此脚本"
    fi
    
    # 检查PostgreSQL连接
    log_info "检查PostgreSQL连接..."
    if python -c "
import os
import psycopg2
try:
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=os.environ.get('DB_PORT', '5432'),
        user=os.environ.get('DB_USER', 'gaojie'),
        password=os.environ.get('DB_PASSWORD', ''),
        database=os.environ.get('DB_NAME', 'modeshift_django')
    )
    conn.close()
    print('PostgreSQL连接成功')
except Exception as e:
    print(f'PostgreSQL连接失败: {e}')
    exit(1)
"; then
        log_success "PostgreSQL连接正常"
    else
        log_error "PostgreSQL连接失败"
        return 1
    fi
    
    log_success "环境检查完成"
}

# 2. 代码质量检查
code_quality_check() {
    log_info "=== 2. 代码质量检查 ==="
    
    # 安装代码质量工具
    log_info "安装代码质量工具..."
    pip install flake8==6.1.0 black==25.1.0 isort==5.13.2 mypy==1.8.0 bandit==1.7.5 safety==2.3.5
    
    # Black代码格式化检查
    log_info "Black代码格式检查..."
    if black --check --diff .; then
        log_success "Black格式检查通过"
    else
        log_error "Black格式检查失败"
        log_info "运行 'black .' 来修复格式问题"
        return 1
    fi
    
    # isort导入排序检查
    log_info "isort导入排序检查..."
    if isort --check-only --diff .; then
        log_success "isort导入排序检查通过"
    else
        log_error "isort导入排序检查失败"
        log_info "运行 'isort .' 来修复导入排序问题"
        return 1
    fi
    
    # Flake8代码检查
    log_info "Flake8代码检查..."
    if flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics; then
        log_success "Flake8关键错误检查通过"
    else
        log_error "Flake8发现关键错误"
        return 1
    fi
    
    # MyPy类型检查
    log_info "MyPy类型检查..."
    if mypy . --ignore-missing-imports --no-error-summary; then
        log_success "MyPy类型检查通过"
    else
        log_warning "MyPy类型检查有警告，但继续执行"
    fi
    
    # Bandit安全扫描
    log_info "Bandit安全扫描..."
    if bandit -r . -f json -o bandit-report.json; then
        log_success "Bandit安全扫描通过"
    else
        log_warning "Bandit发现安全问题，但继续执行"
    fi
    
    # Safety依赖安全检查
    log_info "Safety依赖安全检查..."
    if safety check --json --output safety-report.json; then
        log_success "Safety依赖安全检查通过"
    else
        log_warning "Safety发现依赖安全问题，但继续执行"
    fi
    
    log_success "代码质量检查完成"
}

# 3. 单元测试
unit_tests() {
    log_info "=== 3. 单元测试 ==="
    
    # 安装测试依赖
    log_info "安装测试依赖..."
    pip install pytest pytest-django pytest-cov coverage==7.4.0
    
    # 设置测试环境变量
    export DJANGO_SETTINGS_MODULE=config.settings.testing
    
    # 运行单元测试
    log_info "运行单元测试..."
    if pytest tests/unit/ \
        --cov=apps \
        --cov-report=xml \
        --cov-report=term \
        --junit-xml=test-results.xml \
        -v \
        --maxfail=10 \
        --tb=short; then
        log_success "单元测试通过"
    else
        log_error "单元测试失败"
        return 1
    fi
    
    # 检查测试覆盖率
    COVERAGE=$(python3 -c "
import xml.etree.ElementTree as ET
try:
    root = ET.parse('coverage.xml').getroot()
    coverage = float(root.attrib['line-rate']) * 100
    print(f'{coverage:.1f}')
except:
    print('0.0')
")
    
    log_info "测试覆盖率: $COVERAGE%"
    
    # 覆盖率门禁：要求达到10%
    COVERAGE_INT=$(echo $COVERAGE | cut -d. -f1)
    if [ "$COVERAGE_INT" -lt "10" ]; then
        log_error "测试覆盖率不达标: $COVERAGE% (要求: ≥10%)"
        return 1
    else
        log_success "测试覆盖率达标: $COVERAGE%"
    fi
    
    log_success "单元测试完成"
}

# 4. Django配置检查
django_check() {
    log_info "=== 4. Django配置检查 ==="
    
    # 检查Django配置
    log_info "检查Django配置..."
    if python manage.py check; then
        log_success "Django配置检查通过"
    else
        log_error "Django配置检查失败"
        return 1
    fi
    
    # 检查数据库迁移
    log_info "检查数据库迁移..."
    if python manage.py showmigrations --plan | grep -q "\[ \]"; then
        log_warning "有未应用的迁移，但继续执行"
    else
        log_success "所有迁移已应用"
    fi
    
    # 检查静态文件
    log_info "收集静态文件..."
    if python manage.py collectstatic --noinput; then
        log_success "静态文件收集成功"
    else
        log_warning "静态文件收集失败，但继续执行"
    fi
    
    log_success "Django配置检查完成"
}

# 5. 部署前检查
pre_deployment_check() {
    log_info "=== 5. 部署前检查 ==="
    
    # 检查Git状态
    if git status --porcelain | grep -q .; then
        log_warning "工作目录有未提交的更改"
        git status --short
    else
        log_success "工作目录干净"
    fi
    
    # 检查分支
    CURRENT_BRANCH=$(git branch --show-current)
    log_info "当前分支: $CURRENT_BRANCH"
    
    # 检查环境变量
    log_info "检查关键环境变量..."
    if [ -z "$DJANGO_SECRET_KEY" ]; then
        log_warning "DJANGO_SECRET_KEY未设置"
    else
        log_success "DJANGO_SECRET_KEY已设置"
    fi
    
    log_success "部署前检查完成"
}

# 主函数
main() {
    log_info "🚀 开始QAToolBox生产级CI/CD流程"
    log_info "时间: $(date)"
    
    # 清理环境
    cleanup
    
    # 执行各个阶段
    check_environment || exit 1
    code_quality_check || exit 1
    unit_tests || exit 1
    django_check || exit 1
    pre_deployment_check || exit 1
    
    log_success "🎉 生产级CI/CD流程全部通过！"
    log_info "代码已准备好推送到GitHub进行部署"
    
    # 显示下一步操作
    echo ""
    log_info "下一步操作："
    echo "1. git add ."
    echo "2. git commit -m '通过生产级CI/CD检查'"
    echo "3. git push origin main"
    echo ""
    log_info "这将触发GitHub Actions进行自动部署"
}

# 错误处理
trap 'log_error "CI/CD流程在 $LINENO 行失败"; exit 1' ERR

# 运行主函数
main "$@"
