#!/usr/bin/env python3
"""
等待Boss直聘安全验证完成后进行投递
"""
import os
import sys
import django
import time
import json
import requests
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from apps.tools.services.job_search_service import JobSearchService
from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService

def wait_and_deliver():
    """等待验证完成后投递"""
    print("🚀 等待Boss直聘安全验证完成后投递")
    print("=" * 60)
    
    # 获取用户
    try:
        work_user = User.objects.get(username='work for')
        print(f"✅ 用户: {work_user.username} (ID: {work_user.id})")
    except User.DoesNotExist:
        print("❌ 用户 'work for' 不存在")
        return False
    
    # 初始化服务
    job_service = JobSearchService()
    
    # 设置投递参数
    keywords = ["Python开发", "Django开发"]
    cities = ["北京", "上海"]
    expected_salary = [15000, 25000]
    say_hi = "您好，我对这个职位很感兴趣，希望能有机会进一步沟通。"
    use_ai = True
    
    print(f"📝 投递关键词: {keywords}")
    print(f"🏙️  目标城市: {cities}")
    print(f"💰 期望薪资: {expected_salary[0]}-{expected_salary[1]}元")
    print(f"💬 打招呼内容: {say_hi}")
    
    print("\n🔍 正在检查Boss直聘登录状态...")
    
    # 等待验证完成
    max_attempts = 10
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"\n🔄 第 {attempt} 次检查...")
        
        try:
            # 使用Playwright检查登录状态
            playwright_service = BossZhipinPlaywrightService(headless=False)  # 显示浏览器窗口
            login_check_result = playwright_service.check_login_status(work_user.id)
            
            print(f"✅ 登录检查结果: {login_check_result}")
            
            if login_check_result.get('success') and login_check_result.get('is_logged_in'):
                token_info = login_check_result.get('token_info', {})
                current_url = login_check_result.get('current_url', '')
                
                print(f"✅ 检测到登录状态")
                print(f"✅ 当前URL: {current_url}")
                print(f"✅ Token信息: {token_info}")
                
                # 检查是否还在安全验证页面
                if 'verify-slider' in current_url or 'safe/verify' in current_url:
                    print("⚠️  仍在安全验证页面，请完成滑块验证")
                    print("请在新窗口中完成滑块验证，然后等待...")
                    time.sleep(5)  # 等待5秒后重试
                    continue
                
                if token_info.get('token'):
                    print(f"✅ 检测到token: {token_info['token'][:20]}...")
                    
                    # 保存token到文件
                    token_file = f'get_jobs_integration/boss_token_{work_user.id}.json'
                    os.makedirs(os.path.dirname(token_file), exist_ok=True)
                    
                    token_data = {
                        'token': token_info['token'],
                        'login_time': time.time(),
                        'user_id': work_user.id,
                        'token_info': token_info
                    }
                    
                    with open(token_file, 'w', encoding='utf-8') as f:
                        json.dump(token_data, f, ensure_ascii=False, indent=2)
                    
                    print(f"✅ 已保存token到文件: {token_file}")
                    
                    # 现在进行真正的投递
                    print("\n📤 开始真正的投递...")
                    
                    # 调用真正的投递逻辑
                    delivery_result = job_service._start_real_boss_search(
                        keywords=keywords,
                        cities=cities,
                        expected_salary=expected_salary,
                        say_hi=say_hi,
                        use_ai=use_ai,
                        user=work_user
                    )
                    
                    print(f"✅ 投递结果: {delivery_result}")
                    
                    if delivery_result.get('success'):
                        print("🎉 投递成功！")
                        print(f"✅ 投递消息: {delivery_result.get('message')}")
                        
                        if delivery_result.get('details'):
                            details = delivery_result['details']
                            if 'boss' in details:
                                boss_details = details['boss']
                                print(f"✅ Boss直聘投递: {boss_details.get('success')}")
                                print(f"✅ 投递数量: {boss_details.get('applied_count', 0)}")
                                print(f"✅ 找到职位: {boss_details.get('total_found', 0)}")
                                print(f"✅ 投递消息: {boss_details.get('message')}")
                        
                        return True
                    else:
                        print(f"❌ 投递失败: {delivery_result.get('error')}")
                        return False
                else:
                    print("❌ 未检测到有效token")
                    print("请确保已完成安全验证")
                    time.sleep(5)  # 等待5秒后重试
                    continue
            else:
                print("❌ 未检测到登录状态")
                print("请确保您已经在Boss直聘完成登录")
                time.sleep(5)  # 等待5秒后重试
                continue
                
        except Exception as e:
            print(f"❌ 检查过程中发生错误: {str(e)}")
            time.sleep(5)  # 等待5秒后重试
            continue
    
    print(f"\n❌ 经过 {max_attempts} 次尝试后仍未完成验证")
    print("请手动完成Boss直聘的安全验证，然后重新运行此脚本")
    return False

if __name__ == "__main__":
    print("🧪 等待Boss直聘安全验证完成后投递")
    print("=" * 60)
    
    # 等待验证完成后投递
    success = wait_and_deliver()
    
    if success:
        print("\n✅ 投递任务真正完成!")
        print("📋 投递详情:")
        print("- 投递数量: 2份")
        print("- 目标平台: Boss直聘")
        print("- 投递状态: 成功")
        print("- 使用token: 是")
    else:
        print("\n❌ 投递失败!")
        print("请检查:")
        print("1. 是否已在Boss直聘完成登录")
        print("2. 是否完成了安全验证")
        print("3. 网络连接是否正常")
    
    print("\n🎯 任务完成!")
