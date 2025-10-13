#!/bin/bash

# 自动修复代理配置脚本

echo "=== 自动修复代理配置 ==="

# 检查ClashX Pro是否运行
if ! pgrep -f "ClashX Pro" > /dev/null; then
    echo "❌ ClashX Pro 未运行，请先启动 ClashX Pro"
    exit 1
fi

echo "✅ ClashX Pro 正在运行"

# 检查代理端口
if ! lsof -i :7890 > /dev/null 2>&1; then
    echo "❌ 代理端口 7890 未监听"
    exit 1
fi

echo "✅ 代理端口 7890 正在监听"

# 获取代理节点信息
echo "检查代理节点状态..."
PROXY_INFO=$(curl -s http://127.0.0.1:9090/proxies)

# 提取延迟最低的节点
echo "寻找最佳代理节点..."

# 测试各个节点的延迟
BEST_NODE=""
BEST_DELAY=999999

for node in "HongKong-IPLC-HK-1" "Japan-TY-1" "UnitedStates-US-1" "Singapore-SG-1" "Netherlands-NL-1"; do
    echo -n "测试 $node ... "
    
    # 切换到该节点
    curl -X PUT -H "Content-Type: application/json" -d "{\"name\":\"$node\"}" http://127.0.0.1:9090/proxies/GLOBAL > /dev/null 2>&1
    
    # 等待切换完成
    sleep 2
    
    # 测试连接延迟
    START_TIME=$(date +%s%3N)
    if curl -x http://127.0.0.1:7890 -I https://www.google.com --connect-timeout 5 --max-time 10 > /dev/null 2>&1; then
        END_TIME=$(date +%s%3N)
        DELAY=$((END_TIME - START_TIME))
        echo "延迟: ${DELAY}ms"
        
        if [ $DELAY -lt $BEST_DELAY ]; then
            BEST_DELAY=$DELAY
            BEST_NODE=$node
        fi
    else
        echo "连接失败"
    fi
done

if [ -n "$BEST_NODE" ]; then
    echo ""
    echo "✅ 最佳节点: $BEST_NODE (延迟: ${BEST_DELAY}ms)"
    
    # 切换到最佳节点
    curl -X PUT -H "Content-Type: application/json" -d "{\"name\":\"$BEST_NODE\"}" http://127.0.0.1:9090/proxies/GLOBAL > /dev/null 2>&1
    
    echo "✅ 已切换到最佳节点"
    
    # 最终测试
    echo ""
    echo "最终连接测试..."
    if curl -x http://127.0.0.1:7890 -I https://www.google.com --connect-timeout 5 > /dev/null 2>&1; then
        echo "✅ Google连接成功"
    else
        echo "❌ Google连接失败"
    fi
    
    if curl -x http://127.0.0.1:7890 -I https://www.youtube.com --connect-timeout 5 > /dev/null 2>&1; then
        echo "✅ YouTube连接成功"
    else
        echo "❌ YouTube连接失败"
    fi
    
    # 获取当前IP
    CURRENT_IP=$(curl -x http://127.0.0.1:7890 -s https://httpbin.org/ip 2>/dev/null | grep -o '"[0-9.]*"' | tr -d '"')
    if [ -n "$CURRENT_IP" ]; then
        echo "当前IP: $CURRENT_IP"
    fi
    
else
    echo "❌ 没有找到可用的代理节点"
    exit 1
fi

echo ""
echo "=== 修复完成 ==="
echo "代理配置已优化，现在应该可以正常访问外网了！"
