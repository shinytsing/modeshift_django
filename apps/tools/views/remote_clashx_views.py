#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
远程ClashX Pro管理API
功能：通过服务器API远程启动本地ClashX Pro，使用服务器配置文件
"""

import json
import logging
import os
import subprocess
import tempfile
import time
from pathlib import Path

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def remote_start_clashx_api(request):
    """远程启动ClashX Pro API"""
    try:
        data = json.loads(request.body)
        action = data.get("action", "start")
        
        if action == "start":
            return start_clashx_with_server_config()
        elif action == "stop":
            return stop_clashx()
        elif action == "restart":
            return restart_clashx_with_server_config()
        elif action == "status":
            return get_clashx_status()
        else:
            return JsonResponse({"success": False, "error": "不支持的操作"})
            
    except Exception as e:
        logger.error(f"远程ClashX操作失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


def start_clashx_with_server_config():
    """启动ClashX Pro并使用服务器配置"""
    try:
        # 1. 生成服务器配置文件
        config_content = generate_server_clash_config()
        
        # 2. 生成本地启动脚本
        script_content = generate_local_start_script(config_content)
        
        # 3. 返回启动指令
        return JsonResponse({
            "success": True,
            "message": "ClashX Pro启动指令已生成",
            "data": {
                "config_content": config_content,
                "script_content": script_content,
                "curl_command": generate_curl_command(),
                "instructions": [
                    "1. 将config_content保存为本地配置文件",
                    "2. 将script_content保存为启动脚本",
                    "3. 运行启动脚本启动ClashX Pro",
                    "4. 或直接使用curl命令远程启动"
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"生成ClashX启动配置失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


def generate_server_clash_config():
    """生成服务器Clash配置文件"""
    config = {
        "port": 7890,
        "socks-port": 7891,
        "allow-lan": False,
        "mode": "rule",
        "log-level": "info",
        "external-controller": "127.0.0.1:9090",
        "proxies": [
            {
                "name": "server-proxy-1",
                "type": "ss",
                "server": "47.103.143.152",
                "port": 8388,
                "cipher": "aes-256-gcm",
                "password": "your-password-here"
            },
            {
                "name": "server-proxy-2", 
                "type": "vmess",
                "server": "47.103.143.152",
                "port": 443,
                "uuid": "your-uuid-here",
                "alterId": 0,
                "cipher": "auto",
                "network": "ws",
                "ws-opts": {
                    "path": "/vmess"
                }
            }
        ],
        "proxy-groups": [
            {
                "name": "PROXY",
                "type": "select",
                "proxies": ["server-proxy-1", "server-proxy-2", "DIRECT"]
            },
            {
                "name": "AUTO",
                "type": "url-test",
                "proxies": ["server-proxy-1", "server-proxy-2"],
                "url": "http://www.gstatic.com/generate_204",
                "interval": 300
            }
        ],
        "rules": [
            "DOMAIN-SUFFIX,google.com,PROXY",
            "DOMAIN-SUFFIX,youtube.com,PROXY", 
            "DOMAIN-SUFFIX,github.com,PROXY",
            "DOMAIN-SUFFIX,twitter.com,PROXY",
            "DOMAIN-SUFFIX,facebook.com,PROXY",
            "DOMAIN-SUFFIX,instagram.com,PROXY",
            "GEOIP,CN,DIRECT",
            "MATCH,PROXY"
        ]
    }
    
    import yaml
    return yaml.dump(config, default_flow_style=False, allow_unicode=True)


def generate_local_start_script(config_content):
    """生成本地启动脚本"""
    script = f'''#!/bin/bash

# ClashX Pro 远程启动脚本
# 服务器: 47.103.143.152
# 域名: shenyiqing.xin

# 设置颜色输出
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m'

echo -e "${{BLUE}}========================================${{NC}}"
echo -e "${{BLUE}}     ClashX Pro 远程启动脚本${{NC}}"
echo -e "${{BLUE}}========================================${{NC}}"
echo ""

# 1. 创建配置文件
echo -e "${{YELLOW}}创建Clash配置文件...${{NC}}"
CONFIG_FILE="$HOME/.config/clash/config.yaml"
mkdir -p "$(dirname "$CONFIG_FILE")"

cat > "$CONFIG_FILE" << 'EOF'
{config_content}
EOF

if [ $? -eq 0 ]; then
    echo -e "${{GREEN}}✅ 配置文件创建成功: $CONFIG_FILE${{NC}}"
else
    echo -e "${{RED}}❌ 配置文件创建失败${{NC}}"
    exit 1
fi

# 2. 检查ClashX Pro是否已安装
echo -e "${{YELLOW}}检查ClashX Pro安装状态...${{NC}}"
if [ ! -d "/Applications/ClashX Pro.app" ]; then
    echo -e "${{RED}}❌ ClashX Pro 未安装${{NC}}"
    echo "请先安装ClashX Pro: https://github.com/yichengchen/clashX"
    exit 1
fi
echo -e "${{GREEN}}✅ ClashX Pro 已安装${{NC}}"

# 3. 停止现有ClashX Pro进程
echo -e "${{YELLOW}}停止现有ClashX Pro进程...${{NC}}"
if pgrep -f "ClashX Pro" > /dev/null; then
    pkill -f "ClashX Pro"
    sleep 2
    echo -e "${{GREEN}}✅ 现有进程已停止${{NC}}"
else
    echo -e "${{GREEN}}✅ 没有运行中的ClashX Pro进程${{NC}}"
fi

# 4. 启动ClashX Pro
echo -e "${{YELLOW}}启动ClashX Pro...${{NC}}"
open -a "ClashX Pro"

# 等待启动
echo "等待ClashX Pro启动..."
for i in {{1..10}}; do
    if pgrep -f "ClashX Pro" > /dev/null; then
        echo -e "${{GREEN}}✅ ClashX Pro 启动成功${{NC}}"
        break
    fi
    echo "等待中... ($i/10)"
    sleep 2
done

# 5. 等待代理服务启动
echo -e "${{YELLOW}}等待代理服务启动...${{NC}}"
for i in {{1..15}}; do
    if lsof -i :7890 > /dev/null 2>&1; then
        echo -e "${{GREEN}}✅ 代理服务已启动 (端口: 7890)${{NC}}"
        break
    fi
    echo "等待代理服务启动... ($i/15)"
    sleep 2
done

# 6. 配置系统代理
echo -e "${{YELLOW}}配置系统代理...${{NC}}"
networksetup -setwebproxy "Wi-Fi" 127.0.0.1 7890
networksetup -setsecurewebproxy "Wi-Fi" 127.0.0.1 7890
networksetup -setsocksfirewallproxy "Wi-Fi" 127.0.0.1 7891

if [ $? -eq 0 ]; then
    echo -e "${{GREEN}}✅ 系统代理配置成功${{NC}}"
else
    echo -e "${{YELLOW}}⚠️ 系统代理配置失败，请手动设置${{NC}}"
fi

# 7. 设置环境变量
echo -e "${{YELLOW}}设置环境变量...${{NC}}"
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

echo "export http_proxy=http://127.0.0.1:7890" >> ~/.bashrc
echo "export https_proxy=http://127.0.0.1:7890" >> ~/.bashrc
echo "export HTTP_PROXY=http://127.0.0.1:7890" >> ~/.bashrc
echo "export HTTPS_PROXY=http://127.0.0.1:7890" >> ~/.bashrc

echo -e "${{GREEN}}✅ 环境变量设置成功${{NC}}"

# 8. 测试连接
echo -e "${{YELLOW}}测试外网连接...${{NC}}"
if curl -x http://127.0.0.1:7890 -s https://httpbin.org/ip --connect-timeout 10 > /dev/null; then
    echo -e "${{GREEN}}✅ 外网连接测试成功${{NC}}"
    
    # 获取当前IP
    CURRENT_IP=$(curl -x http://127.0.0.1:7890 -s https://httpbin.org/ip | grep -o '"origin":"[^"]*"' | cut -d'"' -f4)
    echo -e "${{BLUE}}📍 当前IP: $CURRENT_IP${{NC}}"
else
    echo -e "${{RED}}❌ 外网连接测试失败${{NC}}"
fi

# 9. 显示管理信息
echo ""
echo -e "${{BLUE}}========================================${{NC}}"
echo -e "${{GREEN}}🎉 ClashX Pro 启动完成！${{NC}}"
echo -e "${{BLUE}}========================================${{NC}}"
echo -e "${{YELLOW}}代理配置信息:${{NC}}"
echo "  HTTP代理: 127.0.0.1:7890"
echo "  SOCKS代理: 127.0.0.1:7891"
echo "  管理界面: http://127.0.0.1:9090"
echo ""
echo -e "${{YELLOW}}服务器信息:${{NC}}"
echo "  服务器: 47.103.143.152"
echo "  域名: shenyiqing.xin"
echo "  用户: root"
echo ""
echo -e "${{GREEN}}现在可以访问外网了！${{NC}}"
'''
    
    return script


def generate_curl_command():
    """生成curl命令"""
    server_url = "https://shenyiqing.xin"  # 使用您的域名
    curl_cmd = f'''curl -X POST "{server_url}/api/clash/remote-start/" \\
  -H "Content-Type: application/json" \\
  -d '{{"action": "start"}}' \\
  --connect-timeout 30 \\
  --max-time 60'''
    
    return curl_cmd


def stop_clashx():
    """停止ClashX Pro"""
    try:
        # 生成停止脚本
        script_content = '''#!/bin/bash

# 停止ClashX Pro脚本

echo "正在停止ClashX Pro..."

# 停止ClashX Pro进程
if pgrep -f "ClashX Pro" > /dev/null; then
    pkill -f "ClashX Pro"
    echo "✅ ClashX Pro 已停止"
else
    echo "ℹ️ ClashX Pro 未在运行"
fi

# 禁用系统代理
networksetup -setwebproxystate "Wi-Fi" off
networksetup -setsecurewebproxystate "Wi-Fi" off
networksetup -setsocksfirewallproxystate "Wi-Fi" off

echo "✅ 系统代理已禁用"

# 清除环境变量
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY

echo "✅ 环境变量已清除"
echo "🎉 代理已完全关闭"
'''
        
        return JsonResponse({
            "success": True,
            "message": "ClashX Pro停止指令已生成",
            "data": {
                "script_content": script_content,
                "curl_command": f'''curl -X POST "https://shenyiqing.xin/api/clash/remote-start/" \\
  -H "Content-Type: application/json" \\
  -d '{{"action": "stop"}}' \\'''
            }
        })
        
    except Exception as e:
        logger.error(f"生成停止指令失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


def restart_clashx_with_server_config():
    """重启ClashX Pro"""
    try:
        # 先生成停止指令，再生成启动指令
        stop_result = stop_clashx()
        start_result = start_clashx_with_server_config()
        
        return JsonResponse({
            "success": True,
            "message": "ClashX Pro重启指令已生成",
            "data": {
                "stop_script": json.loads(stop_result.content)["data"]["script_content"],
                "start_script": json.loads(start_result.content)["data"]["script_content"],
                "curl_command": f'''curl -X POST "https://shenyiqing.xin/api/clash/remote-start/" \\
  -H "Content-Type: application/json" \\
  -d '{{"action": "restart"}}' \\'''
            }
        })
        
    except Exception as e:
        logger.error(f"生成重启指令失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


def get_clashx_status():
    """获取ClashX Pro状态"""
    try:
        # 生成状态检查脚本
        script_content = '''#!/bin/bash

# ClashX Pro 状态检查脚本

echo "========================================="
echo "     ClashX Pro 状态检查"
echo "========================================="
echo ""

# 检查ClashX Pro进程
echo "1. 检查ClashX Pro进程..."
if pgrep -f "ClashX Pro" > /dev/null; then
    CLASHX_PID=$(pgrep -f "ClashX Pro")
    echo "✅ ClashX Pro 正在运行 (PID: $CLASHX_PID)"
else
    echo "❌ ClashX Pro 未运行"
fi

# 检查代理端口
echo ""
echo "2. 检查代理端口..."
if lsof -i :7890 > /dev/null 2>&1; then
    echo "✅ HTTP代理端口 7890 正在监听"
else
    echo "❌ HTTP代理端口 7890 未监听"
fi

if lsof -i :7891 > /dev/null 2>&1; then
    echo "✅ SOCKS代理端口 7891 正在监听"
else
    echo "❌ SOCKS代理端口 7891 未监听"
fi

# 检查系统代理设置
echo ""
echo "3. 检查系统代理设置..."
HTTP_PROXY=$(networksetup -getwebproxy "Wi-Fi" | grep "Enabled: Yes")
if [ -n "$HTTP_PROXY" ]; then
    echo "✅ HTTP代理已启用"
else
    echo "❌ HTTP代理未启用"
fi

# 测试连接
echo ""
echo "4. 测试外网连接..."
if curl -x http://127.0.0.1:7890 -s https://httpbin.org/ip --connect-timeout 10 > /dev/null; then
    CURRENT_IP=$(curl -x http://127.0.0.1:7890 -s https://httpbin.org/ip | grep -o '"origin":"[^"]*"' | cut -d'"' -f4)
    echo "✅ 外网连接正常"
    echo "📍 当前IP: $CURRENT_IP"
else
    echo "❌ 外网连接失败"
fi

echo ""
echo "========================================="
echo "状态检查完成"
echo "========================================="
'''
        
        return JsonResponse({
            "success": True,
            "message": "ClashX Pro状态检查指令已生成",
            "data": {
                "script_content": script_content,
                "curl_command": f'''curl -X POST "https://shenyiqing.xin/api/clash/remote-start/" \\
  -H "Content-Type: application/json" \\
  -d '{{"action": "status"}}' \\'''
            }
        })
        
    except Exception as e:
        logger.error(f"生成状态检查指令失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["GET"])
def download_clash_config_api(request):
    """下载Clash配置文件"""
    try:
        config_content = generate_server_clash_config()
        
        response = HttpResponse(config_content, content_type='application/x-yaml')
        response['Content-Disposition'] = 'attachment; filename="clash_config.yaml"'
        return response
        
    except Exception as e:
        logger.error(f"下载配置文件失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["GET"])
def download_start_script_api(request):
    """下载启动脚本"""
    try:
        config_content = generate_server_clash_config()
        script_content = generate_local_start_script(config_content)
        
        response = HttpResponse(script_content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="start_clashx.sh"'
        return response
        
    except Exception as e:
        logger.error(f"下载启动脚本失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})
