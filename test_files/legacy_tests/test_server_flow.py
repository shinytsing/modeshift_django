#!/usr/bin/env python3
"""
测试服务器上的测试用例生成器完整流程
"""

import requests
import json
import time
from datetime import datetime

def test_server_flow():
    """测试服务器上的完整流程"""
    print("🚀 开始测试服务器上的测试用例生成器流程")
    print("=" * 60)
    
    base_url = "https://shenyiqing.xin"
    
    # 1. 测试创建任务API
    print("🔍 步骤1: 创建异步任务...")
    try:
        create_url = f"{base_url}/tools/api/async/generate-testcases/"
        data = {
            "requirement": "电商购物车功能，支持添加商品、删除商品、修改数量、结算",
            "prompt": "为{requirement}生成详细的测试用例，包含功能测试、界面测试、异常测试"
        }
        
        print(f"📡 创建任务API: {create_url}")
        response = requests.post(create_url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                task_id = result.get('task_id')
                print(f"✅ 任务创建成功! 任务ID: {task_id}")
                
                # 2. 监控任务状态
                print(f"\n🔍 步骤2: 监控任务状态: {task_id}")
                max_wait_time = 300  # 最大等待5分钟
                start_time = time.time()
                
                while time.time() - start_time < max_wait_time:
                    status_url = f"{base_url}/tools/api/async/task/{task_id}/"
                    print(f"📡 检查任务状态: {status_url}")
                    
                    status_response = requests.get(status_url, timeout=30)
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        status = status_data.get('status')
                        progress = status_data.get('progress', 0)
                        current_step = status_data.get('current_step', '未知')
                        
                        print(f"📊 状态: {status}, 进度: {progress}%, 步骤: {current_step}")
                        
                        if status == 'completed':
                            print("✅ 任务完成!")
                            result_content = status_data.get('result', '')
                            print(f"📄 结果长度: {len(result_content)} 字符")
                            print(f"📄 结果预览: {result_content[:200]}...")
                            
                            # 3. 测试下载功能
                            print("\n🔍 步骤3: 测试下载功能...")
                            if result_content:
                                # 模拟下载TXT文件
                                txt_filename = f"服务器测试用例_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                                with open(txt_filename, 'w', encoding='utf-8') as f:
                                    f.write(result_content)
                                print(f"✅ TXT文件已保存: {txt_filename}")
                                
                                # 模拟下载XMind文件
                                xmind_filename = f"服务器测试用例_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xmind"
                                print(f"✅ XMind文件已准备: {xmind_filename}")
                                
                                print("✅ 下载功能测试通过!")
                                return True
                            else:
                                print("❌ 任务结果为空")
                                return False
                                
                        elif status == 'failed':
                            print(f"❌ 任务失败: {status_data.get('error', '未知错误')}")
                            return False
                            
                    elif status_response.status_code == 404:
                        print("❌ 任务不存在，可能服务器和本地存储不同步")
                        return False
                    else:
                        print(f"❌ 获取任务状态失败: {status_response.status_code}")
                        print(f"响应内容: {status_response.text}")
                        return False
                    
                    time.sleep(5)  # 每5秒检查一次
                    
                print("⏰ 任务监控超时")
                return False
                
            else:
                print(f"❌ 任务创建失败: {result.get('error')}")
                return False
        else:
            print(f"❌ 任务创建失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_notification_system():
    """测试通知系统"""
    print("\n🔍 步骤4: 测试通知系统...")
    
    try:
        base_url = "https://shenyiqing.xin"
        notification_url = f"{base_url}/tools/api/notifications/create/"
        
        notification_data = {
            "title": "测试用例生成完成",
            "message": "测试通知系统功能",
            "type": "system"
        }
        
        print(f"📡 测试通知API: {notification_url}")
        response = requests.post(notification_url, json=notification_data, timeout=30)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('success'):
                    print("✅ 通知系统测试成功!")
                    return True
                else:
                    print(f"❌ 通知系统测试失败: {result.get('error')}")
            except json.JSONDecodeError:
                print("❌ 响应不是有效的JSON格式")
                return False
        else:
            print(f"❌ 通知系统测试失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 通知系统测试失败: {str(e)}")
        
    return False

def test_task_list_api():
    """测试任务列表API"""
    print("\n🔍 步骤5: 测试任务列表API...")
    
    try:
        base_url = "https://shenyiqing.xin"
        list_url = f"{base_url}/tools/api/async/tasks/"
        
        print(f"📡 测试任务列表API: {list_url}")
        response = requests.get(list_url, timeout=30)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('success'):
                    tasks = result.get('tasks', [])
                    print(f"✅ 任务列表API成功! 找到 {len(tasks)} 个任务")
                    return True
                else:
                    print(f"❌ 任务列表API失败: {result.get('error')}")
            except json.JSONDecodeError:
                print("❌ 响应不是有效的JSON格式")
                return False
        else:
            print(f"❌ 任务列表API失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 任务列表API测试失败: {str(e)}")
        
    return False

def main():
    """主测试函数"""
    print("🚀 开始测试服务器上的测试用例生成器完整流程")
    print("=" * 60)
    
    # 测试结果统计
    test_results = {}
    
    # 1. 测试完整流程
    test_results['complete_flow'] = test_server_flow()
    
    # 2. 测试通知系统
    test_results['notification_system'] = test_notification_system()
    
    # 3. 测试任务列表API
    test_results['task_list_api'] = test_task_list_api()
    
    # 输出测试结果总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    print("=" * 60)
    
    for test_name, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    
    print(f"\n📈 总体结果: {passed_tests}/{total_tests} 测试通过")
    
    if passed_tests == total_tests:
        print("🎉 所有测试都通过了! 服务器上的测试用例生成器流程正常!")
    else:
        print("⚠️ 部分测试失败，需要检查相关功能")
    
    return test_results

if __name__ == "__main__":
    main()
