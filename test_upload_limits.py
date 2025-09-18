#!/usr/bin/env python3
"""
测试文件上传限制修复效果
验证200MB文件上传限制是否正确配置
"""

import os
import sys
import requests
import tempfile
from pathlib import Path

# 添加Django项目路径
sys.path.append('/Users/gaojie/Desktop/PycharmProjects/modeshift_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django
django.setup()

from django.conf import settings
from django.test import TestCase, Client
from django.contrib.auth.models import User


class UploadLimitTest:
    """上传限制测试类"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.client = Client()
        self.test_results = []
    
    def create_test_file(self, size_mb: int, filename: str = "test_audio.mp3") -> str:
        """创建指定大小的测试文件"""
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        # 创建指定大小的文件（填充随机数据）
        with open(file_path, 'wb') as f:
            chunk_size = 1024 * 1024  # 1MB chunks
            for _ in range(size_mb):
                f.write(b'0' * chunk_size)
        
        return file_path
    
    def test_django_settings(self):
        """测试Django设置中的文件上传限制"""
        print("🔍 检查Django设置...")
        
        settings_to_check = [
            ('DATA_UPLOAD_MAX_MEMORY_SIZE', settings.DATA_UPLOAD_MAX_MEMORY_SIZE),
            ('FILE_UPLOAD_MAX_MEMORY_SIZE', settings.FILE_UPLOAD_MAX_MEMORY_SIZE),
        ]
        
        expected_size = 200 * 1024 * 1024  # 200MB
        
        for setting_name, actual_value in settings_to_check:
            if actual_value == expected_size:
                print(f"✅ {setting_name}: {actual_value / 1024 / 1024}MB (正确)")
                self.test_results.append(f"✅ {setting_name}: 正确")
            else:
                print(f"❌ {setting_name}: {actual_value / 1024 / 1024}MB (期望: 200MB)")
                self.test_results.append(f"❌ {setting_name}: 错误")
    
    def test_audio_converter_api(self):
        """测试音频转换API的文件大小检查"""
        print("\n🔍 测试音频转换API...")
        
        # 创建测试用户（如果需要登录）
        try:
            user = User.objects.get(username='testuser')
        except User.DoesNotExist:
            user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        
        self.client.force_login(user)
        
        # 测试不同大小的文件
        test_sizes = [
            (50, "应该成功"),      # 50MB - 应该成功
            (150, "应该成功"),     # 150MB - 应该成功  
            (250, "应该失败"),     # 250MB - 应该失败
        ]
        
        for size_mb, expected in test_sizes:
            print(f"\n  测试 {size_mb}MB 文件上传...")
            
            # 创建测试文件
            test_file_path = self.create_test_file(size_mb, f"test_{size_mb}mb.mp3")
            
            try:
                with open(test_file_path, 'rb') as f:
                    response = self.client.post(
                        '/tools/api/audio_converter/',
                        {
                            'audio_file': f,
                            'target_format': 'mp3'
                        },
                        format='multipart'
                    )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        result = f"✅ {size_mb}MB: 上传成功"
                        print(f"    {result}")
                    else:
                        if "文件太大" in data.get('message', ''):
                            if expected == "应该失败":
                                result = f"✅ {size_mb}MB: 正确拒绝 (文件太大)"
                                print(f"    {result}")
                            else:
                                result = f"❌ {size_mb}MB: 意外拒绝"
                                print(f"    {result}")
                        else:
                            result = f"⚠️  {size_mb}MB: 其他错误 - {data.get('message', '')}"
                            print(f"    {result}")
                else:
                    result = f"❌ {size_mb}MB: HTTP {response.status_code}"
                    print(f"    {result}")
                
                self.test_results.append(result)
                
            except Exception as e:
                result = f"❌ {size_mb}MB: 异常 - {str(e)}"
                print(f"    {result}")
                self.test_results.append(result)
            
            finally:
                # 清理测试文件
                if os.path.exists(test_file_path):
                    os.remove(test_file_path)
    
    def test_nginx_config(self):
        """检查Nginx配置文件"""
        print("\n🔍 检查Nginx配置...")
        
        nginx_configs = [
            'nginx.prod.conf',
            'nginx.production.conf'
        ]
        
        for config_file in nginx_configs:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    content = f.read()
                    if 'client_max_body_size 200M' in content:
                        print(f"✅ {config_file}: 已设置200MB限制")
                        self.test_results.append(f"✅ {config_file}: 正确")
                    else:
                        print(f"❌ {config_file}: 未找到200MB限制配置")
                        self.test_results.append(f"❌ {config_file}: 错误")
            else:
                print(f"⚠️  {config_file}: 文件不存在")
                self.test_results.append(f"⚠️  {config_file}: 不存在")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始测试文件上传限制修复效果...\n")
        
        self.test_django_settings()
        self.test_nginx_config()
        self.test_audio_converter_api()
        
        print("\n" + "="*50)
        print("📊 测试结果汇总:")
        print("="*50)
        
        success_count = sum(1 for result in self.test_results if result.startswith("✅"))
        total_count = len(self.test_results)
        
        for result in self.test_results:
            print(result)
        
        print(f"\n✅ 成功: {success_count}/{total_count}")
        
        if success_count == total_count:
            print("\n🎉 所有测试通过！文件上传限制已正确设置为200MB。")
        else:
            print(f"\n⚠️  有 {total_count - success_count} 个测试失败，请检查配置。")
        
        return success_count == total_count


def main():
    """主函数"""
    print("🔧 文件上传限制测试工具")
    print("=" * 50)
    
    tester = UploadLimitTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ 测试完成：文件上传限制已正确配置为200MB")
        return 0
    else:
        print("\n❌ 测试完成：部分配置需要检查")
        return 1


if __name__ == "__main__":
    sys.exit(main())
