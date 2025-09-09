#!/bin/bash

# 移动端性能测试脚本
# 测试优化后的网站性能

set -e

# 服务器配置
SERVER_HOST="47.103.143.152"
DOMAIN="shenyiqing.xin"

# 颜色输出
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

# 检查依赖
check_dependencies() {
    log_info "检查测试依赖..."
    
    if ! command -v curl &> /dev/null; then
        log_error "curl 未安装，请先安装"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        log_warning "jq 未安装，某些测试可能无法进行"
    fi
    
    log_success "依赖检查完成"
}

# 基础连接测试
test_connection() {
    log_info "测试服务器连接..."
    
    if curl -f -s --connect-timeout 10 "http://$SERVER_HOST/health/" > /dev/null; then
        log_success "服务器连接正常"
        return 0
    else
        log_error "服务器连接失败"
        return 1
    fi
}

# 响应时间测试
test_response_time() {
    log_info "测试响应时间..."
    
    local url="http://$SERVER_HOST/"
    local times=()
    
    for i in {1..5}; do
        local start_time=$(date +%s.%N)
        if curl -f -s "$url" > /dev/null; then
            local end_time=$(date +%s.%N)
            local duration=$(echo "$end_time - $start_time" | bc)
            times+=($duration)
            log_info "请求 $i: ${duration}s"
        else
            log_error "请求 $i 失败"
        fi
    done
    
    # 计算平均响应时间
    local sum=0
    for time in "${times[@]}"; do
        sum=$(echo "$sum + $time" | bc)
    done
    
    local avg=$(echo "scale=3; $sum / ${#times[@]}" | bc)
    log_success "平均响应时间: ${avg}s"
    
    # 判断性能等级
    if (( $(echo "$avg < 1.0" | bc -l) )); then
        log_success "性能优秀 (< 1s)"
    elif (( $(echo "$avg < 2.0" | bc -l) )); then
        log_warning "性能良好 (1-2s)"
    else
        log_error "性能需要优化 (> 2s)"
    fi
}

# 静态资源测试
test_static_resources() {
    log_info "测试静态资源加载..."
    
    local static_files=(
        "/static/css/mobile-optimized.css"
        "/static/js/mobile-optimized.js"
        "/static/css/responsive.css"
        "/static/base.css"
    )
    
    local success_count=0
    local total_count=${#static_files[@]}
    
    for file in "${static_files[@]}"; do
        local url="http://$SERVER_HOST$file"
        if curl -f -s --head "$url" | grep -q "200 OK"; then
            log_success "✓ $file"
            ((success_count++))
        else
            log_error "✗ $file"
        fi
    done
    
    log_info "静态资源加载成功率: $success_count/$total_count"
    
    if [ $success_count -eq $total_count ]; then
        log_success "所有静态资源加载正常"
    else
        log_warning "部分静态资源加载失败"
    fi
}

# 压缩测试
test_compression() {
    log_info "测试Gzip压缩..."
    
    local url="http://$SERVER_HOST/"
    local response=$(curl -s -H "Accept-Encoding: gzip" -I "$url")
    
    if echo "$response" | grep -q "Content-Encoding: gzip"; then
        log_success "Gzip压缩已启用"
    else
        log_warning "Gzip压缩未启用或未检测到"
    fi
}

# 缓存头测试
test_cache_headers() {
    log_info "测试缓存头..."
    
    local static_url="http://$SERVER_HOST/static/css/mobile-optimized.css"
    local response=$(curl -s -I "$static_url")
    
    if echo "$response" | grep -q "Cache-Control: public, immutable"; then
        log_success "静态文件缓存头正确"
    else
        log_warning "静态文件缓存头可能有问题"
    fi
    
    if echo "$response" | grep -q "Vary: Accept-Encoding"; then
        log_success "压缩变体头正确"
    else
        log_warning "压缩变体头可能有问题"
    fi
}

# 移动端优化测试
test_mobile_optimization() {
    log_info "测试移动端优化..."
    
    local url="http://$SERVER_HOST/"
    local response=$(curl -s -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15" -I "$url")
    
    if echo "$response" | grep -q "X-Mobile-Optimized: true"; then
        log_success "移动端优化头已设置"
    else
        log_warning "移动端优化头未检测到"
    fi
}

# 安全头测试
test_security_headers() {
    log_info "测试安全头..."
    
    local url="http://$SERVER_HOST/"
    local response=$(curl -s -I "$url")
    
    local security_headers=(
        "X-Frame-Options"
        "X-Content-Type-Options"
        "X-XSS-Protection"
        "Referrer-Policy"
    )
    
    local found_headers=0
    for header in "${security_headers[@]}"; do
        if echo "$response" | grep -q "$header"; then
            log_success "✓ $header"
            ((found_headers++))
        else
            log_warning "✗ $header"
        fi
    done
    
    log_info "安全头覆盖率: $found_headers/${#security_headers[@]}"
}

# 数据库连接测试
test_database_connection() {
    log_info "测试数据库连接..."
    
    local url="http://$SERVER_HOST/admin/"
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$response" = "302" ] || [ "$response" = "200" ]; then
        log_success "数据库连接正常 (HTTP $response)"
    else
        log_warning "数据库连接可能有问题 (HTTP $response)"
    fi
}

# 生成性能报告
generate_report() {
    log_info "生成性能测试报告..."
    
    local report_file="mobile-performance-report-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$report_file" << EOF
移动端性能测试报告
==================
测试时间: $(date)
服务器: $SERVER_HOST
域名: $DOMAIN

测试结果:
EOF
    
    # 运行所有测试并记录结果
    test_connection >> "$report_file" 2>&1
    test_response_time >> "$report_file" 2>&1
    test_static_resources >> "$report_file" 2>&1
    test_compression >> "$report_file" 2>&1
    test_cache_headers >> "$report_file" 2>&1
    test_mobile_optimization >> "$report_file" 2>&1
    test_security_headers >> "$report_file" 2>&1
    test_database_connection >> "$report_file" 2>&1
    
    log_success "性能报告已生成: $report_file"
}

# 主函数
main() {
    log_info "开始移动端性能测试..."
    
    check_dependencies
    
    if test_connection; then
        test_response_time
        test_static_resources
        test_compression
        test_cache_headers
        test_mobile_optimization
        test_security_headers
        test_database_connection
        generate_report
        
        log_success "🎉 性能测试完成！"
        log_info "访问地址: http://$SERVER_HOST"
        log_info "域名: $DOMAIN"
    else
        log_error "无法连接到服务器，请检查网络和服务状态"
        exit 1
    fi
}

# 执行主函数
main "$@"
