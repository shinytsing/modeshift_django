#!/usr/bin/env python3
"""
CI/CD部署监控脚本
实时监控GitHub Actions和部署状态
"""

import requests
import time
import json
from datetime import datetime


def get_github_actions_status(repo_owner, repo_name, token=None):
    """获取GitHub Actions运行状态"""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/runs"
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    if token:
        headers["Authorization"] = f"token {token}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ 获取GitHub Actions状态失败: {e}")
        return None


def check_server_health(server_url):
    """检查服务器健康状态"""
    health_endpoints = [
        f"{server_url}/health/",
        f"{server_url}/",
        f"{server_url}:8000/health/",
        f"{server_url}:8000/"
    ]
    
    for endpoint in health_endpoints:
        try:
            response = requests.get(endpoint, timeout=10)
            if response.status_code == 200:
                return True, endpoint
        except requests.RequestException:
            continue
    
    return False, None


def format_status(status):
    """格式化状态显示"""
    status_icons = {
        "completed": "✅",
        "in_progress": "🔄", 
        "queued": "⏳",
        "failed": "❌",
        "cancelled": "🚫",
        "success": "✅",
        "failure": "❌"
    }
    return status_icons.get(status, "❓")


def monitor_deployment():
    """监控部署过程"""
    repo_owner = "shinytsing"
    repo_name = "modeshift_django"
    server_url = "http://47.103.143.152"
    
    print("🚀 开始监控CI/CD部署过程...")
    print("=" * 60)
    print(f"📊 仓库: {repo_owner}/{repo_name}")
    print(f"🌐 服务器: {server_url}")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 检查GitHub Actions状态
    print("\n🔍 检查GitHub Actions状态...")
    actions_data = get_github_actions_status(repo_owner, repo_name)
    
    if actions_data and "workflow_runs" in actions_data:
        latest_run = actions_data["workflow_runs"][0]
        status = latest_run["status"]
        conclusion = latest_run.get("conclusion", "unknown")
        
        print(f"📋 最新运行: {latest_run['name']}")
        print(f"🆔 运行ID: {latest_run['id']}")
        print(f"📅 创建时间: {latest_run['created_at']}")
        print(f"🔄 状态: {format_status(status)} {status}")
        print(f"📊 结论: {format_status(conclusion)} {conclusion}")
        print(f"🔗 链接: {latest_run['html_url']}")
        
        # 检查各个作业状态
        if "jobs_url" in latest_run:
            try:
                jobs_response = requests.get(latest_run["jobs_url"])
                jobs_data = jobs_response.json()
                
                print("\n📋 作业状态:")
                for job in jobs_data.get("jobs", []):
                    job_status = job["status"]
                    job_conclusion = job.get("conclusion", "unknown")
                    print(f"  - {job['name']}: {format_status(job_status)} {job_status} ({format_status(job_conclusion)} {job_conclusion})")
            except Exception as e:
                print("  ⚠️ 无法获取作业详情")
    else:
        print("❌ 无法获取GitHub Actions状态")
    
    # 检查服务器健康状态
    print(f"\n🏥 检查服务器健康状态...")
    is_healthy, working_endpoint = check_server_health(server_url)
    
    if is_healthy:
        print(f"✅ 服务器健康检查通过: {working_endpoint}")
    else:
        print(f"❌ 服务器健康检查失败")
        print(f"   尝试的端点:")
        for endpoint in [f"{server_url}/health/", f"{server_url}/", f"{server_url}:8000/health/", f"{server_url}:8000/"]:
            print(f"   - {endpoint}")
    
    print("\n" + "=" * 60)
    print("📋 监控总结:")
    print(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if actions_data and "workflow_runs" in actions_data:
        latest_run = actions_data["workflow_runs"][0]
        if latest_run["status"] == "completed" and latest_run.get("conclusion") == "success":
            print("🎉 CI/CD流程成功完成！")
        elif latest_run["status"] == "completed" and latest_run.get("conclusion") == "failure":
            print("❌ CI/CD流程失败，请检查日志")
        elif latest_run["status"] == "in_progress":
            print("🔄 CI/CD流程正在进行中...")
        else:
            print(f"📊 CI/CD状态: {latest_run['status']}")
    
    if is_healthy:
        print("✅ 服务器运行正常")
    else:
        print("⚠️ 服务器可能存在问题")
    
    print("\n🔗 有用的链接:")
    print(f"📊 GitHub Actions: https://github.com/{repo_owner}/{repo_name}/actions")
    print(f"🌐 生产环境: {server_url}")
    print(f"🏥 健康检查: {server_url}/health/")


def main():
    """主函数"""
    try:
        monitor_deployment()
    except KeyboardInterrupt:
        print("\n\n⏹️ 监控已停止")
    except Exception as e:
        print(f"\n❌ 监控过程中出错: {e}")

if __name__ == "__main__":
    main()
