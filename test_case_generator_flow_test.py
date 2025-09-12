#!/usr/bin/env python3
"""
测试用例生成器流程测试脚本
测试从创建任务到下载文件的完整流程
"""

import json
import time
import requests
from datetime import datetime

# 服务器配置
BASE_URL = "https://shenyiqing.xin"
TEST_CASE_URL = f"{BASE_URL}/tools/test_case_generator/"
TASK_MANAGER_URL = f"{BASE_URL}/tools/task_manager/"

# API端点
CREATE_TASK_API = f"{BASE_URL}/tools/api/async/generate-testcases/"
TASK_STATUS_API = f"{BASE_URL}/tools/api/async/task/"
TASK_LIST_API = f"{BASE_URL}/tools/api/async/tasks/"
DOWNLOAD_API = f"{BASE_URL}/tools/api/async/task/"

def test_create_task():
    """测试创建任务"""
    print("🚀 开始测试创建任务...")
    
    # 测试数据
    test_data = {
        "requirement": "用户登录功能，支持手机号和邮箱登录，包含记住密码选项，需要验证码验证",
        "prompt": "根据{requirement}生成详细的测试用例，包含功能测试、界面测试、性能测试、安全测试和兼容性测试"
    }
    
    try:
        response = requests.post(CREATE_TASK_API, json=test_data, timeout=30)
        print(f"创建任务响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                task_id = result.get('task_id')
                print(f"✅ 任务创建成功! 任务ID: {task_id}")
                return task_id
            else:
                print(f"❌ 任务创建失败: {result.get('error')}")
                return None
        else:
            print(f"❌ 请求失败: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 创建任务异常: {e}")
        return None

def test_task_status(task_id):
    """测试查询任务状态"""
    print(f"📊 开始查询任务状态: {task_id}")
    
    try:
        response = requests.get(f"{TASK_STATUS_API}{task_id}/", timeout=30)
        print(f"查询状态响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                status = result.get('status')
                progress = result.get('progress', 0)
                current_step = result.get('current_step', '未知')
                print(f"✅ 任务状态: {status}, 进度: {progress}%, 当前步骤: {current_step}")
                return result
            else:
                print(f"❌ 查询状态失败: {result.get('error')}")
                return None
        else:
            print(f"❌ 请求失败: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 查询状态异常: {e}")
        return None

def test_task_list():
    """测试获取任务列表"""
    print("📋 开始获取任务列表...")
    
    try:
        response = requests.get(TASK_LIST_API, timeout=30)
        print(f"任务列表响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                tasks = result.get('tasks', [])
                print(f"✅ 获取到 {len(tasks)} 个任务")
                for task in tasks[:3]:  # 只显示前3个任务
                    print(f"  - 任务ID: {task.get('id', '')[:8]}..., 状态: {task.get('status')}, 进度: {task.get('progress', 0)}%")
                return tasks
            else:
                print(f"❌ 获取任务列表失败: {result.get('error')}")
                return []
        else:
            print(f"❌ 请求失败: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ 获取任务列表异常: {e}")
        return []

def test_download_task(task_id, format_type='txt'):
    """测试下载任务结果"""
    print(f"📥 开始下载任务结果: {task_id}, 格式: {format_type}")
    
    try:
        download_url = f"{DOWNLOAD_API}{task_id}/download/{format_type}/"
        response = requests.get(download_url, timeout=30)
        print(f"下载响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            # 检查是否是文件下载
            content_type = response.headers.get('content-type', '')
            if 'text/plain' in content_type or 'application/octet-stream' in content_type:
                filename = f"test_result_{task_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✅ 文件下载成功: {filename}")
                return filename
            else:
                print(f"❌ 响应不是文件格式: {content_type}")
                print(f"响应内容: {response.text[:200]}...")
                return None
        else:
            print(f"❌ 下载失败: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 下载异常: {e}")
        return None

def wait_for_task_completion(task_id, max_wait_time=300):
    """等待任务完成"""
    print(f"⏳ 等待任务完成: {task_id} (最多等待 {max_wait_time} 秒)")
    
    start_time = time.time()
    while time.time() - start_time < max_wait_time:
        result = test_task_status(task_id)
        if result:
            status = result.get('status')
            progress = result.get('progress', 0)
            current_step = result.get('current_step', '未知')
            
            print(f"  状态: {status}, 进度: {progress}%, 步骤: {current_step}")
            
            if status == 'completed':
                print("✅ 任务完成!")
                return True
            elif status == 'failed':
                print(f"❌ 任务失败: {result.get('error', '未知错误')}")
                return False
            elif status in ['pending', 'running']:
                time.sleep(5)  # 等待5秒后再次检查
            else:
                print(f"❓ 未知状态: {status}")
                return False
        else:
            print("❌ 无法获取任务状态")
            return False
    
    print("⏰ 等待超时")
    return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 测试用例生成器流程测试")
    print("=" * 60)
    
    # 1. 测试创建任务
    task_id = test_create_task()
    if not task_id:
        print("❌ 创建任务失败，测试终止")
        return
    
    print("\n" + "-" * 40)
    
    # 2. 等待任务完成
    if wait_for_task_completion(task_id):
        print("\n" + "-" * 40)
        
        # 3. 测试获取任务列表
        test_task_list()
        
        print("\n" + "-" * 40)
        
        # 4. 测试下载不同格式的文件
        formats = ['txt', 'xmind', 'feishu']
        for format_type in formats:
            print(f"\n测试下载 {format_type.upper()} 格式...")
            filename = test_download_task(task_id, format_type)
            if filename:
                print(f"✅ {format_type.upper()} 格式下载成功: {filename}")
            else:
                print(f"❌ {format_type.upper()} 格式下载失败")
    
    print("\n" + "=" * 60)
    print("🎉 测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()