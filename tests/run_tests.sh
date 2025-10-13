#!/bin/bash

# 测试运行脚本
# 用于运行不同类型的测试

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TESTS_DIR="$PROJECT_ROOT/tests"
REPORTS_DIR="$TESTS_DIR/reports"

# 创建报告目录
mkdir -p "$REPORTS_DIR"

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

# 检查依赖
check_dependencies() {
    log_info "Checking dependencies..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 is not installed"
        exit 1
    fi
    
    # 检查pytest
    if ! python3 -c "import pytest" &> /dev/null; then
        log_error "pytest is not installed. Please install it with: pip install pytest"
        exit 1
    fi
    
    # 检查Django服务器是否运行
    if ! curl -s http://localhost:8000/health/ > /dev/null; then
        log_warning "Django server is not running. Please start it with: python manage.py runserver"
        log_info "You can start the server in another terminal and then run tests"
    fi
    
    log_success "Dependencies check completed"
}

# 运行所有测试
run_all_tests() {
    log_info "Running all tests..."
    
    python3 -m pytest "$TESTS_DIR" \
        --verbose \
        --tb=short \
        --html="$REPORTS_DIR/html-report.html" \
        --self-contained-html \
        --cov=apps \
        --cov-report=html:"$REPORTS_DIR/coverage" \
        --cov-report=xml:"$REPORTS_DIR/coverage.xml" \
        --junitxml="$REPORTS_DIR/junit.xml" \
        --durations=10
    
    log_success "All tests completed"
}

# 运行UI测试
run_ui_tests() {
    log_info "Running UI tests..."
    
    python3 -m pytest "$TESTS_DIR/ui" \
        -m ui \
        --verbose \
        --tb=short \
        --html="$REPORTS_DIR/ui-report.html" \
        --self-contained-html
    
    log_success "UI tests completed"
}

# 运行WebSocket测试
run_websocket_tests() {
    log_info "Running WebSocket tests..."
    
    python3 -m pytest "$TESTS_DIR/websocket" \
        -m websocket \
        --verbose \
        --tb=short \
        --html="$REPORTS_DIR/websocket-report.html" \
        --self-contained-html
    
    log_success "WebSocket tests completed"
}

# 运行性能测试
run_performance_tests() {
    log_info "Running performance tests..."
    
    python3 -m pytest "$TESTS_DIR/performance" \
        -m performance \
        --verbose \
        --tb=short \
        --html="$REPORTS_DIR/performance-report.html" \
        --self-contained-html \
        --durations=0
    
    log_success "Performance tests completed"
}

# 运行冒烟测试
run_smoke_tests() {
    log_info "Running smoke tests..."
    
    python3 -m pytest "$TESTS_DIR" \
        -m smoke \
        --verbose \
        --tb=short \
        --html="$REPORTS_DIR/smoke-report.html" \
        --self-contained-html
    
    log_success "Smoke tests completed"
}

# 运行集成测试
run_integration_tests() {
    log_info "Running integration tests..."
    
    python3 -m pytest "$TESTS_DIR" \
        -m integration \
        --verbose \
        --tb=short \
        --html="$REPORTS_DIR/integration-report.html" \
        --self-contained-html
    
    log_success "Integration tests completed"
}

# 运行特定测试
run_specific_test() {
    local test_path="$1"
    log_info "Running specific test: $test_path"
    
    python3 -m pytest "$test_path" \
        --verbose \
        --tb=short \
        --html="$REPORTS_DIR/specific-test-report.html" \
        --self-contained-html
    
    log_success "Specific test completed"
}

# 运行带标记的测试
run_tests_with_markers() {
    local markers="$1"
    log_info "Running tests with markers: $markers"
    
    python3 -m pytest "$TESTS_DIR" \
        -m "$markers" \
        --verbose \
        --tb=short \
        --html="$REPORTS_DIR/${markers}-report.html" \
        --self-contained-html
    
    log_success "Tests with markers completed"
}

# 生成测试报告
generate_reports() {
    log_info "Generating test reports..."
    
    # 生成总结报告
    python3 "$TESTS_DIR/run_tests.py" --summary
    
    log_success "Test reports generated in $REPORTS_DIR"
}

# 清理测试数据
cleanup() {
    log_info "Cleaning up test data..."
    
    # 清理临时文件
    find "$TESTS_DIR" -name "*.pyc" -delete
    find "$TESTS_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    log_success "Cleanup completed"
}

# 显示帮助信息
show_help() {
    echo "Usage: $0 [OPTIONS] [TEST_TYPE]"
    echo ""
    echo "Test Types:"
    echo "  all          Run all tests (default)"
    echo "  ui           Run UI tests only"
    echo "  websocket    Run WebSocket tests only"
    echo "  performance  Run performance tests only"
    echo "  smoke        Run smoke tests only"
    echo "  integration  Run integration tests only"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -c, --check    Check dependencies only"
    echo "  -r, --reports  Generate test reports"
    echo "  -l, --cleanup  Clean up test data"
    echo "  -t, --test     Run specific test file"
    echo "  -m, --markers  Run tests with specific markers"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all tests"
    echo "  $0 ui                 # Run UI tests only"
    echo "  $0 -t tests/ui/test_basic_ui.py  # Run specific test"
    echo "  $0 -m 'ui and not slow'          # Run UI tests excluding slow ones"
    echo "  $0 -r                 # Generate reports"
}

# 主函数
main() {
    local test_type="all"
    local check_only=false
    local generate_reports_flag=false
    local cleanup_flag=false
    local specific_test=""
    local markers=""
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -c|--check)
                check_only=true
                shift
                ;;
            -r|--reports)
                generate_reports_flag=true
                shift
                ;;
            -l|--cleanup)
                cleanup_flag=true
                shift
                ;;
            -t|--test)
                specific_test="$2"
                shift 2
                ;;
            -m|--markers)
                markers="$2"
                shift 2
                ;;
            all|ui|websocket|performance|smoke|integration)
                test_type="$1"
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 检查依赖
    check_dependencies
    
    if [[ "$check_only" == true ]]; then
        exit 0
    fi
    
    # 清理
    if [[ "$cleanup_flag" == true ]]; then
        cleanup
    fi
    
    # 运行测试
    cd "$PROJECT_ROOT"
    
    if [[ -n "$specific_test" ]]; then
        run_specific_test "$specific_test"
    elif [[ -n "$markers" ]]; then
        run_tests_with_markers "$markers"
    else
        case "$test_type" in
            ui)
                run_ui_tests
                ;;
            websocket)
                run_websocket_tests
                ;;
            performance)
                run_performance_tests
                ;;
            smoke)
                run_smoke_tests
                ;;
            integration)
                run_integration_tests
                ;;
            all)
                run_all_tests
                ;;
            *)
                log_error "Unknown test type: $test_type"
                show_help
                exit 1
                ;;
        esac
    fi
    
    # 生成报告
    if [[ "$generate_reports_flag" == true ]]; then
        generate_reports
    fi
    
    log_success "Test run completed successfully!"
}

# 运行主函数
main "$@"