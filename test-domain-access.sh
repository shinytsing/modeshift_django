#!/bin/bash

# 🌐 域名访问测试脚本

set -e

# 服务器信息
HOST="47.103.143.152"
DOMAIN="shenyiqing.xin"

# 颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${BLUE}🌐${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 测试DNS解析
test_dns() {
    log "测试DNS解析..."
    
    local ip=$(nslookup $DOMAIN | grep "Address:" | tail -1 | awk '{print $2}')
    
    if [ "$ip" = "$HOST" ]; then
        success "DNS解析正确: $DOMAIN -> $ip"
    else
        error "DNS解析错误: $DOMAIN -> $ip (期望: $HOST)"
        return 1
    fi
}

# 测试HTTP访问
test_http_access() {
    log "测试HTTP访问..."
    
    # 测试IP访问
    local ip_status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "http://$HOST/")
    if [ "$ip_status" = "200" ]; then
        success "IP访问正常: http://$HOST/ (状态码: $ip_status)"
    else
        error "IP访问失败: http://$HOST/ (状态码: $ip_status)"
        return 1
    fi
    
    # 测试域名访问
    local domain_status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "http://$DOMAIN/")
    if [ "$domain_status" = "200" ]; then
        success "域名访问正常: http://$DOMAIN/ (状态码: $domain_status)"
    else
        error "域名访问失败: http://$DOMAIN/ (状态码: $domain_status)"
        return 1
    fi
}

# 测试页面内容
test_page_content() {
    log "测试页面内容..."
    
    # 测试IP页面内容
    local ip_content=$(curl -s --max-time 10 "http://$HOST/" | grep -i "title" | head -1)
    if [[ "$ip_content" == *"ModeShift"* ]]; then
        success "IP页面内容正常: $ip_content"
    else
        warning "IP页面内容异常: $ip_content"
    fi
    
    # 测试域名页面内容
    local domain_content=$(curl -s --max-time 10 "http://$DOMAIN/" | grep -i "title" | head -1)
    if [[ "$domain_content" == *"ModeShift"* ]]; then
        success "域名页面内容正常: $domain_content"
    else
        warning "域名页面内容异常: $domain_content"
    fi
}

# 测试响应头
test_response_headers() {
    log "测试响应头..."
    
    # 测试IP响应头
    local ip_headers=$(curl -I -s --max-time 10 "http://$HOST/" | head -5)
    echo "IP响应头:"
    echo "$ip_headers"
    echo ""
    
    # 测试域名响应头
    local domain_headers=$(curl -I -s --max-time 10 "http://$DOMAIN/" | head -5)
    echo "域名响应头:"
    echo "$domain_headers"
    echo ""
}

# 测试不同路径
test_different_paths() {
    log "测试不同路径..."
    
    local paths=("/" "/admin/" "/health/")
    
    for path in "${paths[@]}"; do
        local ip_status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "http://$HOST$path")
        local domain_status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "http://$DOMAIN$path")
        
        if [ "$ip_status" = "$domain_status" ]; then
            success "路径 $path 访问一致: IP($ip_status) = 域名($domain_status)"
        else
            warning "路径 $path 访问不一致: IP($ip_status) ≠ 域名($domain_status)"
        fi
    done
}

# 生成访问报告
generate_access_report() {
    log "生成访问报告..."
    
    local report_file="domain-access-report.txt"
    
    cat > "$report_file" << EOF
# 域名访问测试报告
生成时间: $(date)
测试域名: $DOMAIN
服务器IP: $HOST

## DNS解析测试
$(nslookup $DOMAIN)

## HTTP访问测试
### IP访问
$(curl -I -s --max-time 10 "http://$HOST/")

### 域名访问
$(curl -I -s --max-time 10 "http://$DOMAIN/")

## 页面内容测试
### IP页面标题
$(curl -s --max-time 10 "http://$HOST/" | grep -i "title" | head -1)

### 域名页面标题
$(curl -s --max-time 10 "http://$DOMAIN/" | grep -i "title" | head -1)

## 建议
1. 如果DNS解析正确但浏览器无法访问，请清除浏览器缓存
2. 如果状态码不是200，请检查服务器配置
3. 如果页面内容异常，请检查应用服务状态
EOF

    success "访问报告已生成: $report_file"
}

# 主测试函数
main() {
    echo "🌐 开始域名访问测试"
    echo "测试域名: $DOMAIN"
    echo "服务器IP: $HOST"
    echo ""
    
    local test_results=()
    
    # 执行各项测试
    test_dns && test_results+=("✅ DNS解析") || test_results+=("❌ DNS解析")
    test_http_access && test_results+=("✅ HTTP访问") || test_results+=("❌ HTTP访问")
    test_page_content && test_results+=("✅ 页面内容") || test_results+=("❌ 页面内容")
    test_response_headers && test_results+=("✅ 响应头") || test_results+=("❌ 响应头")
    test_different_paths && test_results+=("✅ 路径测试") || test_results+=("❌ 路径测试")
    
    echo ""
    echo "📊 测试结果汇总:"
    for result in "${test_results[@]}"; do
        echo "  $result"
    done
    
    # 生成报告
    generate_access_report
    
    echo ""
    if [[ "${test_results[*]}" == *"❌"* ]]; then
        error "部分测试失败，请检查配置"
        echo ""
        echo "🔧 故障排除建议:"
        echo "  1. 检查DNS解析: nslookup $DOMAIN"
        echo "  2. 检查服务器状态: ssh root@$HOST 'systemctl status nginx'"
        echo "  3. 检查Nginx配置: ssh root@$HOST 'nginx -t'"
        echo "  4. 清除浏览器缓存并重试"
        exit 1
    else
        success "🎉 所有测试通过！域名访问正常"
        echo ""
        echo "🌐 访问地址:"
        echo "  • http://$HOST"
        echo "  • http://$DOMAIN"
        echo ""
        echo "💡 如果浏览器仍无法访问，请尝试:"
        echo "  1. 清除浏览器缓存 (Ctrl+F5)"
        echo "  2. 使用无痕模式访问"
        echo "  3. 检查是否有代理或VPN"
        echo "  4. 尝试不同的浏览器"
    fi
}

# 执行测试
main "$@"
