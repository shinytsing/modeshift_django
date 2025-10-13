#!/bin/bash

# 🚀 Django网站全维度测试一键执行脚本
# 功能：安装依赖、执行测试、生成报告、打开结果
# 作者：高杰
# 日期：2025-10-08

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo ""
    print_message $PURPLE "=========================================="
    print_message $PURPLE "🚀 Django网站全维度测试系统"
    print_message $PURPLE "=========================================="
    echo ""
}

print_step() {
    local step=$1
    local message=$2
    print_message $BLUE "[步骤 $step] $message"
}

print_success() {
    print_message $GREEN "✅ $1"
}

print_warning() {
    print_message $YELLOW "⚠️  $1"
}

print_error() {
    print_message $RED "❌ $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "命令 $1 未找到，请先安装"
        return 1
    fi
    return 0
}

# 检查Python环境
check_python_env() {
    print_step "1" "检查Python环境"
    
    if ! check_command python3; then
        print_error "Python3 未安装"
        exit 1
    fi
    
    python_version=$(python3 --version 2>&1)
    print_success "Python版本: $python_version"
}

# 安装Python依赖
install_python_deps() {
    print_step "2" "安装Python测试依赖"
    
    print_message $CYAN "正在安装测试框架和工具..."
    
    # 核心测试依赖
    pip3 install -U pytest pytest-django pytest-mock pytest-html pytest-cov allure-pytest requests selenium playwright requests-mock
    
    if [ $? -eq 0 ]; then
        print_success "Python依赖安装完成"
    else
        print_error "Python依赖安装失败"
        exit 1
    fi
}

# 安装Allure
install_allure() {
    print_step "3" "安装Allure报告工具"
    
    if check_command allure; then
        print_success "Allure已安装"
        return 0
    fi
    
    print_message $CYAN "正在安装Allure..."
    
    # 检查操作系统
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if check_command brew; then
            brew install allure
        else
            print_warning "请手动安装Homebrew后运行: brew install allure"
            print_message $YELLOW "或者访问: https://docs.qameta.io/allure/#_installing_a_commandline"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        print_message $YELLOW "Linux系统请手动安装Allure"
        print_message $YELLOW "参考: https://docs.qameta.io/allure/#_installing_a_commandline"
    else
        print_warning "未知操作系统，请手动安装Allure"
    fi
}

# 清理旧测试结果
cleanup_old_results() {
    print_step "4" "清理旧测试结果"
    
    print_message $CYAN "清理旧的测试结果和报告..."
    
    # 清理目录
    rm -rf tests/allure-results
    rm -rf tests/reports/allure-report
    rm -rf tests/reports/screenshots
    rm -rf .pytest_cache
    
    # 创建必要目录
    mkdir -p tests/allure-results
    mkdir -p tests/reports/allure-report
    mkdir -p tests/reports/screenshots
    
    print_success "旧结果清理完成"
}

# 设置Django环境
setup_django_env() {
    print_step "5" "设置Django测试环境"
    
    # 设置Django设置模块
    export DJANGO_SETTINGS_MODULE=config.settings.development
    
    print_success "Django环境设置完成"
}

# 执行测试
run_tests() {
    print_step "6" "执行全维度测试"
    
    print_message $CYAN "开始执行pytest测试..."
    print_message $YELLOW "测试模块: 功能、接口、性能、安全、UI自动化"
    
    # 执行pytest测试
    python3 -m pytest tests/ \
        --alluredir=tests/allure-results \
        --cov=. \
        --cov-report=xml:tests/reports/coverage.xml \
        --html=tests/reports/pytest_report.html \
        --self-contained-html \
        -v \
        --tb=short \
        --disable-warnings \
        --maxfail=10
    
    test_exit_code=$?
    
    if [ $test_exit_code -eq 0 ]; then
        print_success "所有测试执行完成"
    else
        print_warning "部分测试失败，退出码: $test_exit_code"
    fi
}

