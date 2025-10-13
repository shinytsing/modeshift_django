#!/bin/bash

# 代理应用启动器
# 提供多种启动选项

echo "=== 代理应用启动器 ==="
echo ""
echo "请选择要启动的应用："
echo "1. 简单代理开关 (推荐)"
echo "2. 完整代理管理器"
echo "3. Python图形界面版本"
echo "4. 命令行工具"
echo "5. 退出"
echo ""

read -p "请输入选择 (1-5): " choice

case $choice in
    1)
        echo "启动简单代理开关..."
        open SimpleProxyToggle.app
        ;;
    2)
        echo "启动完整代理管理器..."
        open ProxyToggle.app
        ;;
    3)
        echo "启动Python图形界面版本..."
        ./start_proxy_app.sh
        ;;
    4)
        echo "启动命令行工具..."
        ./proxy_manager.sh help
        ;;
    5)
        echo "退出"
        exit 0
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac
