#!/usr/bin/env python3

# Webhook触发部署方法
# 使用方法: python3 deploy-webhook.py

import os
import json
import requests
import subprocess
import time
from flask import Flask, request, jsonify
from threading import Thread
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 服务器配置
SERVER_CONFIG = {
    'host': '47.103.143.152',
    'username': 'root',
    'deploy_path': '/root/modeshift_django',
    'webhook_secret': 'your-webhook-secret-key'
}

class WebhookDeployer:
    def __init__(self):
        self.deploying = False
        
    def deploy_via_ssh(self, branch='main'):
        """通过SSH进行部署"""
        logger.info(f"开始SSH部署，分支: {branch}")
        
        try:
            # SSH命令
            ssh_cmd = f"""
            cd {SERVER_CONFIG['deploy_path']} &&
            git fetch origin &&
            git checkout {branch} &&
            git pull origin {branch} &&
            venv/bin/python manage.py collectstatic --noinput &&
            venv/bin/python manage.py migrate --noinput &&
            pkill -TERM -f gunicorn || true &&
            sleep 3 &&
            nohup venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 wsgi:application --daemon &&
            sudo nginx -s reload &&
            echo '✅ SSH部署完成'
            """
            
            # 执行SSH命令
            result = subprocess.run([
                'ssh', '-o', 'StrictHostKeyChecking=no',
                f"{SERVER_CONFIG['username']}@{SERVER_CONFIG['host']}",
                ssh_cmd
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("SSH部署成功")
                return True, result.stdout
            else:
                logger.error(f"SSH部署失败: {result.stderr}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            logger.error("SSH部署超时")
            return False, "部署超时"
        except Exception as e:
            logger.error(f"SSH部署异常: {e}")
            return False, str(e)
    
    def deploy_via_curl(self, branch='main'):
        """通过curl API进行部署"""
        logger.info(f"开始API部署，分支: {branch}")
        
        try:
            # 构建API请求
            api_url = f"https://{SERVER_CONFIG['host']}/api/deploy/"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {SERVER_CONFIG['webhook_secret']}"
            }
            data = {
                'branch': branch,
                'action': 'deploy'
            }
            
            # 发送请求
            response = requests.post(api_url, json=data, headers=headers, timeout=60)
            
            if response.status_code == 200:
                logger.info("API部署成功")
                return True, response.json()
            else:
                logger.error(f"API部署失败: {response.text}")
                return False, response.text
                
        except requests.RequestException as e:
            logger.error(f"API部署异常: {e}")
            return False, str(e)
    
    def deploy_via_github_actions(self, branch='main'):
        """通过GitHub Actions进行部署"""
        logger.info(f"触发GitHub Actions部署，分支: {branch}")
        
        try:
            # GitHub API URL
            api_url = "https://api.github.com/repos/shinytsing/modeshift_django/actions/workflows/ultimate-deploy.yml/dispatches"
            headers = {
                'Authorization': f"token {os.getenv('GITHUB_TOKEN')}",
                'Accept': 'application/vnd.github.v3+json'
            }
            data = {
                'ref': branch
            }
            
            # 发送请求
            response = requests.post(api_url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 204:
                logger.info("GitHub Actions部署触发成功")
                return True, "部署已触发"
            else:
                logger.error(f"GitHub Actions触发失败: {response.text}")
                return False, response.text
                
        except requests.RequestException as e:
            logger.error(f"GitHub Actions触发异常: {e}")
            return False, str(e)

# 创建部署器实例
deployer = WebhookDeployer()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook接收端点"""
    try:
        # 验证签名
        signature = request.headers.get('X-Hub-Signature-256')
        if not signature:
            return jsonify({'error': '缺少签名'}), 401
        
        # 解析请求数据
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的JSON数据'}), 400
        
        # 检查事件类型
        event_type = request.headers.get('X-GitHub-Event')
        if event_type == 'push':
            branch = data.get('ref', '').replace('refs/heads/', '')
            if branch == 'main':
                # 异步执行部署
                if not deployer.deploying:
                    deployer.deploying = True
                    Thread(target=execute_deploy, args=(branch,)).start()
                    return jsonify({'message': '部署已开始'}), 200
                else:
                    return jsonify({'message': '部署正在进行中'}), 202
        
        return jsonify({'message': '事件已接收'}), 200
        
    except Exception as e:
        logger.error(f"Webhook处理异常: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/deploy', methods=['POST'])
def manual_deploy():
    """手动部署端点"""
    try:
        data = request.get_json()
        method = data.get('method', 'ssh')
        branch = data.get('branch', 'main')
        
        if deployer.deploying:
            return jsonify({'error': '部署正在进行中'}), 409
        
        # 执行部署
        deployer.deploying = True
        success, message = execute_deploy_method(method, branch)
        deployer.deploying = False
        
        return jsonify({
            'success': success,
            'message': message
        }), 200 if success else 500
        
    except Exception as e:
        deployer.deploying = False
        logger.error(f"手动部署异常: {e}")
        return jsonify({'error': str(e)}), 500

def execute_deploy(branch):
    """执行部署"""
    try:
        success, message = deployer.deploy_via_ssh(branch)
        logger.info(f"部署结果: {success}, 消息: {message}")
    except Exception as e:
        logger.error(f"部署异常: {e}")
    finally:
        deployer.deploying = False

def execute_deploy_method(method, branch):
    """根据方法执行部署"""
    if method == 'ssh':
        return deployer.deploy_via_ssh(branch)
    elif method == 'api':
        return deployer.deploy_via_curl(branch)
    elif method == 'github':
        return deployer.deploy_via_github_actions(branch)
    else:
        return False, f"不支持的部署方法: {method}"

@app.route('/status', methods=['GET'])
def status():
    """部署状态检查"""
    return jsonify({
        'deploying': deployer.deploying,
        'timestamp': time.time()
    })

def main():
    """主函数"""
    print("🚀 Webhook部署服务启动")
    print("=====================")
    print("")
    print("📋 可用的部署方法:")
    print("1. SSH直接部署")
    print("2. API调用部署")
    print("3. GitHub Actions触发")
    print("")
    print("🌐 Webhook端点:")
    print("- POST /webhook - GitHub Webhook")
    print("- POST /deploy - 手动部署")
    print("- GET /status - 状态检查")
    print("")
    print("🔧 使用方法:")
    print("1. 启动服务: python3 deploy-webhook.py")
    print("2. 配置GitHub Webhook: http://your-server:5000/webhook")
    print("3. 手动部署: curl -X POST http://localhost:5000/deploy -H 'Content-Type: application/json' -d '{\"method\":\"ssh\",\"branch\":\"main\"}'")
    print("")
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()