# 生成Allure报告
generate_allure_report() {
    print_step "7" "生成Allure HTML报告"
    
    if ! check_command allure; then
        print_warning "Allure未安装，跳过HTML报告生成"
        return 0
    fi
    
    print_message $CYAN "正在生成Allure HTML报告..."
    
    allure generate tests/allure-results -o tests/reports/allure-report --clean
    
    if [ $? -eq 0 ]; then
        print_success "Allure HTML报告生成完成"
    else
        print_error "Allure报告生成失败"
    fi
}

# 生成测试统计
generate_test_stats() {
    print_step "8" "生成测试统计信息"
    
    print_message $CYAN "分析测试结果..."
    
    # 统计测试结果
    total_tests=$(find tests/allure-results -name "*-result.json" 2>/dev/null | wc -l || echo "0")
    passed_tests=$(find tests/allure-results -name "*-result.json" -exec grep -l '"status":"passed"' {} \; 2>/dev/null | wc -l || echo "0")
    failed_tests=$(find tests/allure-results -name "*-result.json" -exec grep -l '"status":"failed"' {} \; 2>/dev/null | wc -l || echo "0")
    
    print_message $GREEN "📊 测试统计:"
    print_message $GREEN "   总测试数: $total_tests"
    print_message $GREEN "   通过数: $passed_tests"
    print_message $GREEN "   失败数: $failed_tests"
    
    if [ $total_tests -gt 0 ]; then
        pass_rate=$((passed_tests * 100 / total_tests))
        print_message $GREEN "   通过率: ${pass_rate}%"
    fi
}

# 打开报告
open_reports() {
    print_step "9" "打开测试报告"
    
    # 检查报告文件是否存在
    if [ -f "tests/reports/allure-report/index.html" ]; then
        print_message $CYAN "正在打开Allure HTML报告..."
        
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            open tests/reports/allure-report/index.html
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            xdg-open tests/reports/allure-report/index.html 2>/dev/null || echo "请手动打开: tests/reports/allure-report/index.html"
        else
            print_message $YELLOW "请手动打开: tests/reports/allure-report/index.html"
        fi
        
        print_success "Allure报告已打开"
    else
        print_warning "Allure报告文件不存在"
    fi
    
    # 检查Markdown报告
    if [ -f "tests/reports/网站全维度测试报告.md" ]; then
        print_success "Markdown报告已生成: tests/reports/网站全维度测试报告.md"
    fi
}

# 显示最终结果
show_final_results() {
    print_header
    print_message $GREEN "🎉 Django网站全维度测试完成！"
    echo ""
    print_message $CYAN "📁 报告文件位置:"
    print_message $CYAN "   Allure HTML报告: tests/reports/allure-report/index.html"
    print_message $CYAN "   Markdown报告: tests/reports/网站全维度测试报告.md"
    print_message $CYAN "   测试截图: tests/reports/screenshots/"
    print_message $CYAN "   覆盖率报告: tests/reports/coverage.xml"
    print_message $CYAN "   Pytest报告: tests/reports/pytest_report.html"
    echo ""
    print_message $YELLOW "💡 提示:"
    print_message $YELLOW "   - 查看Allure报告了解详细测试结果"
    print_message $YELLOW "   - 查看Markdown报告了解测试总结"
    print_message $YELLOW "   - 查看截图了解UI测试结果"
    echo ""
}

# 主函数
main() {
    print_header
    
    # 记录开始时间
    start_time=$(date +%s)
    
    # 执行各个步骤
    check_python_env
    install_python_deps
    install_allure
    cleanup_old_results
    setup_django_env
    run_tests
    generate_allure_report
    generate_test_stats
    open_reports
    
    # 记录结束时间
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    show_final_results
    
    print_message $GREEN "⏱️  总执行时间: ${duration}秒"
    print_message $GREEN "✅ 测试执行完成！"
}

# 错误处理
trap 'print_error "脚本执行过程中发生错误，退出码: $?"' ERR

# 执行主函数
main "$@"