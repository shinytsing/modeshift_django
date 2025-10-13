#!/usr/bin/env python3
"""
HTTP请求方式测试智能投递流程
直接调用Django API接口，避免asyncio问题
"""
import requests
import json
import time

def test_smart_delivery_via_http():
    """通过HTTP请求测试智能投递流程"""
    print("🌐 通过HTTP请求测试智能投递流程...")
    
    # Django服务器地址
    base_url = "http://localhost:8000"
    
    # 测试数据
    test_data = {
        "platforms": ["boss"],
        "keywords": ["Python", "Java"],
        "cities": ["101020100"],  # 北京
        "expected_salary": [15, 25],
        "say_hi": "您好，我有相关工作经验，希望应聘这个岗位！",
        "use_ai": True,
        "send_img_resume": False
    }
    
    print(f"📋 测试数据: {test_data}")
    
    try:
        # 步骤1: 测试智能投递API
        print("🔍 步骤1: 调用智能投递API...")
        
        # 使用现有的API接口
        api_url = f"{base_url}/tools/job-search/start-playwright-api/"
        
        headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': 'test'  # 简化测试，实际使用时需要获取CSRF token
        }
        
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
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保Django服务器正在运行 (python manage.py runserver)")
    except requests.exceptions.Timeout:
        print("❌ 请求超时: 服务器响应时间过长")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    print("\n" + "="*80)
    print("🔍 HTTP请求测试完成")
    print("="*80)

def test_debug_mode_via_http():
    """通过HTTP请求测试调试模式"""
    print("🐛 通过HTTP请求测试调试模式...")
    
    # Django服务器地址
    base_url = "http://localhost:8000"
    
    # 测试数据
    test_data = {
        "platforms": ["boss"],
        "keywords": ["Python"],
        "cities": ["101020100"],
        "expected_salary": [15, 25],
        "say_hi": "测试调试模式",
        "use_ai": True,
        "send_img_resume": False
    }
    
    try:
        # 调用调试API
        api_url = f"{base_url}/tools/job-search/debug-playwright-login-api/"
        
        headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': 'test'
        }
        
        response = requests.post(
            api_url,
            json=test_data,
            headers=headers,
            timeout=60  # 调试模式可能需要更长时间
        )
        
        print(f"📊 调试API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 调试API调用成功")
            
            if result.get('debug_logs'):
                print("📋 调试日志:")
                for log in result.get('debug_logs', []):
                    print(f"  {log}")
            
            if result.get('success'):
                print("🎉 调试模式投递成功！")
            else:
                print("⚠️ 调试模式需要登录")
                print(f"📋 说明: {result.get('instructions', [])}")
                
        else:
            print(f"❌ 调试API调用失败: {response.status_code}")
            print(f"❌ 响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 调试模式请求失败: {str(e)}")

def test_cookie_validation_via_http():
    """通过HTTP请求测试Cookie验证"""
    print("🍪 通过HTTP请求测试Cookie验证...")
    
    # Django服务器地址
    base_url = "http://localhost:8000"
    
    # 用户提供的Cookie数据
    test_cookies = {
        "__a": "20936101.1758901166..1758901166.72.1.72.72",
        "__c": "1758901166", 
        "__g": "-",
        "__l": "l=%2Flogin.zhipin.com%2F&r=http%3A%2F%2Flocalhost%3A8000%2Ftools%2Fjob-search%2Flauncher%2F&g=&s=3&friend_source=0&s=3&friend_source=0",
        "__zp_stoken__": "0138fT05Aw4XEhsOMOzQRHR4WFUEwQE4rHzhPMkNFRE9ORUdGT05NJUA%2Fw4HDhcSNwovDtlnDinNPMk5FQk9POEVFOiJOQcK7T040W8OFxIfCi8O3YsOKHH0dwrsWc8OPHcOzwrocT8OOKTfCi8OOQTpCQMOqw4zDosOBwpzDjcOZw4HCkcONw5jCujo6QC8rRhZtH1pGOlNRbAhIZ1BmYlwSSUhTKEA7T0UKxIPEgDVHFB4eHxQWHBwdFhAKCh4VEwkJCBMVHx8eFT1PwpvDgcOOxLvEocSyw7PEpMKbwrvEgWzDt8KrwrF3wp1TwqVlxIHCu8K9w43CpWjCnMOBwr9nw4LDg2zDhFtUYcOAS2VTXUh1w4VIVG7DgmfCj1AQHhcdH0YSw59iw4s%3D"
    }
    
    # 测试数据
    test_data = {
        "platforms": ["boss"],
        "keywords": ["Python"],
        "cities": ["101020100"],
        "expected_salary": [15, 25],
        "say_hi": "使用提供的Cookie测试",
        "use_ai": True,
        "send_img_resume": False,
        "current_browser_cookies": test_cookies
    }
    
    try:
        # 调用手动Cookie API
        api_url = f"{base_url}/tools/job-search/boss-manual-cookies-start-api/"
        
        headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': 'test'
        }
        
        response = requests.post(
            api_url,
            json=test_data,
            headers=headers,
            timeout=60
        )
        
        print(f"📊 Cookie验证API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Cookie验证API调用成功")
            
            if result.get('success'):
                print("🎉 Cookie验证成功，投递任务启动！")
                print(f"📝 消息: {result.get('message', 'N/A')}")
                print(f"🆔 任务ID: {result.get('task_id', 'N/A')}")
                
                if result.get('login_detected'):
                    print("✅ 登录状态检测成功")
                    print(f"🍪 Cookie数量: {result.get('cookie_count', 'N/A')}")
            else:
                print("❌ Cookie验证失败")
                print(f"❌ 错误: {result.get('error', '未知错误')}")
                
        else:
            print(f"❌ Cookie验证API调用失败: {response.status_code}")
            print(f"❌ 响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ Cookie验证请求失败: {str(e)}")

def main():
    """主函数"""
    print("🚀 开始HTTP请求方式测试智能投递流程")
    print("="*80)
    
    # 测试1: 智能投递API
    test_smart_delivery_via_http()
    
    print("\n" + "="*80)
    
    # 测试2: 调试模式
    test_debug_mode_via_http()
    
    print("\n" + "="*80)
    
    # 测试3: Cookie验证
    test_cookie_validation_via_http()
    
    print("\n" + "="*80)
    print("🎯 所有HTTP请求测试完成")
    print("="*80)

if __name__ == "__main__":
    main()
