#!/usr/bin/env python3
"""
测试自动检测Boss直聘登录状态功能
"""
import requests
import json

def test_job_search_api():
    """测试求职搜索API"""
    url = "http://localhost:8001/tools/job-search/api/start/"
    
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': 'test'
    }
    
    data = {
        "platforms": ["boss"],
        "keywords": ["测试工程师"],
        "cities": ["武汉"],
        "expected_salary": [15],
        "say_hi": "您好！我有三年测试经验，计算机本科\n个人网站shenyiqing.xin，善用大模型工具解决问题\n具备丰富的社交软件测试经验，[青藤之恋]app.\n独立负责过 Web 、移动端、h5，服务端的核心测试工作。有性能，api和ui自动化测试经验，并且因此获得了飞书的效率先锋证书\n对cicd有实践部署经验",
        "use_ai": True,
        "send_img_resume": True
    }
    
    try:
        print("🚀 测试求职搜索API...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ API调用成功")
                if result.get('login_detected'):
                    print("✅ 检测到登录状态")
                    print(f"登录信息: {result.get('login_message', '')}")
                else:
                    print("❌ 未检测到登录状态")
            else:
                print(f"❌ API返回错误: {result.get('error', '未知错误')}")
                if result.get('need_login'):
                    print("💡 需要先登录Boss直聘")
                    if result.get('login_status'):
                        login_status = result['login_status']
                        print(f"登录状态详情:")
                        print(f"  - 检测方式: {login_status.get('found_indicator', '未知')}")
                        print(f"  - 置信度: {login_status.get('login_confidence', 0)}%")
                        print(f"  - 当前页面: {login_status.get('current_url', '未知')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
    except Exception as e:
        print(f"❌ 其他错误: {e}")

def test_login_status_api():
    """测试登录状态检测API"""
    url = "http://localhost:8001/tools/job-search/api/boss-status/"
    
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': 'test'
    }
    
    try:
        print("\n🔍 测试登录状态检测API...")
        print(f"URL: {url}")
        
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
    except Exception as e:
        print(f"❌ 其他错误: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("测试自动检测Boss直聘登录状态功能")
    print("=" * 60)
    
    test_login_status_api()
    test_job_search_api()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
