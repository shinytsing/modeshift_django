import os
import requests
import json
import hashlib
import hmac
import time

# 从环境变量获取配置
SECRET_ID = os.getenv("TENCENT_SECRET_ID")
SECRET_KEY = os.getenv("TENCENT_SECRET_KEY")
APP_ID = os.getenv("TENCENT_APP_ID")

print(f"SECRET_ID: {SECRET_ID}")
print(f"SECRET_KEY: {SECRET_KEY}")
print(f"APP_ID: {APP_ID}")

if not all([SECRET_ID, SECRET_KEY, APP_ID]):
    print("❌ 环境变量未正确设置")
    exit(1)

print("✅ 环境变量已正确设置")
