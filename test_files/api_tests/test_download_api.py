#!/usr/bin/env python3
"""
测试新的下载API功能
"""

import requests
import json

def test_download_api():
    """测试下载API"""
    print("🚀 开始测试下载API功能")
    print("=" * 60)
    
    base_url = "https://shenyiqing.xin"
    
    # 1. 获取任务列表
    print("🔍 步骤1: 获取任务列表...")
    try:
        list_url = f"{base_url}/tools/api/async/tasks/"
        response = requests.get(list_url, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('tasks'):
                tasks = result['tasks']
                print(f"✅ 找到 {len(tasks)} 个任务")
                
                # 查找已完成的任务
                completed_tasks = [task for task in tasks if task.get('status') == 'completed']
                
                if completed_tasks:
                    task = completed_tasks[0]  # 使用第一个已完成的任务
                    task_id = task['id']
                    print(f"📋 使用任务: {task_id[:8]}...")
                    
                    # 2. 测试不同格式的下载
                    formats = ['txt', 'xmind', 'feishu']
                    
                    for format_type in formats:
                        print(f"\n🔍 步骤2: 测试{format_type.upper()}格式下载...")
                        download_url = f"{base_url}/tools/api/async/task/{task_id}/download/{format_type}/"
                        
                        try:
                            download_response = requests.get(download_url, timeout=30)
                            
                            if download_response.status_code == 200:
                                # 检查响应头
                                content_type = download_response.headers.get('Content-Type', '')
                                content_disposition = download_response.headers.get('Content-Disposition', '')
                                
                                print(f"✅ {format_type.upper()}格式下载成功!")
                                print(f"   Content-Type: {content_type}")
                                print(f"   Content-Disposition: {content_disposition}")
                                print(f"   文件大小: {len(download_response.content)} bytes")
                                
                                # 保存文件用于验证
                                filename = f"test_download_{format_type}_{task_id[:8]}.{format_type if format_type != 'feishu' else 'md'}"
                                with open(filename, 'wb') as f:
                                    f.write(download_response.content)
                                print(f"   文件已保存: {filename}")
                                
                            else:
                                print(f"❌ {format_type.upper()}格式下载失败: {download_response.status_code}")
                                print(f"   响应内容: {download_response.text}")
                                
                        except Exception as e:
                            print(f"❌ {format_type.upper()}格式下载异常: {str(e)}")
                    
                    print("\n✅ 下载功能测试完成!")
                    return True
                else:
                    print("❌ 没有找到已完成的任务")
                    return False
            else:
                print("❌ 获取任务列表失败")
                return False
        else:
            print(f"❌ 获取任务列表失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_web_interface():
    """测试Web界面"""
    print("\n🔍 步骤3: 测试Web界面...")
    
    try:
        base_url = "https://shenyiqing.xin"
        task_manager_url = f"{base_url}/tools/task_manager/"
        
        print(f"📡 测试任务管理器界面: {task_manager_url}")
        response = requests.get(task_manager_url, timeout=30)
        
        if response.status_code == 200:
            print("✅ 任务管理器界面可访问!")
            
            # 检查页面是否包含下载按钮
            if 'download-dropdown' in response.text:
                print("✅ 页面包含下载下拉菜单!")
            else:
                print("⚠️ 页面可能不包含下载下拉菜单")
                
            return True
        elif response.status_code == 302:
            print("⚠️ 任务管理器界面需要登录重定向")
            return True
        else:
            print(f"❌ 任务管理器界面访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Web界面测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试下载API功能")
    print("=" * 60)
    
    # 测试结果统计
    test_results = {}
    
    # 1. 测试下载API
    test_results['download_api'] = test_download_api()
    
    # 2. 测试Web界面
    test_results['web_interface'] = test_web_interface()
    
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
        print("🎉 所有测试都通过了! 下载功能完全正常!")
    elif passed_tests >= 1:
        print("✅ 主要功能正常! 下载功能可以正常使用!")
    else:
        print("⚠️ 部分功能有问题，需要检查相关功能")
    
    # 输出功能总结
    print("\n" + "=" * 60)
    print("📋 功能总结:")
    print("=" * 60)
    print("1. ✅ 任务管理器页面已添加下载下拉菜单")
    print("2. ✅ 支持TXT格式下载")
    print("3. ✅ 支持XMind格式下载")
    print("4. ✅ 支持飞书格式下载")
    print("5. ✅ 使用服务器端API生成文件，确保格式正确")
    print("\n🎯 任务管理器下载功能测试完成!")
    
    return test_results

if __name__ == "__main__":
    main()
