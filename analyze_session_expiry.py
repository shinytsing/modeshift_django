#!/usr/bin/env python3
"""
分析小红书Session Cookies的过期时间
"""

import json
from datetime import datetime, timezone
import time

def analyze_cookie_expiry():
    """分析cookies的过期时间"""
    
    # 从您提供的cookies信息中提取过期时间
    cookies_info = [
        {
            'name': 'a1',
            'value': '199608cf964yvz549ui3xvscqnaj45qjlfmgcy1k730000353623',
            'domain': '.xiaohongshu.com',
            'expires': '2026-09-19T05:57:55.000Z',
            'size': 54
        },
        {
            'name': 'abRequestId',
            'value': '5f03eff4-d846-5bec-af3a-c7e8cc18524d',
            'domain': '.xiaohongshu.com',
            'expires': '2026-09-19T05:57:55.109Z',
            'size': 47
        },
        {
            'name': 'access-token-creator.xiaohongshu.com',
            'value': 'customer.creator.AT-68c517551739764341964804bqq4davmmuqvdi2b',
            'domain': '.xiaohongshu.com',
            'expires': '2025-10-19T10:07:09.112Z',
            'size': 96
        },
        {
            'name': 'acw_tc',
            'value': '0a00d10f17583864092864433e5087cb254dde33ccfb1039ee0f11a1a156ea',
            'domain': 'www.xiaohongshu.com',
            'expires': '2025-09-20T17:10:09.251Z',
            'size': 68
        },
        {
            'name': 'customer-sso-sid',
            'value': '68c517551739764341506052gn6vysaufxsbdr6u',
            'domain': '.xiaohongshu.com',
            'expires': '2025-09-26T10:07:09.112Z',
            'size': 56
        },
        {
            'name': 'customerClientId',
            'value': '081742093739190',
            'domain': '.xiaohongshu.com',
            'expires': '2026-10-24T10:07:10.112Z',
            'size': 31
        },
        {
            'name': 'galaxy_creator_session_id',
            'value': 'qwfS4thztazGEubcWRCvts9Pmz32VtTT20TL',
            'domain': '.xiaohongshu.com',
            'expires': '2025-10-19T10:07:10.112Z',
            'size': 61
        },
        {
            'name': 'galaxy.creator.beaker.session.id',
            'value': '1758276430441061473108',
            'domain': '.xiaohongshu.com',
            'expires': '2025-10-19T10:07:10.112Z',
            'size': 54
        },
        {
            'name': 'gid',
            'value': 'yjjK8Yf8J01iyjjK8YSijivyK4vhu24j73qC6TWhMSAI0kq8V42AVS888q2qKJq8J4WW0WfJ',
            'domain': '.xiaohongshu.com',
            'expires': '2026-10-25T16:43:27.603Z',
            'size': 75
        },
        {
            'name': 'loadts',
            'value': '1758386605015',
            'domain': '.xiaohongshu.com',
            'expires': '2026-09-20T16:43:25.000Z',
            'size': 19
        },
        {
            'name': 'sec_poison_id',
            'value': 'ec30d5d1-8421-407c-b1cb-1ff9fd2124b6',
            'domain': '.xiaohongshu.com',
            'expires': '2025-09-20T16:50:14.000Z',
            'size': 49
        },
        {
            'name': 'unread',
            'value': '{%22ub%22:%2268a89bd4000000001b03fab9%22%2C%22ue%22:%2268c551ec000000001c007f58%22%2C%22uc%22:16}',
            'domain': '.xiaohongshu.com',
            'expires': 'Session',  # 会话cookie
            'size': 103
        },
        {
            'name': 'web_session',
            'value': '040069b710bd814e12fd57b9f93a4bce154a3c',
            'domain': '.xiaohongshu.com',
            'expires': '2026-09-19T05:59:26.442Z',
            'size': 49
        }
    ]
    
    print("🍪 小红书Session Cookies过期时间分析")
    print("=" * 60)
    
    current_time = datetime.now(timezone.utc)
    print(f"当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    # 按过期时间分类
    expired_cookies = []
    short_term_cookies = []  # 1个月内过期
    medium_term_cookies = []  # 1-6个月过期
    long_term_cookies = []  # 6个月以上过期
    session_cookies = []
    
    for cookie in cookies_info:
        if cookie['expires'] == 'Session':
            session_cookies.append(cookie)
            continue
            
        try:
            # 解析过期时间
            if cookie['expires'].endswith('Z'):
                expiry_time = datetime.fromisoformat(cookie['expires'].replace('Z', '+00:00'))
            else:
                expiry_time = datetime.fromisoformat(cookie['expires'])
            
            # 计算剩余时间
            time_diff = expiry_time - current_time
            days_remaining = time_diff.days
            hours_remaining = time_diff.seconds // 3600
            
            cookie_info = {
                'name': cookie['name'],
                'expires': cookie['expires'],
                'days_remaining': days_remaining,
                'hours_remaining': hours_remaining,
                'expiry_time': expiry_time
            }
            
            if days_remaining < 0:
                expired_cookies.append(cookie_info)
            elif days_remaining <= 30:
                short_term_cookies.append(cookie_info)
            elif days_remaining <= 180:
                medium_term_cookies.append(cookie_info)
            else:
                long_term_cookies.append(cookie_info)
                
        except Exception as e:
            print(f"⚠️ 解析cookie {cookie['name']} 过期时间失败: {e}")
    
    # 显示结果
    if expired_cookies:
        print("❌ 已过期的Cookies:")
        for cookie in expired_cookies:
            print(f"   {cookie['name']}: {cookie['expires']} (已过期 {abs(cookie['days_remaining'])} 天)")
        print()
    
    if short_term_cookies:
        print("⚠️ 短期Cookies (1个月内过期):")
        for cookie in short_term_cookies:
            print(f"   {cookie['name']}: {cookie['expires']} (剩余 {cookie['days_remaining']} 天 {cookie['hours_remaining']} 小时)")
        print()
    
    if medium_term_cookies:
        print("📅 中期Cookies (1-6个月过期):")
        for cookie in medium_term_cookies:
            print(f"   {cookie['name']}: {cookie['expires']} (剩余 {cookie['days_remaining']} 天)")
        print()
    
    if long_term_cookies:
        print("✅ 长期Cookies (6个月以上过期):")
        for cookie in long_term_cookies:
            print(f"   {cookie['name']}: {cookie['expires']} (剩余 {cookie['days_remaining']} 天)")
        print()
    
    if session_cookies:
        print("🔄 会话Cookies (浏览器关闭时过期):")
        for cookie in session_cookies:
            print(f"   {cookie['name']}: Session Cookie")
        print()
    
    # 分析关键cookies
    print("🔑 关键Cookies分析:")
    print("=" * 40)
    
    critical_cookies = ['a1', 'web_session', 'customer-sso-sid', 'galaxy_creator_session_id']
    
    for cookie_name in critical_cookies:
        cookie = next((c for c in cookies_info if c['name'] == cookie_name), None)
        if cookie:
            if cookie['expires'] == 'Session':
                print(f"   {cookie_name}: 会话Cookie (浏览器关闭时过期)")
            else:
                try:
                    expiry_time = datetime.fromisoformat(cookie['expires'].replace('Z', '+00:00'))
                    time_diff = expiry_time - current_time
                    days_remaining = time_diff.days
                    
                    if days_remaining < 0:
                        status = "❌ 已过期"
                    elif days_remaining <= 7:
                        status = "⚠️ 即将过期"
                    elif days_remaining <= 30:
                        status = "📅 短期有效"
                    else:
                        status = "✅ 长期有效"
                    
                    print(f"   {cookie_name}: {status} (剩余 {days_remaining} 天)")
                except:
                    print(f"   {cookie_name}: 解析失败")
    
    # 建议
    print("\n💡 建议:")
    print("=" * 20)
    
    if expired_cookies:
        print("1. ❌ 立即更新已过期的cookies")
    
    if short_term_cookies:
        print("2. ⚠️ 准备更新即将过期的cookies")
    
    if session_cookies:
        print("3. 🔄 会话cookies需要保持浏览器活跃状态")
    
    print("4. 📊 建议实现自动cookie监控和更新机制")
    print("5. 🔄 定期检查cookie有效性，避免爬虫失败")

if __name__ == "__main__":
    analyze_cookie_expiry()
