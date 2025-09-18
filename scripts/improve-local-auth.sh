#!/bin/bash

# 改进本地认证系统

echo "🔐 改进本地认证系统..."

# 1. 创建用户注册/登录优化
ssh root@47.103.143.152 "cd /root/modeshift_django && cat > apps/users/views/auth_views.py << 'EOF'
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

def register_view(request):
    \"\"\"用户注册视图\"\"\"
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功！')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

@csrf_exempt
def api_login(request):
    \"\"\"API登录接口\"\"\"
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({'success': True, 'message': '登录成功'})
        else:
            return JsonResponse({'success': False, 'message': '用户名或密码错误'})
    
    return JsonResponse({'success': False, 'message': '无效请求'})
EOF"

# 2. 创建简化的登录页面
ssh root@47.103.143.152 "cd /root/modeshift_django && cat > templates/users/simple_login.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>快速登录</title>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <style>
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        .login-container { max-width: 400px; margin: 100px auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type=\"text\"], input[type=\"password\"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%; }
        .btn:hover { background: #0056b3; }
        .error { color: red; margin-top: 10px; }
        .success { color: green; margin-top: 10px; }
    </style>
</head>
<body>
    <div class=\"login-container\">
        <h2>快速登录</h2>
        <form id=\"loginForm\">
            <div class=\"form-group\">
                <label>用户名/邮箱:</label>
                <input type=\"text\" id=\"username\" required>
            </div>
            <div class=\"form-group\">
                <label>密码:</label>
                <input type=\"password\" id=\"password\" required>
            </div>
            <button type=\"submit\" class=\"btn\">登录</button>
            <div id=\"message\"></div>
        </form>
        
        <div style=\"margin-top: 20px; text-align: center;\">
            <p>还没有账户？ <a href=\"/users/register/\">立即注册</a></p>
        </div>
    </div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const messageDiv = document.getElementById('message');
            
            try {
                const response = await fetch('/users/api/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify({username: username, password: password})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    messageDiv.innerHTML = '<div class=\"success\">登录成功！正在跳转...</div>';
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 1000);
                } else {
                    messageDiv.innerHTML = '<div class=\"error\">' + data.message + '</div>';
                }
            } catch (error) {
                messageDiv.innerHTML = '<div class=\"error\">登录失败，请重试</div>';
            }
        });
    </script>
</body>
</html>
EOF"

echo "✅ 本地认证系统改进完成"
echo "💡 现在用户可以："
echo "   1. 使用用户名/密码快速登录"
echo "   2. 注册新账户"
echo "   3. 享受流畅的登录体验"
