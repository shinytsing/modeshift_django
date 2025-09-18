#!/bin/bash

echo "开始修复服务器上的训练计划编辑器..."

# 1. 下载最新的JavaScript文件
echo "下载最新的training_plan_editor.js文件..."
curl -s "https://raw.githubusercontent.com/shinytsing/modeshift_django/f4000134b5f727556c8063efe712c80163382036/src/static/js/training_plan_editor.js" -o src/static/js/training_plan_editor.js

# 2. 修复模板文件，添加JavaScript引用
echo "修复模板文件..."
if grep -q "training_plan_editor.js" templates/tools/training_plan_editor.html; then
    echo "JavaScript文件引用已存在"
else
    echo "添加JavaScript文件引用..."
    # 在</script>标签后添加JavaScript文件引用
    sed -i '/<\/script>/a\\n<!-- 引入训练计划编辑器JavaScript文件 -->\n<script src="{% static '\''js/training_plan_editor.js'\'' %}"></script>' templates/tools/training_plan_editor.html
fi

# 3. 收集静态文件
echo "收集静态文件..."
source venv/bin/activate
python manage.py collectstatic --noinput

# 4. 重启服务
echo "重启Django服务..."
pkill -f "python manage.py runserver" || true
pkill -f "gunicorn" || true

# 启动服务（后台运行）
nohup python manage.py runserver 0.0.0.0:8000 > /dev/null 2>&1 &
echo "Django服务已重启"

# 5. 验证修复结果
echo "验证修复结果..."
sleep 3
curl -I http://localhost:8000/tools/fitness/plan-editor/ || echo "页面访问测试失败"

echo "服务器修复完成！"
echo "请访问: http://shenyiqing.xin/tools/fitness/plan-editor/"
