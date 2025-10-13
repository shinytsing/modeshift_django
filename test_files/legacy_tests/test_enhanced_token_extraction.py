#!/usr/bin/env python3
"""
测试增强版Token提取功能
详细测试各种Token提取方法
"""
import sys
import os

# 添加项目路径
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')

def test_enhanced_token_extraction():
    """测试增强版Token提取功能"""
    print("🔍 测试增强版Token提取功能...")
    
    try:
        from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
        
        # 创建服务实例
        service = BossZhipinPlaywrightService(headless=True)
        
        # 测试HTTP请求检测（包含Token提取）
        print("\n1. 测试HTTP请求检测和Token提取...")
        http_result = service._check_login_via_http_request()
        print(f"📊 HTTP检测结果: {http_result}")
        
        if http_result.get('token_info'):
            token_info = http_result['token_info']
            print(f"🔑 提取到的Token信息: {token_info}")
            if token_info.get('token'):
                print(f"🎉 成功提取到Token: {token_info['token'][:50]}...")
                print(f"📊 Token来源: {token_info.get('source', '未知')}")
            else:
                print("❌ 未提取到Token")
        else:
            print("❌ 未获取到Token信息")
        
        # 测试完整的检测流程
        print("\n2. 测试完整检测流程...")
        full_result = service.check_login_status(1)
        print(f"📊 完整检测结果: {full_result}")
        
        if full_result.get('token_info'):
            token_info = full_result['token_info']
            print(f"🔑 完整检测Token信息: {token_info}")
            if token_info.get('token'):
                print(f"🎉 完整检测成功提取到Token: {token_info['token'][:50]}...")
                print(f"📊 Token来源: {token_info.get('source', '未知')}")
            else:
                print("❌ 完整检测未提取到Token")
        else:
            print("❌ 完整检测未获取到Token信息")
            
    except Exception as e:
        print(f"💥 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

def test_direct_http_extraction():
    """直接测试HTTP响应Token提取"""
    print("\n3. 直接测试HTTP响应Token提取...")
    
    try:
        import requests
        from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
        
        # 创建服务实例
        service = BossZhipinPlaywrightService(headless=True)
        
        # 直接访问Boss直聘页面
        url = "https://www.zhipin.com/web/geek/jobs"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        print(f"🔍 访问URL: {url}")
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📊 响应内容长度: {len(response.text)}")
        print(f"📊 最终URL: {response.url}")
        
        # 使用服务提取Token
        token_info = service._extract_token_from_http_response(response)
        print(f"🔑 提取到的Token信息: {token_info}")
        
        if token_info.get('token'):
            print(f"🎉 成功提取到Token: {token_info['token'][:50]}...")
            print(f"📊 Token来源: {token_info.get('source', '未知')}")
        else:
            print("❌ 未提取到Token")
            
            # 检查响应内容中是否包含可能的token
            content = response.text
            print(f"\n🔍 检查响应内容中的token模式...")
            
            import re
            patterns = [
                r'"wt2":"([^"]+)"',
                r'"zp_at":"([^"]+)"',
                r'"token":"([^"]+)"',
                r'wt2=([^&\s]+)',
                r'zp_at=([^&\s]+)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    print(f"✅ 找到匹配模式 {pattern}: {matches[:3]}...")  # 只显示前3个匹配
                else:
                    print(f"❌ 模式 {pattern} 无匹配")
            
            # 检查页面中是否包含登录相关的内容
            login_indicators = ['立即沟通', '投递简历', '我的简历', '个人中心']
            found_indicators = [indicator for indicator in login_indicators if indicator in content]
            print(f"🔍 找到的登录指标: {found_indicators}")
            
    except Exception as e:
        print(f"💥 直接HTTP测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 增强版Token提取功能测试")
    print("=" * 60)
    
    test_enhanced_token_extraction()
    test_direct_http_extraction()
    
    print("\n" + "=" * 60)
    print("🏁 测试完成")
    print("=" * 60)
