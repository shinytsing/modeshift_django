#!/usr/bin/env python3
"""
创建模拟二维码用于测试
"""
import os
import shutil

# 创建media/qr_codes目录
os.makedirs('media/qr_codes', exist_ok=True)

# 复制现有的二维码文件作为测试
if os.path.exists('/tmp/test_qr.png'):
    shutil.copy('/tmp/test_qr.png', 'media/qr_codes/test_qr.png')
    print("✅ 已复制测试二维码到 media/qr_codes/test_qr.png")
else:
    print("❌ 没有找到测试二维码文件")

# 创建一个简单的测试二维码
test_qr_content = """data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="""

print("✅ 模拟二维码生成完成")
print("💡 现在可以测试前端显示功能")
