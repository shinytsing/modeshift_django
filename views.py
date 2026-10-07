import mimetypes
import os
import subprocess
import sys
import threading

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import redirect, render
from django.views.static import serve
from functools import wraps


def login_required_modal(view_func):
    """
    自定义登录装饰器，未登录时重定向到主页
    """
    if getattr(settings, "AUTH_LOGIN_DISABLED", False):
        return view_func

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        return redirect("home")

    return wrapper


@login_required_modal  # 使用自定义装饰器
def tool_view(request):
    preferred_mode = "work"
    if request.user.is_authenticated:
        try:
            from apps.users.models import UserModePreference

            preferred_mode = UserModePreference.get_user_preferred_mode(request.user)
        except Exception:
            preferred_mode = "work"

    context = {
        "preferred_mode": preferred_mode,
        "mode_names": {
            "work": "极客模式",
            "life": "生活模式",
            "training": "狂暴模式",
            "emo": "Emo模式",
        },
    }

    return render(request, "tool.html", context)  # 确保这里指向你的工具模板


# 添加一个根视图函数
def home_view(request):
    # 主页不自动跳转或显示弹窗，让用户自由浏览
    return render(request, "home.html")  # 显示首页


def welcome_view(request):
    return render(request, "welcome.html")


def theme_demo_view(request):
    return render(request, "theme_demo.html")


def resume_3d_view(request):
    """Public interactive portfolio page for the QA resume."""
    return render(request, "resume_3d.html")


def resume_download_view(request):
    """Download the resume supplied by its owner, independent of desktop paths."""
    resume_path = settings.BASE_DIR / "docs" / "assets" / "gaojie-resume.pdf"
    try:
        resume_file = open(resume_path, "rb")
    except FileNotFoundError:
        raise Http404("简历文件暂不可用")
    return FileResponse(resume_file, as_attachment=True, filename="高杰-测试开发工程师.pdf", content_type="application/pdf")


_resume_demo_lock = threading.Lock()


@require_POST
def resume_run_ui_demo(request):
    """Reuse the registration/login/BMI scenario collected by the GitHub QA gate."""
    from qa.support.auth import auth_mutations_are_allowed

    local_demo = settings.DEBUG and request.META.get("REMOTE_ADDR") in {"127.0.0.1", "::1"}
    if not local_demo and os.getenv("RESUME_UI_DEMO_ENABLED") != "1":
        return JsonResponse({"status": "unavailable", "message": "服务器尚未启用浏览器演示"}, status=403)
    target_url = os.getenv("RESUME_UI_DEMO_BASE_URL")
    if not target_url and not local_demo:
        return JsonResponse({"status": "unavailable", "message": "服务器尚未配置演示环境地址"}, status=503)
    target_url = target_url or f"http://127.0.0.1:{request.get_port()}"
    if not auth_mutations_are_allowed(target_url):
        return JsonResponse({"status": "unavailable", "message": "此流程会创建 QA 测试账号，请先配置独立演示环境并允许测试造数"}, status=503)
    if not _resume_demo_lock.acquire(blocking=False):
        return JsonResponse({"status": "busy", "message": "已有演示正在执行，请稍后再试"}, status=409)
    try:
        command = [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            "qa/pytest.ini",
            "qa/ui/test_authenticated_bmi_flow.py::test_user_registers_logs_in_and_calculates_bmi_through_the_visible_ui",
            "-v",
            "-o",
            "addopts=",
            "--slowmo",
            "1000",
        ]
        if local_demo and sys.platform == "darwin":
            command += ["--headed"]
            command += ["--browser-channel", "chrome"]
        env = os.environ.copy()
        env["BASE_URL"] = target_url
        result = subprocess.run(command, cwd=settings.BASE_DIR, env=env, capture_output=True, text=True, timeout=90)
        return JsonResponse(
            {
                "status": "passed" if result.returncode == 0 else "failed",
                "message": "演示通过" if result.returncode == 0 else "演示失败，请查看执行日志",
                "output": (result.stdout + result.stderr)[-6000:],
            }
        )
    except subprocess.TimeoutExpired:
        return JsonResponse({"status": "failed", "message": "执行超过 90 秒，已停止", "output": "执行超时"}, status=504)
    except OSError:
        return JsonResponse({"status": "failed", "message": "无法启动测试进程，请检查 Python 环境", "output": "测试进程启动失败"}, status=500)
    finally:
        _resume_demo_lock.release()


def version_history_view(request):
    """版本迭代记录页面"""
    return render(request, "version_history.html")


def help_page_view(request):
    """帮助中心页面"""
    return render(request, "tools/help_page.html")


def custom_static_serve(request, path):
    """自定义静态文件服务，禁用缓存"""
    response = serve(request, path, document_root=settings.STATIC_ROOT)
    # 添加缓存控制头，禁用缓存
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response


def public_default_media_serve(request):
    """Serve the bundled default avatar without requiring a login.

    The default avatar is referenced by public pages and is not user content.
    Keep the general media endpoint protected while allowing this one immutable
    asset to render before authentication.
    """
    full_path = os.path.join(settings.MEDIA_ROOT, "vx.jpg")
    if not os.path.isfile(full_path):
        raise Http404("默认头像不存在")

    response = FileResponse(open(full_path, "rb"), content_type="image/jpeg")
    response["Content-Length"] = os.path.getsize(full_path)
    response["Cache-Control"] = "public, max-age=3600"
    response["X-Content-Type-Options"] = "nosniff"
    response["Content-Disposition"] = 'inline; filename="vx.jpg"'
    return response


def secure_media_serve(request, path):
    """安全的媒体文件服务，需要登录验证"""
    try:
        # The bundled default avatar is used on public pages before login.
        if path.rstrip("/") == "vx.jpg":
            return public_default_media_serve(request)

        if not getattr(settings, "AUTH_LOGIN_DISABLED", False) and not request.user.is_authenticated:
            return redirect("home")

        # 检查文件路径是否在媒体目录内
        full_path = os.path.join(settings.MEDIA_ROOT, path)
        if not os.path.exists(full_path):
            raise Http404("文件不存在")

        # 检查文件是否在允许的目录内
        allowed_dirs = [
            "chat_images",
            "chat_files",
            "chat_audio",
            "chat_videos",
            "avatars",
        ]
        path_parts = path.split("/")
        if not any(allowed_dir in path_parts for allowed_dir in allowed_dirs):
            raise Http404("无权访问此文件")

        # 获取文件信息
        file_size = os.path.getsize(full_path)
        file_name = os.path.basename(full_path)

        # 获取MIME类型
        mime_type, _ = mimetypes.guess_type(full_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        # 创建文件响应
        response = FileResponse(open(full_path, "rb"), content_type=mime_type)

        # 设置响应头
        response["Content-Length"] = file_size
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"

        # 如果是图片，允许内联显示
        if mime_type.startswith("image/"):
            response["Content-Disposition"] = f'inline; filename="{file_name}"'
        else:
            response["Content-Disposition"] = f'attachment; filename="{file_name}"'

        return response

    except Exception as e:
        print(f"媒体文件服务错误: {e}")
        raise Http404("文件访问失败")
