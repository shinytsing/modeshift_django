#!/usr/bin/env python3
"""
简化的HTTP请求测试脚本
直接测试Django API接口
"""
import requests
import json
import time

def test_simple_api():
    """测试简单的API接口"""
    print("🌐 测试Django API接口...")
    
    # Django服务器地址
    base_url = "http://localhost:8000"
    
    try:
        # 测试1: 健康检查
        print("🔍 测试1: 健康检查...")
        health_url = f"{base_url}/tools/health/"
        
        response = requests.get(health_url, timeout=10)
        print(f"📊 健康检查状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Django服务器运行正常")
        else:
            print(f"❌ 健康检查失败: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: Django服务器未运行")
        print("💡 请先运行: python3 manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ 健康检查失败: {str(e)}")
        return False
    
    # 测试2: 投递API
    print("\n🔍 测试2: 投递API...")
    
    # 测试数据
    test_data = {
        "platforms": ["boss"],
        "keywords": ["Python"],
        "cities": ["101020100"],  # 北京
        "expected_salary": [15, 25],
        "say_hi": "测试HTTP请求",
        "use_ai": True,
        "send_img_resume": False
    }
    
    try:
        # 使用现有的API接口
        api_url = f"{base_url}/tools/job-search/start-playwright-api/"
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        print(f"📤 发送请求到: {api_url}")
        print(f"📋 请求数据: {test_data}")
        
        response = requests.post(
            api_url,
            json=test_data,
            headers=headers,
            timeout=30
        )
        
        print(f"📊 API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API调用成功: {result}")
            
            # 分析响应结果
            if result.get('success'):
                print("🎉 投递任务启动成功！")
                print(f"📝 消息: {result.get('message', 'N/A')}")
                print(f"🆔 任务ID: {result.get('task_id', 'N/A')}")
                
                if result.get('login_detected'):
                    print("✅ 登录状态检测成功")
                    print(f"🍪 Cookie来源: {result.get('cookie_source', 'N/A')}")
                    print(f"🍪 Cookie数量: {result.get('cookie_count', 'N/A')}")
                else:
                    print("⚠️ 需要登录")
                    print(f"📋 说明: {result.get('instructions', [])}")
                    
            else:
                print("❌ 投递任务启动失败")
                print(f"❌ 错误: {result.get('error', '未知错误')}")
                
                if result.get('need_login'):
                    print("🔐 需要登录")
                    print(f"🌐 登录URL: {result.get('login_url', 'N/A')}")
                    print(f"📋 说明: {result.get('instructions', [])}")
                    
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"❌ 响应内容: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时: 服务器响应时间过长")
    except Exception as e:
        print(f"❌ API请求失败: {str(e)}")
    
    return True

def main():
    """主函数"""
    print("🚀 开始简化HTTP请求测试")
    print("="*60)
    
    # 测试API
    success = test_simple_api()
    
    print("\n" + "="*60)
    if success:
        print("🎯 HTTP请求测试完成")
    else:
        print("❌ HTTP请求测试失败")
    print("="*60)

if __name__ == "__main__":
    main()
