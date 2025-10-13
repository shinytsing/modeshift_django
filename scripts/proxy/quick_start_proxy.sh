#!/bin/bash

# 一键启动ClashX Pro代理
# 服务器: 47.103.143.152
# 域名: shenyiqing.xin
# 用户: root

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}      一键启动ClashX Pro代理${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}服务器信息:${NC}"
echo "  服务器: 47.103.143.152"
echo "  域名: shenyiqing.xin"
echo "  用户: root"
echo ""

# 检查ClashX Pro是否已安装
echo -e "${YELLOW}检查ClashX Pro安装状态...${NC}"
if [ ! -d "/Applications/ClashX Pro.app" ]; then
    echo -e "${RED}❌ ClashX Pro 未安装${NC}"
    echo "请先安装ClashX Pro: https://github.com/yichengchen/clashX"
    exit 1
fi
echo -e "${GREEN}✅ ClashX Pro 已安装${NC}"

# 检查ClashX Pro是否正在运行
echo -e "${YELLOW}检查ClashX Pro运行状态...${NC}"
if pgrep -f "ClashX Pro" > /dev/null; then
    echo -e "${GREEN}✅ ClashX Pro 正在运行${NC}"
    clashx_pid=$(pgrep -f "ClashX Pro")
    echo "   进程ID: $clashx_pid"
else
    echo -e "${YELLOW}⚠️ ClashX Pro 未运行，正在启动...${NC}"
    
    # 启动ClashX Pro
    open -a "ClashX Pro"
    
    # 等待启动
    echo "等待ClashX Pro启动..."
    for i in {1..10}; do
        if pgrep -f "ClashX Pro" > /dev/null; then
            echo -e "${GREEN}✅ ClashX Pro 启动成功${NC}"
            break
        fi
        echo "等待中... ($i/10)"
        sleep 2
    done
    
    # 再次检查
    if ! pgrep -f "ClashX Pro" > /dev/null; then
        echo -e "${RED}❌ ClashX Pro 启动失败${NC}"
        echo "请手动启动ClashX Pro或检查安装"
        exit 1
    fi
fi

# 等待代理服务启动
echo -e "${YELLOW}等待代理服务启动...${NC}"
for i in {1..15}; do
    if lsof -i :7890 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ HTTP代理端口 7890 已启动${NC}"
        break
    fi
    echo "等待代理服务启动... ($i/15)"
    sleep 2
done

# 检查代理端口
if ! lsof -i :7890 > /dev/null 2>&1; then
    echo -e "${RED}❌ HTTP代理端口 7890 未启动${NC}"
    echo "请检查ClashX Pro配置"
    exit 1
fi

# 设置系统代理
echo -e "${YELLOW}设置系统代理...${NC}"
networksetup -setwebproxy "Wi-Fi" 127.0.0.1 7890
networksetup -setsecurewebproxy "Wi-Fi" 127.0.0.1 7890
networksetup -setsocksfirewallproxy "Wi-Fi" 127.0.0.1 7891

echo -e "${GREEN}✅ 系统代理已设置${NC}"
echo "HTTP代理: 127.0.0.1:7890"
echo "SOCKS代理: 127.0.0.1:7891"

# 设置环境变量
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

echo -e "${GREEN}✅ 环境变量已设置${NC}"

# 测试连接
echo ""
echo -e "${YELLOW}测试代理连接...${NC}"

# 测试Google
echo -n "测试Google连接... "
if curl -x http://127.0.0.1:7890 -I https://www.google.com --connect-timeout 10 --max-time 15 > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
fi

# 测试YouTube
echo -n "测试YouTube连接... "
if curl -x http://127.0.0.1:7890 -I https://www.youtube.com --connect-timeout 10 --max-time 15 > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
fi

# 测试GitHub
echo -n "测试GitHub连接... "
if curl -x http://127.0.0.1:7890 -I https://www.github.com --connect-timeout 10 --max-time 15 > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
fi

# 获取当前IP
echo -n "获取当前IP地址... "
current_ip=$(curl -x http://127.0.0.1:7890 -s https://httpbin.org/ip 2>/dev/null | grep -o '"[0-9.]*"' | tr -d '"')
if [ -n "$current_ip" ]; then
    echo -e "${GREEN}${current_ip}${NC}"
else
    echo -e "${RED}获取失败${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}      代理启动完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}管理界面: http://127.0.0.1:9090${NC}"
echo -e "${BLUE}代理状态: 已启用${NC}"
echo -e "${BLUE}当前IP: ${current_ip:-未知}${NC}"
echo ""
echo -e "${YELLOW}常用命令:${NC}"
echo "  关闭代理: ./proxy_manager.sh off"
echo "  检查状态: ./proxy_manager.sh status"
echo "  测试连接: ./proxy_manager.sh test"
echo ""
