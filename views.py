import mimetypes
import json
import os
import subprocess
import sys
import threading

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
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
    """Run the same read-only resume journey exercised by the QA gate."""
    local_demo = settings.DEBUG and request.META.get("REMOTE_ADDR") in {"127.0.0.1", "::1"}
    target_url = f"http://127.0.0.1:{request.get_port() if local_demo else 8000}"
    if not _resume_demo_lock.acquire(blocking=False):
        return JsonResponse({"status": "busy", "message": "已有演示正在执行，请稍后再试"}, status=409)
    cache_lock = False
    try:
        if not local_demo:
            try:
                cache_lock = cache.add("resume:ui-demo:running", "1", timeout=100)
            except Exception:
                return JsonResponse({"status": "unavailable", "message": "演示服务暂不可用，请稍后重试"}, status=503)
            if not cache_lock:
                return JsonResponse({"status": "busy", "message": "已有演示正在执行，请稍后再试"}, status=409)
        env = os.environ.copy()
        env["BASE_URL"] = target_url
        env["QA_DEMO_HEADED"] = "1" if local_demo and sys.platform == "darwin" else "0"
        result = subprocess.run(
            [sys.executable, "-m", "qa.ui.public_demo"],
            cwd=settings.BASE_DIR,
            env=env,
            capture_output=True,
            text=True,
            timeout=90,
        )
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            payload = {"status": "failed", "error": "浏览器进程未返回有效结果"}
        if result.returncode == 0 and payload.get("status") == "passed":
            return JsonResponse(
                {
                    "status": "passed",
                    "message": "只读 UI 自动化演示通过",
                    "output": "\n".join(payload["steps"]),
                    "screenshot": payload["screenshot"],
                }
            )
        return JsonResponse(
            {
                "status": "failed",
                "message": "演示未通过，请检查页面或报告图片",
                "output": payload.get("error", "浏览器执行失败")[-1000:],
            },
            status=500,
        )
    except subprocess.TimeoutExpired:
        return JsonResponse({"status": "failed", "message": "执行超过 90 秒，已停止", "output": "执行超时"}, status=504)
    except OSError:
        return JsonResponse(
            {"status": "failed", "message": "无法启动测试进程，请检查 Python 环境", "output": "测试进程启动失败"}, status=500
        )
    finally:
        if cache_lock:
            cache.delete("resume:ui-demo:running")
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
