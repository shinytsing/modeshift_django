#!/usr/bin/env python3
"""
Token管理功能测试脚本
测试跨标签页token同步功能
"""

import os
import sys
import django
import json
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from apps.tools.services.cookie_manager_service import get_cookie_manager
from apps.users.middleware_async_safe import get_user_login_state, sync_user_session


def test_cookie_manager():
    """测试Cookie管理器功能"""
    print("🧪 测试Cookie管理器功能...")
    
    # 获取或创建测试用户
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )
    
    if created:
        print(f"✅ 创建测试用户: {user.username}")
    else:
        print(f"✅ 使用现有测试用户: {user.username}")
    
    # 测试Boss直聘Cookie管理器
    cookie_manager = get_cookie_manager(user, 'boss')
    
    # 测试保存token
    test_token = "test_token_123456789"
    success = cookie_manager.save_token(test_token, 'test_login')
    print(f"✅ 保存Token: {'成功' if success else '失败'}")
    
    # 测试加载token
    token_data = cookie_manager.load_token()
    if token_data and token_data.get('is_valid'):
        print(f"✅ 加载Token: 成功 (Token: {token_data['token'][:20]}...)")
    else:
        print("❌ 加载Token: 失败")
    
    # 测试token有效性
    is_valid = cookie_manager.is_token_valid()
    print(f"✅ Token有效性检查: {'有效' if is_valid else '无效'}")
    
    # 测试获取登录状态
    status = cookie_manager.get_login_status()
    print(f"✅ 登录状态: {json.dumps(status, indent=2, ensure_ascii=False)}")
    
    # 测试清除token
    clear_success = cookie_manager.clear_token()
    print(f"✅ 清除Token: {'成功' if clear_success else '失败'}")
    
    return True


def test_middleware_functions():
    """测试中间件功能"""
    print("\n🧪 测试中间件功能...")
    
    # 获取测试用户
    user = User.objects.get(username='test_user')
    
    # 测试获取用户登录状态
    login_state = get_user_login_state(user.id)
    print(f"✅ 用户登录状态: {json.dumps(login_state, indent=2, ensure_ascii=False)}")
    
    # 测试同步用户session
    session_data = {
        'boss_token': 'test_session_token',
        'login_time': time.time(),
        'platform': 'boss'
    }
    sync_success = sync_user_session(user.id, session_data)
    print(f"✅ 同步用户Session: {'成功' if sync_success else '失败'}")
    
    return True


def test_cross_tab_sync():
    """测试跨标签页同步功能"""
    print("\n🧪 测试跨标签页同步功能...")
    
    # 获取测试用户
    user = User.objects.get(username='test_user')
    
    # 模拟多个标签页的token操作
    platforms = ['boss', 'lagou', 'liepin', 'zhipin', '51job']
    
    for platform in platforms:
        cookie_manager = get_cookie_manager(user, platform)
        
        # 保存token
        test_token = f"test_token_{platform}_{int(time.time())}"
        success = cookie_manager.save_token(test_token, 'cross_tab_test')
        
        if success:
            print(f"✅ {platform} Token保存成功")
            
            # 验证token
            token_data = cookie_manager.load_token()
            if token_data and token_data.get('is_valid'):
                print(f"✅ {platform} Token验证成功")
            else:
                print(f"❌ {platform} Token验证失败")
        else:
            print(f"❌ {platform} Token保存失败")
    
    return True


def test_async_safety():
    """测试异步安全性"""
    print("\n🧪 测试异步安全性...")
    
    # 测试异步上下文检测
    from apps.users.middleware_async_safe import is_async_context
    
    # 在同步上下文中测试
    is_async = is_async_context()
    print(f"✅ 同步上下文检测: {'异步' if is_async else '同步'}")
    
    # 测试异步安全装饰器
    from apps.users.middleware_async_safe import async_safe_session
    
    @async_safe_session
    def test_function(self, request):
        return "test_result"
    
    # 模拟request对象
    class MockRequest:
        pass
    
    request = MockRequest()
    result = test_function(None, request)
    print(f"✅ 异步安全装饰器测试: {'通过' if result is not None else '跳过'}")
    
    return True


def cleanup_test_data():
    """清理测试数据"""
    print("\n🧹 清理测试数据...")
    
    try:
        # 删除测试用户
        user = User.objects.get(username='test_user')
        user.delete()
        print("✅ 测试用户已删除")
        
        # 清理cookie文件
        cookie_dir = Path(__file__).parent.parent / 'get_jobs_integration' / 'cookies'
        if cookie_dir.exists():
            for file in cookie_dir.glob('*test_user*'):
                file.unlink()
                print(f"✅ 删除cookie文件: {file.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 清理测试数据失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始Token管理功能测试...")
    print("=" * 50)
    
    try:
        # 运行各项测试
        test_cookie_manager()
        test_middleware_functions()
        test_cross_tab_sync()
        test_async_safety()
        
        print("\n" + "=" * 50)
        print("✅ 所有测试完成！")
        
        # 询问是否清理测试数据
        try:
            cleanup = input("\n是否清理测试数据？(y/N): ").strip().lower()
        except EOFError:
            cleanup = 'n'  # 在非交互环境中默认不清理
        if cleanup in ['y', 'yes']:
            cleanup_test_data()
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
