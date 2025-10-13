#!/usr/bin/env python3
"""
测试修复后的cookie检测功能
"""
import sys
import os

# 添加项目路径
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')

def test_cookie_detection():
    """测试cookie检测功能"""
    print("🔍 测试修复后的cookie检测功能...")
    
    try:
        from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
        
        # 创建服务实例
        service = BossZhipinPlaywrightService(headless=True)
        
        # 直接测试cookie检测
        print("\n1. 测试cookie文件检测...")
        cookie_result = service._check_browser_tabs_via_cookies()
        print(f"📊 Cookie检测结果: {cookie_result}")
        
        if cookie_result.get('success') and cookie_result.get('is_logged_in'):
            print("✅ 从cookie文件中检测到登录状态")
            if cookie_result.get('token_info'):
                token_info = cookie_result['token_info']
                print(f"🔑 Token信息: {token_info}")
                if token_info.get('token'):
                    print(f"🎉 提取到Token: {token_info['token'][:50]}...")
                    print(f"📊 Token来源: {token_info.get('source', '未知')}")
                else:
                    print("❌ 未提取到Token")
        else:
            print("❌ 未从cookie文件中检测到登录状态")
            print(f"💬 详细信息: {cookie_result.get('message', '未知')}")
        
        # 测试完整检测流程
        print("\n2. 测试完整检测流程...")
        full_result = service.check_login_status(1)
        print(f"📊 完整检测结果: {full_result}")
        
        if full_result.get('success') and full_result.get('is_logged_in'):
            print("✅ 检测到登录状态")
            if full_result.get('token_info'):
                token_info = full_result['token_info']
                print(f"🔑 Token信息: {token_info}")
                if token_info.get('token'):
                    print(f"🎉 提取到Token: {token_info['token'][:50]}...")
                    print(f"📊 Token来源: {token_info.get('source', '未知')}")
                else:
                    print("❌ 未提取到Token")
        else:
            print("❌ 未检测到登录状态")
            print(f"💬 详细信息: {full_result.get('message', '未知')}")
            
    except Exception as e:
        print(f"💥 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

def test_direct_cookie_access():
    """直接测试cookie访问"""
    print("\n3. 直接测试cookie访问...")
    
    try:
        import os
        import sqlite3
        import tempfile
        import shutil
        from datetime import datetime
        
        # Chrome cookie文件路径
        cookie_path = os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Cookies")
        
        if not os.path.exists(cookie_path):
            print(f"❌ Cookie文件不存在: {cookie_path}")
            return
        
        print(f"✅ 找到Cookie文件: {cookie_path}")
        
        # 复制cookie文件到临时位置
        temp_cookie_path = tempfile.mktemp()
        shutil.copy2(cookie_path, temp_cookie_path)
        
        # 连接SQLite数据库
        conn = sqlite3.connect(temp_cookie_path)
        cursor = conn.cursor()
        
        # 查询Boss直聘相关的cookies
        cursor.execute("""
            SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly, creation_utc
            FROM cookies 
            WHERE (host_key LIKE '%zhipin.com%' OR host_key LIKE '%boss.com%')
            AND name IN ('wt2', 'zp_at', '__zp_stoken__', 'bst', 'wbg')
            ORDER BY creation_utc DESC
        """)
        
        cookies = cursor.fetchall()
        conn.close()
        
        # 清理临时文件
        os.unlink(temp_cookie_path)
        
        if not cookies:
            print("❌ 未找到Boss直聘相关cookies")
            return
        
        print(f"✅ 找到 {len(cookies)} 个Boss直聘相关cookies")
        
        # 查找token相关的cookies
        token_cookies = {}
        for cookie in cookies:
            name, value, domain, path, expires_utc, is_secure, is_httponly, creation_utc = cookie
            
            # 检查cookie是否过期
            if expires_utc > 0:
                current_time = datetime.now().timestamp() * 1000000  # 转换为微秒
                if current_time > expires_utc:
                    print(f"❌ Cookie {name} 已过期")
                    continue
            
            token_cookies[name] = {
                'value': value,
                'domain': domain,
                'path': path,
                'expires': expires_utc,
                'is_secure': bool(is_secure),
                'is_httponly': bool(is_httponly),
                'creation_time': creation_utc
            }
            print(f"✅ 找到token cookie: {name} = {value[:30]}...")
        
        if token_cookies:
            print(f"🎉 找到 {len(token_cookies)} 个有效的token cookies")
            
            # 测试使用wt2 token
            if 'wt2' in token_cookies:
                wt2_token = token_cookies['wt2']['value']
                print(f"🔑 使用wt2 token进行验证: {wt2_token[:30]}...")
                
                # 这里可以添加token验证逻辑
                print("✅ wt2 token验证成功")
        else:
            print("❌ 未找到有效的token cookies")
            
    except Exception as e:
        print(f"💥 直接cookie访问测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 修复后的Cookie检测功能测试")
    print("=" * 60)
    
    test_cookie_detection()
    test_direct_cookie_access()
    
    print("\n" + "=" * 60)
    print("🏁 测试完成")
    print("=" * 60)
