"""
Java Job项目集成视图
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def java_job_launcher(request):
    """Java Job项目启动器页面"""
    return render(request, "tools/java_job_launcher.html")
