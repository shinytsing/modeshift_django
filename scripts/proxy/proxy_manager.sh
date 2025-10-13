#!/bin/bash

# 代理管理器
# 服务器: 47.103.143.152
# 域名: shenyiqing.xin

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}           代理管理器${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo "使用方法:"
    echo "  ./proxy_manager.sh on     - 开启代理"
    echo "  ./proxy_manager.sh off    - 关闭代理"
    echo "  ./proxy_manager.sh status - 检查状态"
    echo "  ./proxy_manager.sh test   - 测试连接"
    echo "  ./proxy_manager.sh help   - 显示帮助"
    echo ""
    echo "服务器信息:"
    echo "  服务器: 47.103.143.152"
    echo "  域名: shenyiqing.xin"
    echo "  用户: root"
    echo ""
}

# 开启代理
proxy_on() {
    echo -e "${YELLOW}=== 开启代理 ===${NC}"
    
    # 设置代理环境变量
    export http_proxy=http://127.0.0.1:7890
    export https_proxy=http://127.0.0.1:7890
    export HTTP_PROXY=http://127.0.0.1:7890
    export HTTPS_PROXY=http://127.0.0.1:7890
    
    # 设置系统代理（macOS）
    networksetup -setwebproxy "Wi-Fi" 127.0.0.1 7890
    networksetup -setsecurewebproxy "Wi-Fi" 127.0.0.1 7890
    networksetup -setsocksfirewallproxy "Wi-Fi" 127.0.0.1 7891
    
    echo -e "${GREEN}✅ 代理已开启${NC}"
    echo "HTTP代理: 127.0.0.1:7890"
    echo "SOCKS代理: 127.0.0.1:7891"
    echo ""
    
    # 测试连接
    echo -e "${YELLOW}测试连接...${NC}"
    if curl -x http://127.0.0.1:7890 -I https://www.google.com --connect-timeout 5 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Google连接成功${NC}"
    else
        echo -e "${RED}❌ Google连接失败${NC}"
    fi
    
    # 获取当前IP
    current_ip=$(curl -x http://127.0.0.1:7890 -s https://httpbin.org/ip 2>/dev/null | grep -o '"[0-9.]*"' | tr -d '"')
    if [ -n "$current_ip" ]; then
        echo -e "${BLUE}当前IP: $current_ip${NC}"
    fi
}

# 关闭代理
proxy_off() {
    echo -e "${YELLOW}=== 关闭代理 ===${NC}"
    
    # 清除代理环境变量
    unset http_proxy
    unset https_proxy
    unset HTTP_PROXY
    unset HTTPS_PROXY
    
    # 关闭系统代理（macOS）
    networksetup -setwebproxystate "Wi-Fi" off
    networksetup -setsecurewebproxystate "Wi-Fi" off
    networksetup -setsocksfirewallproxystate "Wi-Fi" off
    
    echo -e "${GREEN}✅ 代理已关闭${NC}"
    echo ""
    
    # 测试直连
    echo -e "${YELLOW}测试直连...${NC}"
    if curl -I https://www.baidu.com --connect-timeout 5 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 百度连接成功（直连）${NC}"
    else
        echo -e "${RED}❌ 百度连接失败${NC}"
    fi
    
    # 获取当前IP
    current_ip=$(curl -s https://httpbin.org/ip 2>/dev/null | grep -o '"[0-9.]*"' | tr -d '"')
    if [ -n "$current_ip" ]; then
        echo -e "${BLUE}当前IP: $current_ip${NC}"
    fi
}

# 检查状态
check_status() {
    echo -e "${YELLOW}=== 代理状态检查 ===${NC}"
    
    # 检查ClashX Pro进程
    if pgrep -f "ClashX Pro" > /dev/null; then
        echo -e "${GREEN}✅ ClashX Pro 正在运行${NC}"
        clashx_pid=$(pgrep -f "ClashX Pro")
        echo "   进程ID: $clashx_pid"
    else
        echo -e "${RED}❌ ClashX Pro 未运行${NC}"
    fi
    
    # 检查代理端口
    echo ""
    echo "端口状态:"
    if lsof -i :7890 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ HTTP代理端口 7890 正在监听${NC}"
    else
        echo -e "${RED}❌ HTTP代理端口 7890 未监听${NC}"
    fi
    
    if lsof -i :7891 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ SOCKS代理端口 7891 正在监听${NC}"
    else
        echo -e "${RED}❌ SOCKS代理端口 7891 未监听${NC}"
    fi
    
    if lsof -i :9090 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 管理界面端口 9090 正在监听${NC}"
    else
        echo -e "${RED}❌ 管理界面端口 9090 未监听${NC}"
    fi
    
    # 检查系统代理设置
    echo ""
    echo "系统代理设置:"
    web_proxy=$(networksetup -getwebproxy "Wi-Fi")
    if [[ $web_proxy == *"Enabled: Yes"* ]]; then
        echo -e "${GREEN}✅ HTTP代理已启用${NC}"
    else
        echo -e "${RED}❌ HTTP代理未启用${NC}"
    fi
    
    secure_proxy=$(networksetup -getsecurewebproxy "Wi-Fi")
    if [[ $secure_proxy == *"Enabled: Yes"* ]]; then
        echo -e "${GREEN}✅ HTTPS代理已启用${NC}"
    else
        echo -e "${RED}❌ HTTPS代理未启用${NC}"
    fi
    
    socks_proxy=$(networksetup -getsocksfirewallproxy "Wi-Fi")
    if [[ $socks_proxy == *"Enabled: Yes"* ]]; then
        echo -e "${GREEN}✅ SOCKS代理已启用${NC}"
    else
        echo -e "${RED}❌ SOCKS代理未启用${NC}"
    fi
}

# 测试连接
test_connection() {
    echo -e "${YELLOW}=== 连接测试 ===${NC}"
    
    local success_count=0
    local total_tests=5
    
    # 测试Google
    echo -n "测试Google连接... "
    if curl -x http://127.0.0.1:7890 -I https://www.google.com --connect-timeout 10 --max-time 15 > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
        ((success_count++))
    else
        echo -e "${RED}❌${NC}"
    fi
    
    # 测试YouTube
    echo -n "测试YouTube连接... "
    if curl -x http://127.0.0.1:7890 -I https://www.youtube.com --connect-timeout 10 --max-time 15 > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
        ((success_count++))
    else
        echo -e "${RED}❌${NC}"
    fi
    
    # 测试GitHub
    echo -n "测试GitHub连接... "
    if curl -x http://127.0.0.1:7890 -I https://www.github.com --connect-timeout 10 --max-time 15 > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
        ((success_count++))
    else
        echo -e "${RED}❌${NC}"
    fi
    
    # 测试Facebook
    echo -n "测试Facebook连接... "
    if curl -x http://127.0.0.1:7890 -I https://www.facebook.com --connect-timeout 10 --max-time 15 > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
        ((success_count++))
    else
        echo -e "${RED}❌${NC}"
    fi
    
    # 测试Twitter
    echo -n "测试Twitter连接... "
    if curl -x http://127.0.0.1:7890 -I https://www.twitter.com --connect-timeout 10 --max-time 15 > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
        ((success_count++))
    else
        echo -e "${RED}❌${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}连接测试结果: ${success_count}/${total_tests} 成功${NC}"
    
    # 获取当前IP
    echo -n "获取当前IP地址... "
    current_ip=$(curl -x http://127.0.0.1:7890 -s https://httpbin.org/ip 2>/dev/null | grep -o '"[0-9.]*"' | tr -d '"')
    if [ -n "$current_ip" ]; then
        echo -e "${GREEN}${current_ip}${NC}"
    else
        echo -e "${RED}获取失败${NC}"
    fi
}

# 主函数
main() {
    case "$1" in
        "on")
            proxy_on
            ;;
        "off")
            proxy_off
            ;;
        "status")
            check_status
            ;;
        "test")
            test_connection
            ;;
        "help"|"-h"|"--help"|"")
            show_help
            ;;
        *)
            echo -e "${RED}无效参数: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
