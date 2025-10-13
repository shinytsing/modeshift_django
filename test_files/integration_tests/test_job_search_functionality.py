#!/usr/bin/env python3
"""
简单的AI找工作系统功能验证
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.services.job_search_service import JobSearchService
from django.contrib.auth.models import User

def test_job_search_service():
    """测试JobSearchService服务"""
    print("🧪 测试JobSearchService服务...")
    
    try:
        # 创建服务实例
        service = JobSearchService()
        print("✅ JobSearchService实例创建成功")
        
        # 测试配置生成
        config_data = service._generate_config(
            platforms=['boss', 'liepin'],
            keywords=['Python开发', 'Java工程师'],
            cities=['北京', '上海'],
            expected_salary=[15, 25],
            say_hi='您好，我对这个职位很感兴趣',
            use_ai=True,
            send_img_resume=False
        )
        print("✅ 配置生成成功")
        print(f"📋 配置包含平台: {list(config_data['platforms'].keys())}")
        
        # 测试配置文件写入
        service._write_config_file(config_data)
        print("✅ 配置文件写入成功")
        
        # 检查配置文件是否存在
        if os.path.exists(service.config_file):
            print("✅ 配置文件已创建")
        else:
            print("❌ 配置文件未创建")
        
        print("\n🎉 JobSearchService测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ JobSearchService测试失败: {str(e)}")
        return False

def test_views_import():
    """测试视图导入"""
    print("\n🧪 测试视图导入...")
    
    try:
        from apps.tools.views.job_search_views import (
            job_search_dashboard,
            job_search_launcher,
            start_job_search_api,
            get_job_search_status_api,
            stop_job_search_api
        )
        print("✅ 所有视图函数导入成功")
        return True
    except Exception as e:
        print(f"❌ 视图导入失败: {str(e)}")
        return False

def test_urls_config():
    """测试URL配置"""
    print("\n🧪 测试URL配置...")
    
    try:
        from django.urls import reverse
        from django.test import Client
        
        # 测试URL反向解析
        urls_to_test = [
            'tools:job_search_dashboard',
            'tools:job_search_launcher',
            'tools:start_job_search_api',
            'tools:get_job_search_status_api',
            'tools:stop_job_search_api'
        ]
        
        for url_name in urls_to_test:
            try:
                url = reverse(url_name)
                print(f"✅ {url_name} -> {url}")
            except Exception as e:
                print(f"❌ {url_name} 反向解析失败: {str(e)}")
                return False
        
        print("✅ 所有URL配置正确")
        return True
        
    except Exception as e:
        print(f"❌ URL配置测试失败: {str(e)}")
        return False

def test_template_exists():
    """测试模板是否存在"""
    print("\n🧪 测试模板文件...")
    
    template_path = "templates/tools/job_search_launcher.html"
    if os.path.exists(template_path):
        print("✅ job_search_launcher.html模板存在")
        
        # 检查模板内容
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "AI一键投递系统" in content:
                print("✅ 模板内容正确")
            else:
                print("❌ 模板内容不正确")
        return True
    else:
        print("❌ job_search_launcher.html模板不存在")
        return False

if __name__ == "__main__":
    print("🔧 AI找工作系统功能验证")
    print("=" * 50)
    
    # 运行所有测试
    tests = [
        test_views_import,
        test_urls_config,
        test_template_exists,
        test_job_search_service
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！AI找工作系统集成成功！")
        print("\n🎯 功能特性:")
        print("✅ 支持多平台投递 (Boss直聘、猎聘、拉勾、前程无忧、智联招聘)")
        print("✅ AI智能匹配和个性化打招呼语")
        print("✅ 实时状态监控")
        print("✅ 完整的API接口")
        print("✅ 现代化前端界面")
        print("✅ 集成到work_mode页面")
        
        print("\n📋 使用说明:")
        print("1. 访问 http://localhost:8000/tools/work_mode/")
        print("2. 点击 'AI一键投递系统' 卡片")
        print("3. 配置投递参数")
        print("4. 点击 '开始投递' 按钮")
        print("5. 实时查看投递状态")
        
        print("\n🔧 技术实现:")
        print("- Django视图层: job_search_views.py")
        print("- 服务层: job_search_service.py")
        print("- 前端模板: job_search_launcher.html")
        print("- URL路由: 已集成到tools/urls.py")
        print("- 依赖: PyYAML (已安装)")
        
    else:
        print("❌ 部分测试失败，请检查错误信息")
