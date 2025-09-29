import json
import logging
import platform

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..services.clash_config_manager import ClashConfigManager
from ..services.clash_service import clash_service

logger = logging.getLogger(__name__)


def clash_dashboard(request):
    """Clash内嵌代理仪表板"""
    return render(request, "tools/clash_dashboard.html")


@csrf_exempt
@require_http_methods(["GET"])
def clash_status_api(request):
    """获取Clash服务状态"""
    try:
        status = clash_service.get_status()
        return JsonResponse({"success": True, "data": status})
    except Exception as e:
        logger.error(f"获取Clash状态失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def clash_start_api(request):
    """启动Clash服务"""
    try:
        success, message = clash_service.start_clash()
        return JsonResponse({"success": success, "message": message})
    except Exception as e:
        logger.error(f"启动Clash失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def clash_stop_api(request):
    """停止Clash服务"""
    try:
        success, message = clash_service.stop_clash()
        return JsonResponse({"success": success, "message": message})
    except Exception as e:
        logger.error(f"停止Clash失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def clash_restart_api(request):
    """重启Clash服务"""
    try:
        success, message = clash_service.restart_clash()
        return JsonResponse({"success": success, "message": message})
    except Exception as e:
        logger.error(f"重启Clash失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def clash_test_connection_api(request):
    """测试Clash连接"""
    try:
        success, message = clash_service.test_connection()
        return JsonResponse({"success": success, "message": message})
    except Exception as e:
        logger.error(f"测试Clash连接失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def clash_proxy_info_api(request):
    """获取代理信息 - 隐藏敏感信息"""
    try:
        proxy_info = clash_service.get_proxy_info()

        # 隐藏敏感信息，只返回基本信息
        safe_proxy_info = {
            "status": proxy_info.get("status", "unknown"),
            "current_proxy": proxy_info.get("current_proxy", ""),
            "available_proxies": len(proxy_info.get("proxies", [])),
            "proxy_groups": proxy_info.get("proxy_groups", []),
            "connection_status": proxy_info.get("connection_status", "unknown"),
        }

        return JsonResponse({"success": True, "data": safe_proxy_info})
    except Exception as e:
        logger.error(f"获取代理信息失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def clash_switch_proxy_api(request):
    """切换代理"""
    try:
        data = json.loads(request.body)
        group = data.get("group", "PROXY")
        proxy = data.get("proxy")

        if not proxy:
            return JsonResponse({"success": False, "error": "请指定代理名称"})

        success, message = clash_service.switch_proxy(group, proxy)
        return JsonResponse({"success": success, "message": message})
    except Exception as e:
        logger.error(f"切换代理失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def clash_install_api(request):
    """安装Clash"""
    try:
        success, message = clash_service.install_clash()

        if success:
            return JsonResponse({"success": True, "message": message, "type": "success"})
        else:
            # 安装失败，提供详细的错误信息和解决方案
            return JsonResponse(
                {
                    "success": False,
                    "message": message,
                    "type": "error",
                    "solutions": _get_clash_install_solutions(),
                    "manual_guide": _get_manual_install_guide(),
                }
            )

    except Exception as e:
        logger.error(f"安装Clash失败: {e}")
        return JsonResponse(
            {
                "success": False,
                "message": f"安装过程中发生错误: {str(e)}",
                "type": "error",
                "solutions": _get_clash_install_solutions(),
                "manual_guide": _get_manual_install_guide(),
            }
        )


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def clash_config_api(request):
    """获取Clash配置 - 隐藏敏感信息"""
    try:
        config_manager = ClashConfigManager(clash_service.clash_config_path)
        config = config_manager.export_config()

        # 隐藏敏感配置信息
        safe_config = {
            "port": config.get("port", 7890),
            "socks-port": config.get("socks-port", 7891),
            "allow-lan": config.get("allow-lan", False),
            "mode": config.get("mode", "rule"),
            "log-level": config.get("log-level", "info"),
            "external-controller": config.get("external-controller", "127.0.0.1:9090"),
        }

        # 获取代理列表但隐藏敏感信息
        proxies = config_manager.get_proxy_list()
        safe_proxies = []
        for proxy in proxies:
            safe_proxy = {
                "name": proxy.get("name", ""),
                "type": proxy.get("type", ""),
                "server": proxy.get("server", ""),
                "port": proxy.get("port", ""),
                "country": proxy.get("country", ""),
                "city": proxy.get("city", ""),
            }
            # 隐藏密码、密钥等敏感信息
            safe_proxies.append(safe_proxy)

        return JsonResponse(
            {
                "success": True,
                "data": {
                    "config": safe_config,
                    "proxies": safe_proxies,
                    "proxy_groups": config_manager.get_proxy_groups(),
                    "rules": config_manager.get_rules(),
                },
            }
        )
    except Exception as e:
        logger.error(f"获取Clash配置失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def clash_update_config_api(request):
    """更新Clash配置"""
    try:
        data = json.loads(request.body)
        config_data = data.get("config")

        if not config_data:
            return JsonResponse({"success": False, "error": "请提供配置数据"})

        config_manager = ClashConfigManager(clash_service.clash_config_path)
        success = config_manager.import_config(config_data)

        if success:
            config_manager.save_config()
            return JsonResponse({"success": True, "message": "配置更新成功"})
        else:
            return JsonResponse({"success": False, "error": "配置格式错误"})
    except Exception as e:
        logger.error(f"更新Clash配置失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def clash_add_proxy_api(request):
    """添加代理节点"""
    try:
        data = json.loads(request.body)
        proxy_config = data.get("proxy")

        if not proxy_config:
            return JsonResponse({"success": False, "error": "请提供代理配置"})

        config_manager = ClashConfigManager(clash_service.clash_config_path)
        config_manager.add_proxy(proxy_config)
        config_manager.save_config()

        return JsonResponse({"success": True, "message": "代理节点添加成功"})
    except Exception as e:
        logger.error(f"添加代理节点失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def clash_remove_proxy_api(request):
    """移除代理节点"""
    try:
        data = json.loads(request.body)
        proxy_name = data.get("proxy_name")

        if not proxy_name:
            return JsonResponse({"success": False, "error": "请指定代理名称"})

        config_manager = ClashConfigManager(clash_service.clash_config_path)
        config_manager.remove_proxy(proxy_name)
        config_manager.save_config()

        return JsonResponse({"success": True, "message": "代理节点移除成功"})
    except Exception as e:
        logger.error(f"移除代理节点失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


def _get_clash_install_solutions():
    """获取Clash安装解决方案"""
    system = platform.system().lower()

    solutions = [
        {
            "title": "方案1: 使用包管理器安装 (推荐)",
            "description": "这是最简单快捷的安装方式",
            "commands": _get_package_manager_commands(system),
            "difficulty": "简单",
        },
        {
            "title": "方案2: 下载图形界面版本",
            "description": "适合不熟悉命令行的用户",
            "links": _get_gui_download_links(system),
            "difficulty": "简单",
        },
        {
            "title": "方案3: 手动下载二进制文件",
            "description": "适合需要自定义安装位置的用户",
            "commands": _get_manual_download_commands(system),
            "difficulty": "中等",
        },
        {
            "title": "方案4: 使用镜像站下载",
            "description": "适合网络访问GitHub困难的用户",
            "commands": _get_mirror_download_commands(system),
            "difficulty": "中等",
        },
    ]

    return solutions


def _get_package_manager_commands(system):
    """获取包管理器安装命令"""
    if system == "darwin":  # macOS
        return [
            "brew install clash",
            '# 如果没有Homebrew，先安装: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
        ]
    elif system == "linux":
        return [
            "# Ubuntu/Debian:",
            "sudo apt update && sudo apt install clash",
            "",
            "# CentOS/RHEL:",
            "sudo yum install clash",
            "",
            "# Arch Linux:",
            "sudo pacman -S clash",
        ]
    elif system == "windows":
        return [
            "# 使用Chocolatey:",
            "choco install clash",
            "",
            "# 如果没有Chocolatey，先安装:",
            "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))",
        ]
    else:
        return ["请查看官方文档获取安装方法"]


def _get_gui_download_links(system):
    """获取图形界面下载链接"""
    if system == "darwin":  # macOS
        return [{"name": "ClashX", "url": "https://github.com/yichengchen/clashX/releases", "description": "macOS专用图形界面版本"}]
    elif system == "windows":
        return [
            {
                "name": "Clash for Windows",
                "url": "https://github.com/Fndroid/clash_for_windows_pkg/releases",
                "description": "Windows专用图形界面版本",
            }
        ]
    else:
        return [
            {
                "name": "ClashX Pro",
                "url": "https://github.com/yichengchen/clashX/releases",
                "description": "跨平台图形界面版本",
            }
        ]


def _get_manual_download_commands(system):
    """获取手动下载命令"""
    arch = platform.machine().lower()

    if system == "darwin":  # macOS
        if arch in ["arm64", "aarch64"]:
            return [
                "curl -L https://github.com/Dreamacro/clash/releases/latest/download/clash-darwin-arm64.gz -o clash.gz",
                "gunzip clash.gz",
                "chmod +x clash",
                "sudo mv clash /usr/local/bin/",
            ]
        else:
            return [
                "curl -L https://github.com/Dreamacro/clash/releases/latest/download/clash-darwin-amd64.gz -o clash.gz",
                "gunzip clash.gz",
                "chmod +x clash",
                "sudo mv clash /usr/local/bin/",
            ]
    elif system == "linux":
        if arch in ["arm64", "aarch64"]:
            return [
                "wget https://github.com/Dreamacro/clash/releases/latest/download/clash-linux-arm64.gz",
                "gunzip clash-linux-arm64.gz",
                "chmod +x clash-linux-arm64",
                "sudo mv clash-linux-arm64 /usr/local/bin/clash",
            ]
        else:
            return [
                "wget https://github.com/Dreamacro/clash/releases/latest/download/clash-linux-amd64.gz",
                "gunzip clash-linux-amd64.gz",
                "chmod +x clash-linux-amd64",
                "sudo mv clash-linux-amd64 /usr/local/bin/clash",
            ]
    elif system == "windows":
        return [
            'Invoke-WebRequest -Uri "https://github.com/Dreamacro/clash/releases/latest/download/clash-windows-amd64.gz" -OutFile "clash.gz"',
            "# 使用7-Zip或其他工具解压gz文件",
            "# 将解压后的文件重命名为clash.exe并放到PATH目录中",
        ]
    else:
        return ["请访问 https://github.com/Dreamacro/clash/releases/latest 下载适合您系统的版本"]


def _get_mirror_download_commands(system):
    """获取镜像站下载命令"""
    arch = platform.machine().lower()

    if system == "darwin":  # macOS
        if arch in ["arm64", "aarch64"]:
            return [
                "curl -L https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest/download/clash-darwin-arm64.gz -o clash.gz",
                "gunzip clash.gz",
                "chmod +x clash",
                "sudo mv clash /usr/local/bin/",
            ]
        else:
            return [
                "curl -L https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest/download/clash-darwin-amd64.gz -o clash.gz",
                "gunzip clash.gz",
                "chmod +x clash",
                "sudo mv clash /usr/local/bin/",
            ]
    elif system == "linux":
        if arch in ["arm64", "aarch64"]:
            return [
                "wget https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest/download/clash-linux-arm64.gz",
                "gunzip clash-linux-arm64.gz",
                "chmod +x clash-linux-arm64",
                "sudo mv clash-linux-arm64 /usr/local/bin/clash",
            ]
        else:
            return [
                "wget https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest/download/clash-linux-amd64.gz",
                "gunzip clash-linux-amd64.gz",
                "chmod +x clash-linux-amd64",
                "sudo mv clash-linux-amd64 /usr/local/bin/clash",
            ]
    else:
        return ["请使用镜像站访问: https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest"]


@csrf_exempt
@require_http_methods(["POST"])
def clash_configure_proxy_api(request):
    """配置系统代理API"""
    try:
        # 检查Clash服务状态
        status = clash_service.get_status()
        if not status.get("is_running"):
            return JsonResponse({"success": False, "error": "Clash服务未运行，请先启动服务"})
        
        # 动态检测可用的代理端口
        available_port = find_available_proxy_port()
        if not available_port:
            return JsonResponse({
                "success": False, 
                "error": "未找到可用的代理端口，请检查Clash配置",
                "proxy_configured": False
            })
        
        # 使用检测到的端口配置系统代理
        success, message = configure_system_proxy(available_port, available_port)
        
        if success:
            return JsonResponse({
                "success": True,
                "message": f"{message} (端口: {available_port})",
                "proxy_configured": True,
                "http_port": available_port,
                "socks_port": available_port
            })
        else:
            return JsonResponse({
                "success": False,
                "error": message,
                "proxy_configured": False
            })
            
    except Exception as e:
        logger.error(f"配置系统代理失败: {e}")
        return JsonResponse({"success": False, "error": f"配置失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
def clash_test_external_access_api(request):
    """测试外网访问API - 增强版，支持无Clash环境"""
    try:
        # 检查Clash服务状态
        status = clash_service.get_status()
        clash_running = status.get("is_running", False)
        
        # 动态检测可用的代理端口
        available_port = find_available_proxy_port()
        
        # 如果没有Clash和代理，尝试直接连接
        if not clash_running and not available_port:
            logger.info("未检测到Clash服务和代理，尝试直接外网连接...")
            return test_direct_external_access()
        
        if not available_port:
            return JsonResponse({"success": False, "error": "未找到可用的代理端口"})
        
        # 使用检测到的端口测试外网访问
        try:
            import requests
            import time
            
            proxies = {
                "http": f"http://127.0.0.1:{available_port}",
                "https": f"http://127.0.0.1:{available_port}"
            }
            
            logger.info(f"使用端口 {available_port} 测试外网访问")
            
            # 测试多个外网服务，提高成功率
            test_services = [
                {"name": "httpbin.org", "url": "http://httpbin.org/get", "ip_url": "http://httpbin.org/ip"},
                {"name": "Google", "url": "http://www.google.com/favicon.ico", "ip_url": "http://httpbin.org/ip"},
                {"name": "Cloudflare", "url": "http://1.1.1.1", "ip_url": "http://httpbin.org/ip"},
            ]
            
            test_results = []
            successful_service = None
            
            for service in test_services:
                try:
                    start_time = time.time()
                    
                    # 测试基本连接
                    test_response = requests.get(service["url"], proxies=proxies, timeout=10)
                    response_time = time.time() - start_time
                    
                    if test_response.status_code in [200, 301, 302]:
                        # 获取IP信息
                        try:
                            ip_response = requests.get(service["ip_url"], proxies=proxies, timeout=10)
                            if ip_response.status_code == 200:
                                ip_data = ip_response.json()
                                current_ip = ip_data.get("origin", "unknown")
                            else:
                                current_ip = "unknown"
                        except:
                            current_ip = "unknown"
                        
                        test_results.append({
                            "service": service["name"],
                            "status": "success",
                            "response_time": round(response_time, 2),
                            "ip": current_ip
                        })
                        
                        if not successful_service:
                            successful_service = {
                                "service": service["name"],
                                "ip": current_ip,
                                "response_time": response_time
                            }
                            
                    else:
                        test_results.append({
                            "service": service["name"],
                            "status": "failed",
                            "status_code": test_response.status_code,
                            "response_time": round(response_time, 2)
                        })
                        
                except Exception as e:
                    test_results.append({
                        "service": service["name"],
                        "status": "error",
                        "error": str(e)
                    })
            
            if successful_service:
                return JsonResponse({
                    "success": True,
                    "message": f"外网访问测试成功 (端口: {available_port})",
                    "ip": successful_service["ip"],
                    "service": successful_service["service"],
                    "response_time": round(successful_service["response_time"], 2),
                    "proxy_port": available_port,
                    "test_results": test_results
                })
            else:
                return JsonResponse({
                    "success": False,
                    "error": "所有外网服务测试失败",
                    "test_results": test_results,
                    "proxy_port": available_port
                })
                
        except requests.exceptions.ProxyError as e:
            logger.error(f"代理连接错误: {e}")
            return JsonResponse({"success": False, "error": f"代理连接失败: {str(e)}"})
        except requests.exceptions.ConnectionError as e:
            logger.error(f"连接错误: {e}")
            return JsonResponse({"success": False, "error": f"连接失败: {str(e)}"})
        except Exception as e:
            logger.error(f"请求错误: {e}")
            return JsonResponse({"success": False, "error": f"请求失败: {str(e)}"})
            
    except Exception as e:
        logger.error(f"测试外网访问失败: {e}")
        return JsonResponse({"success": False, "error": f"测试失败: {str(e)}"})


def test_direct_external_access():
    """测试直接外网访问（无代理环境）"""
    try:
        import requests
        import time
        
        logger.info("开始测试直接外网访问...")
        
        # 测试多个外网服务
        test_services = [
            {"name": "httpbin.org", "url": "http://httpbin.org/get", "ip_url": "http://httpbin.org/ip"},
            {"name": "Google", "url": "http://www.google.com/favicon.ico", "ip_url": "http://httpbin.org/ip"},
            {"name": "Cloudflare", "url": "http://1.1.1.1", "ip_url": "http://httpbin.org/ip"},
            {"name": "GitHub", "url": "https://api.github.com", "ip_url": "http://httpbin.org/ip"},
        ]
        
        test_results = []
        successful_service = None
        
        for service in test_services:
            try:
                start_time = time.time()
                
                # 直接连接测试（不使用代理）
                test_response = requests.get(service["url"], timeout=10)
                response_time = time.time() - start_time
                
                if test_response.status_code in [200, 301, 302]:
                    # 获取IP信息
                    try:
                        ip_response = requests.get(service["ip_url"], timeout=10)
                        if ip_response.status_code == 200:
                            ip_data = ip_response.json()
                            current_ip = ip_data.get("origin", "unknown")
                        else:
                            current_ip = "unknown"
                    except:
                        current_ip = "unknown"
                    
                    test_results.append({
                        "service": service["name"],
                        "status": "success",
                        "response_time": round(response_time, 2),
                        "ip": current_ip
                    })
                    
                    if not successful_service:
                        successful_service = {
                            "service": service["name"],
                            "ip": current_ip,
                            "response_time": response_time
                        }
                        
                else:
                    test_results.append({
                        "service": service["name"],
                        "status": "failed",
                        "status_code": test_response.status_code,
                        "response_time": round(response_time, 2)
                    })
                    
            except Exception as e:
                test_results.append({
                    "service": service["name"],
                    "status": "failed",
                    "error": str(e),
                    "response_time": 10.0
                })
        
        # 计算成功率
        successful_count = len([r for r in test_results if r["status"] == "success"])
        success_rate = (successful_count / len(test_results)) * 100
        
        if successful_service:
            logger.info(f"直接外网访问测试成功: {successful_service['service']}")
            return JsonResponse({
                "success": True,
                "message": f"直接外网访问成功 ({success_rate:.1f}% 成功率)",
                "ip": successful_service["ip"],
                "service": successful_service["service"],
                "response_time": successful_service["response_time"],
                "proxy_port": None,  # 无代理
                "test_results": test_results,
                "access_method": "direct"  # 标记为直接访问
            })
        else:
            logger.warning("直接外网访问测试失败")
            return JsonResponse({
                "success": False,
                "error": "直接外网访问失败",
                "test_results": test_results,
                "access_method": "direct"
            })
            
    except Exception as e:
        logger.error(f"直接外网访问测试异常: {e}")
        return JsonResponse({
            "success": False,
            "error": f"直接外网访问测试异常: {str(e)}",
            "access_method": "direct"
        })


@csrf_exempt
@require_http_methods(["POST"])
def clash_auto_setup_api(request):
    """自动安装和配置Clash API"""
    try:
        import platform
        import subprocess
        import os
        
        logger.info("开始自动安装Clash...")
        
        system = platform.system().lower()
        arch = platform.machine().lower()
        
        # 检测系统架构
        if "arm" in arch or "aarch" in arch:
            arch_name = "arm64"
        elif "x86_64" in arch or "amd64" in arch:
            arch_name = "amd64"
        else:
            arch_name = "amd64"  # 默认
        
        setup_result = {
            "system": f"{system} ({arch_name})",
            "steps": [],
            "success": False,
            "error": None
        }
        
        if system == "darwin":  # macOS
            setup_result["steps"].append("检测到macOS系统")
            
            # 检查是否已安装Homebrew
            try:
                subprocess.run(["brew", "--version"], check=True, capture_output=True)
                setup_result["steps"].append("✅ Homebrew已安装")
                
                # 尝试安装Clash
                try:
                    subprocess.run(["brew", "install", "clash"], check=True, capture_output=True)
                    setup_result["steps"].append("✅ Clash安装成功")
                    setup_result["success"] = True
                except subprocess.CalledProcessError as e:
                    setup_result["steps"].append(f"❌ Clash安装失败: {e}")
                    setup_result["error"] = "Homebrew安装Clash失败"
                    
            except subprocess.CalledProcessError:
                setup_result["steps"].append("❌ 未检测到Homebrew")
                setup_result["error"] = "请先安装Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                
        elif system == "linux":
            setup_result["steps"].append("检测到Linux系统")
            
            # 尝试使用包管理器安装
            try:
                # 尝试apt (Ubuntu/Debian)
                subprocess.run(["apt", "update"], check=True, capture_output=True)
                subprocess.run(["apt", "install", "-y", "clash"], check=True, capture_output=True)
                setup_result["steps"].append("✅ 通过apt安装Clash成功")
                setup_result["success"] = True
            except subprocess.CalledProcessError:
                try:
                    # 尝试yum (CentOS/RHEL)
                    subprocess.run(["yum", "install", "-y", "clash"], check=True, capture_output=True)
                    setup_result["steps"].append("✅ 通过yum安装Clash成功")
                    setup_result["success"] = True
                except subprocess.CalledProcessError:
                    # 手动下载安装
                    setup_result["steps"].append("包管理器安装失败，尝试手动下载...")
                    
                    try:
                        # 创建目录
                        os.makedirs("/opt/clash", exist_ok=True)
                        
                        # 下载Clash
                        download_url = f"https://github.com/Dreamacro/clash/releases/latest/download/clash-linux-{arch_name}.gz"
                        subprocess.run([
                            "wget", "-O", "/tmp/clash.gz", download_url
                        ], check=True, capture_output=True)
                        
                        # 解压
                        subprocess.run([
                            "gunzip", "/tmp/clash.gz"
                        ], check=True, capture_output=True)
                        
                        # 移动并设置权限
                        subprocess.run([
                            "mv", "/tmp/clash", "/opt/clash/clash"
                        ], check=True, capture_output=True)
                        
                        subprocess.run([
                            "chmod", "+x", "/opt/clash/clash"
                        ], check=True, capture_output=True)
                        
                        setup_result["steps"].append("✅ 手动下载安装Clash成功")
                        setup_result["success"] = True
                        
                    except subprocess.CalledProcessError as e:
                        setup_result["steps"].append(f"❌ 手动安装失败: {e}")
                        setup_result["error"] = "所有安装方法都失败了"
                        
        else:
            setup_result["error"] = f"不支持的系统: {system}"
            
        return JsonResponse({
            "success": setup_result["success"],
            "data": setup_result
        })
        
    except Exception as e:
        logger.error(f"自动安装Clash失败: {e}")
        return JsonResponse({
            "success": False,
            "error": f"安装失败: {str(e)}"
        })


def find_available_proxy_port():
    """动态检测可用的代理端口 - 增强版"""
    import socket
    import requests
    
    # 扩展的代理端口列表，包含更多常见代理端口
    possible_ports = [
        # Clash默认端口
        7890, 7891, 7892, 7893,
        # V2Ray/V2RayN端口
        1080, 1081, 1082, 1083, 1084, 1085, 1086, 1087, 1088, 1089,
        # Shadowsocks端口
        8388, 8389, 8390, 8391, 8392,
        # HTTP代理端口
        8080, 8081, 8082, 8083, 8084, 8085, 8086, 8087, 8088, 8089,
        # SOCKS代理端口
        1080, 1081, 1082, 1083, 1084, 1085, 1086, 1087, 1088, 1089,
        # 其他常见端口
        3128, 8118, 8123, 8888, 9999,
        # 自定义端口范围
        10080, 10081, 10082, 10083, 10084, 10085, 10086, 10087, 10088, 10089,
        20080, 20081, 20082, 20083, 20084, 20085, 20086, 20087, 20088, 20089,
    ]
    
    # 按优先级排序，优先检测常用端口
    priority_ports = [7890, 7891, 1080, 8080, 8388, 3128]
    other_ports = [port for port in possible_ports if port not in priority_ports]
    sorted_ports = priority_ports + other_ports
    
    logger.info(f"开始检测代理端口，共 {len(sorted_ports)} 个端口")
    
    for i, port in enumerate(sorted_ports):
        try:
            logger.debug(f"检测端口 {port} ({i+1}/{len(sorted_ports)})")
            
            # 检查端口是否在监听
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)  # 增加超时时间
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:  # 端口在监听
                logger.info(f"端口 {port} 正在监听，开始测试代理功能...")
                
                # 测试HTTP代理
                try:
                    proxies = {
                        "http": f"http://127.0.0.1:{port}",
                        "https": f"http://127.0.0.1:{port}"
                    }
                    
                    # 使用多个测试URL提高成功率
                    test_urls = [
                        "http://httpbin.org/get",
                        "http://www.google.com/favicon.ico",
                        "http://www.baidu.com/favicon.ico"
                    ]
                    
                    for test_url in test_urls:
                        try:
                            response = requests.get(test_url, proxies=proxies, timeout=8)
                            if response.status_code in [200, 301, 302]:  # 接受重定向
                                logger.info(f"✅ 端口 {port} 代理测试成功 (URL: {test_url})")
                                return port
                        except Exception as e:
                            logger.debug(f"端口 {port} 测试URL {test_url} 失败: {e}")
                            continue
                    
                    # 如果HTTP代理失败，尝试SOCKS代理
                    try:
                        socks_proxies = {
                            "http": f"socks5://127.0.0.1:{port}",
                            "https": f"socks5://127.0.0.1:{port}"
                        }
                        
                        response = requests.get("http://httpbin.org/get", proxies=socks_proxies, timeout=8)
                        if response.status_code == 200:
                            logger.info(f"✅ 端口 {port} SOCKS代理测试成功")
                            return port
                    except Exception as e:
                        logger.debug(f"端口 {port} SOCKS代理测试失败: {e}")
                        
                except Exception as e:
                    logger.debug(f"端口 {port} 代理测试失败: {e}")
                    continue
            else:
                logger.debug(f"端口 {port} 未在监听")
                    
        except Exception as e:
            logger.debug(f"端口 {port} 检测异常: {e}")
            continue
    
    logger.warning("❌ 未找到可用的代理端口")
    return None


@csrf_exempt
@require_http_methods(["POST"])
def clash_disable_proxy_api(request):
    """禁用系统代理API"""
    try:
        # 禁用系统代理
        success, message = disable_system_proxy()
        
        if success:
            return JsonResponse({
                "success": True,
                "message": message,
                "proxy_configured": False
            })
        else:
            return JsonResponse({
                "success": False,
                "error": message,
                "proxy_configured": True
            })
            
    except Exception as e:
        logger.error(f"禁用系统代理失败: {e}")
        return JsonResponse({"success": False, "error": f"禁用失败: {str(e)}"})


def configure_system_proxy(http_port, socks_port):
    """配置系统代理"""
    try:
        import platform
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            return configure_macos_proxy(http_port, socks_port)
        elif system == "linux":
            return configure_linux_proxy(http_port, socks_port)
        elif system == "windows":
            return configure_windows_proxy(http_port, socks_port)
        else:
            return False, f"不支持的操作系统: {system}"
            
    except Exception as e:
        logger.error(f"配置系统代理失败: {e}")
        return False, f"配置失败: {str(e)}"


def configure_macos_proxy(http_port, socks_port):
    """配置macOS系统代理"""
    try:
        import subprocess
        
        # 设置HTTP代理
        subprocess.run([
            "networksetup", "-setwebproxy", "Wi-Fi", "127.0.0.1", str(http_port)
        ], check=True, capture_output=True)
        
        # 设置HTTPS代理
        subprocess.run([
            "networksetup", "-setsecurewebproxy", "Wi-Fi", "127.0.0.1", str(http_port)
        ], check=True, capture_output=True)
        
        # 设置SOCKS代理
        subprocess.run([
            "networksetup", "-setsocksfirewallproxy", "Wi-Fi", "127.0.0.1", str(socks_port)
        ], check=True, capture_output=True)
        
        logger.info(f"macOS代理配置成功: HTTP={http_port}, SOCKS={socks_port}")
        return True, "macOS系统代理配置成功"
        
    except subprocess.CalledProcessError as e:
        logger.error(f"macOS代理配置失败: {e}")
        return False, f"macOS代理配置失败: {e.stderr.decode() if e.stderr else str(e)}"
    except Exception as e:
        logger.error(f"macOS代理配置异常: {e}")
        return False, f"macOS代理配置异常: {str(e)}"


def configure_linux_proxy(http_port, socks_port):
    """配置Linux系统代理"""
    try:
        import subprocess
        import os
        
        # 设置环境变量
        proxy_env = {
            "http_proxy": f"http://127.0.0.1:{http_port}",
            "https_proxy": f"http://127.0.0.1:{http_port}",
            "HTTP_PROXY": f"http://127.0.0.1:{http_port}",
            "HTTPS_PROXY": f"http://127.0.0.1:{http_port}",
            "socks_proxy": f"socks5://127.0.0.1:{socks_port}",
            "SOCKS_PROXY": f"socks5://127.0.0.1:{socks_port}"
        }
        
        # 更新当前进程环境变量
        os.environ.update(proxy_env)
        
        logger.info(f"Linux代理配置成功: HTTP={http_port}, SOCKS={socks_port}")
        return True, "Linux系统代理配置成功"
        
    except Exception as e:
        logger.error(f"Linux代理配置失败: {e}")
        return False, f"Linux代理配置失败: {str(e)}"


def configure_windows_proxy(http_port, socks_port):
    """配置Windows系统代理"""
    try:
        import subprocess
        
        # 使用netsh命令设置代理
        proxy_url = f"127.0.0.1:{http_port}"
        
        # 设置代理
        subprocess.run([
            "netsh", "winhttp", "set", "proxy", proxy_url
        ], check=True, capture_output=True)
        
        logger.info(f"Windows代理配置成功: HTTP={http_port}")
        return True, "Windows系统代理配置成功"
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Windows代理配置失败: {e}")
        return False, f"Windows代理配置失败: {e.stderr.decode() if e.stderr else str(e)}"
    except Exception as e:
        logger.error(f"Windows代理配置异常: {e}")
        return False, f"Windows代理配置异常: {str(e)}"


def disable_system_proxy():
    """禁用系统代理"""
    try:
        import platform
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            return disable_macos_proxy()
        elif system == "linux":
            return disable_linux_proxy()
        elif system == "windows":
            return disable_windows_proxy()
        else:
            return False, f"不支持的操作系统: {system}"
            
    except Exception as e:
        logger.error(f"禁用系统代理失败: {e}")
        return False, f"禁用失败: {str(e)}"


def disable_macos_proxy():
    """禁用macOS系统代理"""
    try:
        import subprocess
        
        # 禁用HTTP代理
        subprocess.run([
            "networksetup", "-setwebproxystate", "Wi-Fi", "off"
        ], check=True, capture_output=True)
        
        # 禁用HTTPS代理
        subprocess.run([
            "networksetup", "-setsecurewebproxystate", "Wi-Fi", "off"
        ], check=True, capture_output=True)
        
        # 禁用SOCKS代理
        subprocess.run([
            "networksetup", "-setsocksfirewallproxystate", "Wi-Fi", "off"
        ], check=True, capture_output=True)
        
        logger.info("macOS代理已禁用")
        return True, "macOS系统代理已禁用"
        
    except subprocess.CalledProcessError as e:
        logger.error(f"禁用macOS代理失败: {e}")
        return False, f"禁用macOS代理失败: {e.stderr.decode() if e.stderr else str(e)}"
    except Exception as e:
        logger.error(f"禁用macOS代理异常: {e}")
        return False, f"禁用macOS代理异常: {str(e)}"


def disable_linux_proxy():
    """禁用Linux系统代理"""
    try:
        import os
        
        # 清除环境变量
        proxy_vars = [
            "http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
            "socks_proxy", "SOCKS_PROXY"
        ]
        
        for var in proxy_vars:
            if var in os.environ:
                del os.environ[var]
        
        logger.info("Linux代理已禁用")
        return True, "Linux系统代理已禁用"
        
    except Exception as e:
        logger.error(f"禁用Linux代理失败: {e}")
        return False, f"禁用Linux代理失败: {str(e)}"


def disable_windows_proxy():
    """禁用Windows系统代理"""
    try:
        import subprocess
        
        # 禁用代理
        subprocess.run([
            "netsh", "winhttp", "reset", "proxy"
        ], check=True, capture_output=True)
        
        logger.info("Windows代理已禁用")
        return True, "Windows系统代理已禁用"
        
    except subprocess.CalledProcessError as e:
        logger.error(f"禁用Windows代理失败: {e}")
        return False, f"禁用Windows代理失败: {e.stderr.decode() if e.stderr else str(e)}"
    except Exception as e:
        logger.error(f"禁用Windows代理异常: {e}")
        return False, f"禁用Windows代理异常: {str(e)}"


@csrf_exempt
@require_http_methods(["GET"])
def clash_proxy_health_api(request):
    """代理健康监控API"""
    try:
        import time
        import requests
        
        # 获取系统状态
        status = clash_service.get_status()
        
        # 检测可用代理端口
        available_port = find_available_proxy_port()
        
        health_data = {
            "timestamp": int(time.time()),
            "clash_service": {
                "is_running": status.get("is_running", False),
                "service_type": status.get("service_type", "Unknown"),
                "uptime": status.get("uptime", 0),
                "http_port": status.get("http_port", 7890),
                "socks_port": status.get("socks_port", 7891),
            },
            "proxy_detection": {
                "available_port": available_port,
                "port_scan_completed": True,
            },
            "connectivity_tests": [],
            "overall_health": "unknown"
        }
        
        if available_port:
            # 执行连接测试
            proxies = {
                "http": f"http://127.0.0.1:{available_port}",
                "https": f"http://127.0.0.1:{available_port}"
            }
            
            test_services = [
                {"name": "本地代理", "url": f"http://127.0.0.1:{available_port}", "type": "local"},
                {"name": "httpbin.org", "url": "http://httpbin.org/get", "type": "external"},
                {"name": "Google", "url": "http://www.google.com/favicon.ico", "type": "external"},
                {"name": "Cloudflare", "url": "http://1.1.1.1", "type": "external"},
            ]
            
            successful_tests = 0
            
            for service in test_services:
                try:
                    start_time = time.time()
                    
                    if service["type"] == "local":
                        # 本地代理测试
                        response = requests.get(service["url"], timeout=5)
                    else:
                        # 外网代理测试
                        response = requests.get(service["url"], proxies=proxies, timeout=10)
                    
                    response_time = time.time() - start_time
                    
                    if response.status_code in [200, 301, 302]:
                        health_data["connectivity_tests"].append({
                            "service": service["name"],
                            "status": "healthy",
                            "response_time": round(response_time, 2),
                            "status_code": response.status_code
                        })
                        successful_tests += 1
                    else:
                        health_data["connectivity_tests"].append({
                            "service": service["name"],
                            "status": "unhealthy",
                            "response_time": round(response_time, 2),
                            "status_code": response.status_code
                        })
                        
                except Exception as e:
                    health_data["connectivity_tests"].append({
                        "service": service["name"],
                        "status": "error",
                        "error": str(e)
                    })
            
            # 计算整体健康状态
            total_tests = len(test_services)
            if successful_tests == total_tests:
                health_data["overall_health"] = "excellent"
            elif successful_tests >= total_tests * 0.7:
                health_data["overall_health"] = "good"
            elif successful_tests >= total_tests * 0.3:
                health_data["overall_health"] = "fair"
            else:
                health_data["overall_health"] = "poor"
        else:
            health_data["overall_health"] = "no_proxy"
        
        return JsonResponse({
            "success": True,
            "data": health_data
        })
        
    except Exception as e:
        logger.error(f"代理健康监控失败: {e}")
        return JsonResponse({
            "success": False,
            "error": f"健康监控失败: {str(e)}"
        })


def _get_manual_install_guide():
    """获取详细的手动安装指南"""
    system = platform.system().lower()
    arch = platform.machine().lower()

    guide = {"system_info": f"{system} ({arch})", "steps": [], "troubleshooting": []}

    if system == "darwin":  # macOS
        guide["steps"] = [
            "1. 打开终端 (Terminal)",
            "2. 检查是否已安装Homebrew: brew --version",
            '3. 如果没有Homebrew，先安装: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
            "4. 安装Clash: brew install clash",
            "5. 验证安装: clash --version",
        ]
        guide["troubleshooting"] = [
            "如果Homebrew安装失败，请检查网络连接",
            "如果权限不足，使用sudo运行命令",
            "如果仍然失败，尝试下载ClashX图形界面版本",
        ]
    elif system == "linux":
        guide["steps"] = [
            "1. 打开终端",
            "2. 更新包管理器: sudo apt update (Ubuntu/Debian) 或 sudo yum update (CentOS/RHEL)",
            "3. 安装Clash: sudo apt install clash (Ubuntu/Debian) 或 sudo yum install clash (CentOS/RHEL)",
            "4. 验证安装: clash --version",
        ]
        guide["troubleshooting"] = ["如果包管理器中没有clash，尝试手动下载", "确保有sudo权限", "检查网络连接是否正常"]
    elif system == "windows":
        guide["steps"] = [
            "1. 以管理员身份打开PowerShell",
            "2. 检查是否已安装Chocolatey: choco --version",
            "3. 如果没有Chocolatey，先安装 (见上面的命令)",
            "4. 安装Clash: choco install clash",
            "5. 验证安装: clash --version",
        ]
        guide["troubleshooting"] = [
            "如果PowerShell执行策略限制，运行: Set-ExecutionPolicy RemoteSigned",
            "确保以管理员身份运行",
            "如果仍然失败，下载Clash for Windows图形界面版本",
        ]
    else:
        guide["steps"] = [
            "1. 访问 https://github.com/Dreamacro/clash/releases/latest",
            "2. 下载适合您系统的版本",
            "3. 解压文件并设置执行权限",
            "4. 将可执行文件放到系统PATH目录中",
        ]
        guide["troubleshooting"] = ["确保下载的是正确的系统架构版本", "检查文件权限设置", "确保可执行文件在系统PATH中"]

    return guide
