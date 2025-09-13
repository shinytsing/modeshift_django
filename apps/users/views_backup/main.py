import json
import re
import logging
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaulttags import register
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.content.views import admin_required

from ..forms import ProfileEditForm, UserRegistrationForm
from ..models import Profile, UserActionLog, UserActivityLog, UserMembership, UserRole, UserSessionStats, UserStatus, UserTheme
from ..services.progressive_captcha_service import ProgressiveCaptchaService
from ..services.rate_limit_service import RateLimitService, rate_limit_decorator

logger = logging.getLogger(__name__)

# 注册模板过滤器
@register.filter
def activity_color(activity_type):
    """返回活动类型对应的Bootstrap颜色类"""
    colors = {
        "login": "success",
        "logout": "secondary",
        "api_access": "info",
        "page_view": "primary",
        "tool_usage": "warning",
        "suggestion_submit": "info",
        "feedback_submit": "info",
        "profile_update": "warning",
    }
    return colors.get(activity_type, "secondary")


@register.filter
def status_color(status_code):
    """返回状态码对应的Bootstrap颜色类"""
    if not status_code:
        return "secondary"
    if status_code >= 200 and status_code < 300:
        return "success"
    elif status_code >= 300 and status_code < 400:
        return "info"
    elif status_code >= 400 and status_code < 500:
        return "warning"
    elif status_code >= 500:
        return "danger"
    return "secondary"


def has_repeated_characters(password):
    """检查密码中是否有连续重复的字符（3个或以上）"""
    count = 1
    for i in range(len(password) - 1):
        if password[i] == password[i + 1]:
            count += 1
            if count >= 3:  # 3个或以上连续重复字符
                return True
        else:
            count = 1
    return False


def has_consecutive_characters(password):
    """检查密码中是否有完全连续的字符"""
    # 检查数字是否是连续的，例如 "12345678"
    if re.search(r'0123456789', password) or re.search(r'1234567890', password):
        return True
    # 检查字母是否是连续的，例如 "abcdefg"
    if re.search(r'abcdefghijklmnopqrstuvwxyz', password.lower()) or re.search(r'zyxwvutsrqponmlkjihgfedcba', password.lower()):
        return True
    return False


def has_two_different_character_types(password):
    """检查密码中是否包含至少两种不同的字符类型"""
    types = {
        "lower": re.search(r"[a-z]", password),
        "upper": re.search(r"[A-Z]", password),
        "digit": re.search(r"\d", password),
        "special": re.search(r"[@$!%*?&]", password),  # 可以自定义特殊字符
    }
    return sum(bool(t) for t in types.values()) >= 2


# register_view 已删除，使用现代化弹窗登录


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)  # 退出用户
        messages.info(request, "你已成功登出。")  # 添加登出成功的消息
    else:
        messages.warning(request, "请先登录。")  # 添加没有登录时的提示
    return redirect("home")  # 重定向到首页或其他指定页面


# register 函数已删除，使用现代化弹窗登录


# user_login 函数已删除，使用现代化弹窗登录


def modern_login_modal(request):
    """现代化弹窗登录视图"""
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        form_type = request.POST.get("form_type", "login")
        
        if form_type == "register":
            return handle_modal_register(request)
        else:
            return handle_modal_login(request)
    
    # 如果是直接访问登录URL，重定向到首页
    # 登录弹窗应该通过JavaScript调用，而不是直接访问
    return redirect("/")


def handle_modal_register(request):
    """处理弹窗注册逻辑"""
    # 检查速率限制
    is_allowed, remaining, reset_time = RateLimitService.check_rate_limit(
        request, 'register', max_attempts=3, window_minutes=15
    )
    
    if not is_allowed:
        messages.error(request, f"❌ 注册尝试次数过多，请{15}分钟后再试")
        return redirect("/")
    
    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")
    password_confirm = request.POST.get("password_confirm", "")
    email = request.POST.get("email", "").strip()
    
    # 详细的输入验证
    if not username:
        messages.error(request, "❌ 用户名不能为空，请输入用户名")
        return redirect("/")
    
    if not password:
        messages.error(request, "❌ 密码不能为空，请输入密码")
        return redirect("/")
    
    if not password_confirm:
        messages.error(request, "❌ 请确认密码")
        return redirect("/")
    
    # 用户名验证
    if len(username) < 3:
        messages.error(request, "❌ 用户名至少需要3个字符")
        return redirect("/")
    
    if len(username) > 30:
        messages.error(request, "❌ 用户名不能超过30个字符")
        return redirect("/")
    
    # 检查用户名格式（只允许字母、数字、下划线）
    import re
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        messages.error(request, "❌ 用户名只能包含字母、数字和下划线")
        return redirect("/")
    
    # 检查敏感词
    sensitive_words = ["admin", "root", "system", "test", "user", "guest"]
    if username.lower() in sensitive_words:
        messages.error(request, "❌ 用户名包含敏感词，请选择其他用户名")
        return redirect("/")
    
    # 密码验证
    if password != password_confirm:
        messages.error(request, "❌ 两次输入的密码不一致，请重新确认")
        return redirect("/")
    
    if len(password) < 8:
        messages.error(request, "❌ 密码长度至少需要8个字符")
        return redirect("/")
    
    if len(password) > 128:
        messages.error(request, "❌ 密码长度不能超过128个字符")
        return redirect("/")
    
    # 密码复杂度检查
    if not re.search(r"[A-Za-z]", password):
        messages.error(request, "❌ 密码必须包含至少一个字母")
        return redirect("/")
    
    if not re.search(r"\d", password):
        messages.error(request, "❌ 密码必须包含至少一个数字")
        return redirect("/")
    
    # 检查常见弱密码
    weak_passwords = [
        "password", "123456", "qwerty", "admin", "12345678", "password123",
        "123456789", "1234567890", "qwertyuiop", "asdfghjkl", "zxcvbnm",
        "111111", "000000", "123123", "abc123", "password1", "admin123",
        "root", "user", "guest", "test", "demo", "sample", "default",
        "1234", "12345", "1234567", "123456789", "987654321", "654321",
        "qwerty123", "asdf1234", "zxcv1234", "iloveyou", "welcome",
        "monkey", "dragon", "master", "hello", "letmein", "princess",
        "qazwsx", "michael", "jordan", "harley", "ranger", "shadow",
        "sunshine", "superman", "qwertyui", "trustno1", "batman",
        "thomas", "hockey", "ranger", "daniel", "hannah", "maggie",
        "jessica", "charlie", "jordan", "michelle", "andrew", "joshua",
        "angela", "kevin", "steven", "brian", "nicole", "kimberly",
        "christina", "jennifer", "elizabeth", "robert", "anthony",
        "mark", "donald", "steven", "paul", "andrew", "joshua",
        "kenneth", "kevin", "brian", "george", "timothy", "jose",
        "jeffrey", "ryan", "jacob", "gary", "nicholas", "eric",
        "jonathan", "stephen", "larry", "justin", "scott", "brandon",
        "benjamin", "samuel", "gregory", "frank", "raymond", "alexander",
        "patrick", "jack", "dennis", "jerry", "tyler", "aaron",
        "jose", "henry", "douglas", "adam", "peter", "nathan",
        "zachary", "kyle", "walter", "harold", "jeremy", "ethan",
        "carl", "keith", "roger", "gerald", "arthur", "lawrence",
        "sean", "christian", "wayne", "arthur", "ryan", "louis",
        "philip", "bobby", "johnny", "ralph", "eugene", "howard",
        "juan", "roy", "victor", "arthur", "albert", "arthur",
        "arthur", "arthur", "arthur", "arthur", "arthur", "arthur"
    ]
    if password.lower() in weak_passwords:
        messages.error(request, "❌ 密码过于简单，请选择更复杂的密码")
        return redirect("/")
    
    if has_repeated_characters(password):
        messages.error(request, "❌ 密码不能包含连续重复的字符")
        return redirect("/")
    
    if not has_two_different_character_types(password):
        messages.error(request, "❌ 密码必须包含至少两种不同的字符类型（如字母和数字）")
        return redirect("/")
    
    # 邮箱验证（如果提供）
    if email:
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            messages.error(request, "❌ 邮箱格式不正确")
            return redirect("/")
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "❌ 该邮箱已被注册，请使用其他邮箱")
            return redirect("/")
    
    # 检查用户名是否已存在
    if User.objects.filter(username=username).exists():
        messages.error(request, "❌ 用户名已存在，请选择其他用户名")
        return redirect("/")
    
    try:
        # 创建用户
        user = User.objects.create_user(username=username, password=password, email=email)
        
        # 创建用户相关记录
        try:
            UserRole.objects.create(user=user, role="user")
            UserStatus.objects.create(user=user, status="active")
            UserMembership.objects.create(user=user, membership_type="free")
            Profile.objects.create(user=user)
        except Exception as e:
            logger.error(f"Failed to create user related records: {e}")
            # 如果相关记录创建失败，删除用户
            user.delete()
            messages.error(request, "❌ 注册失败，请稍后重试")
            return redirect("/")
        
        # 记录注册活动
        try:
            from ..models import UserActivityLog
            UserActivityLog.objects.create(
                user=user,
                activity_type="register",
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={"registration_method": "modal", "success": True},
            )
        except Exception as e:
            logger.error(f"Failed to log registration activity: {e}")
        
        # 自动登录用户
        try:
            login(request, user)
            
            # 新用户注册成功，应该显示欢迎窗口
            request.session['show_welcome_modal'] = True
            
            messages.success(request, f"🎉 欢迎 {username}！注册成功并已自动登录。您现在可以开始使用所有功能了！")
        except Exception as e:
            logger.error(f"Failed to auto-login user: {e}")
            messages.success(request, f"✅ 注册成功！请手动登录。")
        
        next_url = request.GET.get("next", "/")
        # 如果next参数是相对路径，确保以/开头
        if next_url and not next_url.startswith('/'):
            next_url = '/' + next_url
        return redirect(next_url)
        
    except Exception as e:
        logger.error(f"Registration failed: {e}", exc_info=True)
        
        # 记录详细的错误信息用于调试
        logger.error(f"Registration attempt details - Username: {username}, Email: {email}, IP: {request.META.get('REMOTE_ADDR')}")
        
        # 根据不同的异常类型提供不同的错误信息
        error_message = str(e).lower()
        if "username" in error_message and "already exists" in error_message:
            messages.error(request, "❌ 用户名已存在，请选择其他用户名")
        elif "email" in error_message and "already exists" in error_message:
            messages.error(request, "❌ 该邮箱已被注册，请使用其他邮箱")
        elif "password" in error_message:
            messages.error(request, "❌ 密码格式不正确")
        elif "username" in error_message:
            messages.error(request, "❌ 用户名格式不正确")
        elif "database" in error_message or "connection" in error_message:
            messages.error(request, "❌ 数据库连接失败，请稍后重试")
            logger.critical(f"Database error during registration: {e}")
        elif "integrity" in error_message:
            messages.error(request, "❌ 数据完整性错误，请检查输入信息")
        else:
            messages.error(request, "❌ 注册失败，请检查输入信息或稍后重试")
            logger.error(f"Unknown registration error: {e}")
        
        return redirect("/")


def handle_modal_login(request):
    """处理弹窗登录逻辑"""
    # 检查速率限制
    is_allowed, remaining, reset_time = RateLimitService.check_rate_limit(
        request, 'login', max_attempts=5, window_minutes=15
    )
    
    if not is_allowed:
        messages.error(request, f"❌ 登录尝试次数过多，请{15}分钟后再试")
        return redirect("/")
    
    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")
    
    # 详细的输入验证
    if not username:
        messages.error(request, "❌ 请输入用户名")
        return redirect("/")
    
    if not password:
        messages.error(request, "❌ 请输入密码")
        return redirect("/")
    
    # 检查用户名长度
    if len(username) < 3:
        messages.error(request, "❌ 用户名格式不正确")
        return redirect("/")
    
    # 检查密码长度
    if len(password) < 1:
        messages.error(request, "❌ 密码不能为空")
        return redirect("/")
    
    # 尝试认证用户
    user = authenticate(request, username=username, password=password)
    if user is not None:
        # 检查用户状态
        if not user.is_active:
            messages.error(request, "❌ 账户已被禁用，请联系管理员")
            return redirect("/")
        
        # 登录成功
        login(request, user)
        
        # 检查是否应该显示欢迎窗口
        from ..models import UserWelcomeModal
        should_show_welcome = UserWelcomeModal.should_show_welcome(user)
        
        # 记录登录活动
        try:
            from ..models import UserActivityLog
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                ip = x_forwarded_for.split(",")[0]
            else:
                ip = request.META.get("REMOTE_ADDR")
            
            UserActivityLog.objects.create(
                user=user,
                activity_type="login",
                ip_address=ip,
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                details={"login_method": "modal_password", "success": True, "show_welcome": should_show_welcome},
            )
        except Exception as e:
            logger.error(f"Failed to log login activity: {e}")
        
        messages.success(request, f"✅ 欢迎回来，{user.username}！您已成功登录。")
        
        # 如果应该显示欢迎窗口，在session中标记
        if should_show_welcome:
            request.session['show_welcome_modal'] = True
        
        next_url = request.GET.get("next", "/")
        # 如果next参数是相对路径，确保以/开头
        if next_url and not next_url.startswith('/'):
            next_url = '/' + next_url
        return redirect(next_url)
    else:
        # 登录失败 - 提供更详细的错误信息并记录安全日志
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 记录失败的登录尝试
        logger.warning(f"Failed login attempt - Username: {username}, IP: {ip_address}, User-Agent: {user_agent}")
        
        # 检查用户名是否存在
        if User.objects.filter(username=username).exists():
            messages.error(request, "❌ 密码错误，请检查密码是否正确")
            logger.info(f"Login failed: incorrect password for existing user '{username}' from IP {ip_address}")
        else:
            messages.error(request, "❌ 用户名不存在，请检查用户名是否正确")
            logger.info(f"Login failed: non-existent username '{username}' from IP {ip_address}")
        
        # 记录失败的活动日志
        try:
            from ..models import UserActivityLog
            UserActivityLog.objects.create(
                user=None,  # 未认证用户
                activity_type="login_failed",
                ip_address=ip_address,
                user_agent=user_agent,
                details={"username": username, "reason": "authentication_failed"},
            )
        except Exception as log_error:
            logger.error(f"Failed to log login failure: {log_error}")
        
        return redirect("/")


def terms_of_service_api(request):
    """服务条款API"""
    try:
        import os
        from django.conf import settings
        
        # 读取服务条款文件
        terms_file = os.path.join(settings.BASE_DIR, 'apps', 'users', 'resources', 'terms_of_service.html')
        
        if os.path.exists(terms_file):
            with open(terms_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return JsonResponse({"success": True, "content": content})
        else:
            return JsonResponse({"success": False, "message": "服务条款文件不存在"}, status=404)
            
    except Exception as e:
        return JsonResponse({"success": False, "message": f"读取服务条款失败: {str(e)}"}, status=500)


def privacy_policy_api(request):
    """隐私政策API"""
    try:
        import os
        from django.conf import settings
        
        # 读取隐私政策文件
        privacy_file = os.path.join(settings.BASE_DIR, 'apps', 'users', 'resources', 'privacy_policy.html')
        
        if os.path.exists(privacy_file):
            with open(privacy_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return JsonResponse({"success": True, "content": content})
        else:
            return JsonResponse({"success": False, "message": "隐私政策文件不存在"}, status=404)
            
    except Exception as e:
        return JsonResponse({"success": False, "message": f"读取隐私政策失败: {str(e)}"}, status=500)


def test_modern_login(request):
    """现代化登录测试页面"""
    return render(request, "test_modern_login.html")

# handle_register 函数已删除，使用现代化弹窗登录

# handle_login 函数已删除，使用现代化弹窗登录


def user_logout(request):
    if request.user.is_authenticated:
        user_id = request.user.id

        # 记录登出活动
        try:
            from django.core.cache import cache

            from .models import UserActivityLog, UserSessionStats

            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                ip = x_forwarded_for.split(",")[0]
            else:
                ip = request.META.get("REMOTE_ADDR")

            UserActivityLog.objects.create(
                user=request.user,
                activity_type="logout",
                ip_address=ip,
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                details={"logout_method": "manual"},
            )

            # 结束活跃会话
            active_session = UserSessionStats.objects.filter(user=request.user, is_active=True).first()
            if active_session:
                active_session.is_active = False
                active_session.session_end = timezone.now()
                active_session.duration = int((active_session.session_end - active_session.session_start).total_seconds())
                active_session.save()

            # 清除用户相关的缓存token和数据
            cache_keys_to_clear = [
                f"boss_user_token_{user_id}",  # Boss直聘登录token
                f"user_profile_{user_id}",  # 用户配置缓存
                f"user_theme_{user_id}",  # 用户主题缓存
                f"user_session_{user_id}",  # 用户会话缓存
            ]

            for cache_key in cache_keys_to_clear:
                try:
                    cache.delete(cache_key)
                except Exception as cache_error:
                    print(f"清除缓存失败 {cache_key}: {cache_error}")

        except Exception as e:
            print(f"记录登出活动失败: {e}")

    # 获取当前会话键，以便在前端清除
    request.session.session_key

    # Django内置登出（清除session和认证状态）
    logout(request)

    # 添加登出成功消息
    messages.success(request, "您已成功登出，所有认证信息已清除")

    # 创建响应并添加自定义头，通知前端清除token
    response = redirect("home")
    response["X-Logout-Success"] = "true"
    response["X-Clear-Storage"] = "true"

    return response


@login_required
def profile_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    return render(request, "users/profile.html", {"profile": profile})


@login_required
def profile_edit(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == "POST":
        form = ProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "个人资料已更新")
            return redirect("profile")
    else:
        form = ProfileEditForm(instance=profile)

    return render(request, "users/profile_edit.html", {"form": form})


# 管理员用户管理视图
@login_required
@admin_required
def admin_user_management(request):
    # 获取所有用户角色信息，按创建时间倒序排列
    user_roles = (
        UserRole.objects.select_related("user", "user__profile")
        .prefetch_related("user__status", "user__membership")
        .order_by("-user__date_joined")
    )

    # 统计信息

    from django.utils import timezone

    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()

    # VIP用户统计
    vip_users = UserMembership.objects.filter(membership_type="vip", is_active=True, end_date__gt=timezone.now()).count()

    # 今日新增用户
    today = timezone.now().date()
    today_users = User.objects.filter(date_joined__date=today).count()

    # 分页
    paginator = Paginator(user_roles, 20)  # 每页显示20个用户
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "users/admin_user_management.html",
        {
            "page_obj": page_obj,
            "total_users": total_users,
            "active_users": active_users,
            "vip_users": vip_users,
            "today_users": today_users,
        },
    )


@login_required
@admin_required
def admin_user_detail(request, user_id):
    user_detail = get_object_or_404(User, id=user_id)
    user_logs = UserActionLog.objects.filter(target_user=user_detail).select_related("admin_user").order_by("-created_at")[:10]

    return render(request, "users/admin_user_detail.html", {"user_detail": user_detail, "user_logs": user_logs})


# 管理员用户管理API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_change_user_status_api(request, user_id):
    try:
        data = json.loads(request.body)
        status = data.get("status")
        reason = data.get("reason", "")

        target_user = get_object_or_404(User, id=user_id)
        user_status, created = UserStatus.objects.get_or_create(user=target_user)

        old_status = user_status.status
        user_status.status = status
        user_status.reason = reason

        if status == "suspended":
            user_status.suspended_until = timezone.now() + timedelta(days=7)  # 默认暂停7天
        else:
            user_status.suspended_until = None

        user_status.save()

        # 记录操作日志
        UserActionLog.objects.create(
            admin_user=request.user,
            target_user=target_user,
            action="status_change",
            details=f"状态从 {old_status} 变更为 {status}，原因：{reason}",
        )

        return JsonResponse({"success": True, "message": f"用户状态已更新为 {status}"}, content_type="application/json")

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_change_membership_api(request, user_id):
    try:
        data = json.loads(request.body)
        membership_type = data.get("membership_type")
        days = data.get("days", 30)
        note = data.get("note", "")

        target_user = get_object_or_404(User, id=user_id)
        membership, created = UserMembership.objects.get_or_create(user=target_user)

        old_type = membership.membership_type
        membership.membership_type = membership_type
        membership.is_active = True

        if days > 0:
            membership.end_date = timezone.now() + timedelta(days=days)
        else:
            membership.end_date = None

        membership.save()

        # 记录操作日志
        UserActionLog.objects.create(
            admin_user=request.user,
            target_user=target_user,
            action="membership_change",
            details=f"会员类型从 {old_type} 变更为 {membership_type}，有效期：{days}天，备注：{note}",
        )

        return JsonResponse({"success": True, "message": f"用户会员已更新为 {membership_type}"}, content_type="application/json")

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_change_role_api(request, user_id):
    try:
        data = json.loads(request.body)
        role = data.get("role")
        note = data.get("note", "")

        target_user = get_object_or_404(User, id=user_id)
        user_role, created = UserRole.objects.get_or_create(user=target_user)

        old_role = user_role.role
        user_role.role = role
        user_role.save()

        # 记录操作日志
        UserActionLog.objects.create(
            admin_user=request.user,
            target_user=target_user,
            action="role_change",
            details=f"角色从 {old_role} 变更为 {role}，备注：{note}",
        )

        return JsonResponse({"success": True, "message": f"用户角色已更新为 {role}"}, content_type="application/json")

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_delete_user_api(request, user_id):
    try:
        data = json.loads(request.body)
        reason = data.get("reason", "")

        target_user = get_object_or_404(User, id=user_id)

        # 软删除：将状态设置为deleted
        user_status, created = UserStatus.objects.get_or_create(user=target_user)
        user_status.status = "deleted"
        user_status.reason = reason
        user_status.save()

        # 记录操作日志
        UserActionLog.objects.create(
            admin_user=request.user, target_user=target_user, action="account_delete", details=f"删除账号，原因：{reason}"
        )

        return JsonResponse({"success": True, "message": "用户账号已删除"}, content_type="application/json")

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


# 获取用户操作日志API
@login_required
@admin_required
def admin_user_logs(request):
    logs = UserActionLog.objects.select_related("admin_user", "target_user").order_by("-created_at")
    paginator = Paginator(logs, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "users/admin_user_logs.html", {"page_obj": page_obj})


# 批量操作API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_batch_operation_api(request):
    try:
        data = json.loads(request.body)
        user_ids = data.get("user_ids", [])
        operation = data.get("operation")
        note = data.get("note", "")

        if not user_ids:
            return JsonResponse({"success": False, "message": "请选择要操作的用户"}, status=400, content_type="application/json")

        success_count = 0
        failed_count = 0

        for user_id in user_ids:
            try:
                target_user = User.objects.get(id=user_id)

                if operation == "suspend":
                    # 批量暂停
                    user_status, created = UserStatus.objects.get_or_create(user=target_user)
                    user_status.status = "suspended"
                    user_status.suspended_until = timezone.now() + timedelta(days=7)
                    user_status.save()

                    UserActionLog.objects.create(
                        admin_user=request.user,
                        target_user=target_user,
                        action="batch_suspended",
                        details=f"批量暂停，备注：{note}",
                    )

                elif operation == "activate":
                    # 批量激活
                    user_status, created = UserStatus.objects.get_or_create(user=target_user)
                    user_status.status = "active"
                    user_status.suspended_until = None
                    user_status.save()

                    UserActionLog.objects.create(
                        admin_user=request.user,
                        target_user=target_user,
                        action="batch_activated",
                        details=f"批量激活，备注：{note}",
                    )

                elif operation == "upgrade_membership":
                    # 批量升级会员
                    membership, created = UserMembership.objects.get_or_create(user=target_user)
                    membership.membership_type = "premium"
                    membership.is_active = True
                    membership.end_date = timezone.now() + timedelta(days=30)
                    membership.save()

                    UserActionLog.objects.create(
                        admin_user=request.user,
                        target_user=target_user,
                        action="batch_upgraded",
                        details=f"批量升级会员，备注：{note}",
                    )

                success_count += 1

            except User.DoesNotExist:
                failed_count += 1
                continue

        return JsonResponse(
            {"success": True, "message": f"批量操作完成，成功：{success_count}，失败：{failed_count}"},
            content_type="application/json",
        )

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


# 用户监控管理页面
@login_required
@admin_required
def admin_user_monitoring(request):
    from datetime import timedelta

    from django.db.models import Avg, Count
    from django.utils import timezone

    from .models import APIUsageStats, UserActivityLog, UserSessionStats

    # 获取今日数据
    today = timezone.now().date()

    # 今日活跃用户
    today_active_users = UserActivityLog.objects.filter(created_at__date=today).values("user").distinct().count()

    # 今日登录次数
    today_logins = UserActivityLog.objects.filter(activity_type="login", created_at__date=today).count()

    # 今日API调用次数
    today_api_calls = APIUsageStats.objects.filter(created_at__date=today).count()

    # 当前在线用户
    online_users = UserSessionStats.objects.filter(
        is_active=True, session_start__gte=timezone.now() - timedelta(minutes=30)
    ).count()

    # 最近活动
    recent_activities = UserActivityLog.objects.select_related("user").order_by("-created_at")[:20]

    # API使用统计
    api_stats = (
        APIUsageStats.objects.filter(created_at__date=today)
        .values("endpoint", "method")
        .annotate(count=Count("id"), avg_response_time=Avg("response_time"))
        .order_by("-count")[:10]
    )

    # 活跃会话
    active_sessions = UserSessionStats.objects.select_related("user").filter(is_active=True).order_by("-session_start")

    return render(
        request,
        "users/admin_user_monitoring.html",
        {
            "today_active_users": today_active_users,
            "today_logins": today_logins,
            "today_api_calls": today_api_calls,
            "online_users": online_users,
            "recent_activities": recent_activities,
            "api_stats": api_stats,
            "active_sessions": active_sessions,
        },
    )


# 用户监控统计API
@csrf_exempt
@require_http_methods(["GET"])
@login_required
@admin_required
def admin_monitoring_stats_api(request):
    from datetime import timedelta

    from django.db.models import Avg, Count
    from django.utils import timezone

    from .models import APIUsageStats, UserActivityLog, UserSessionStats

    try:
        # 获取今日数据
        today = timezone.now().date()

        # 今日活跃用户
        today_active_users = UserActivityLog.objects.filter(created_at__date=today).values("user").distinct().count()

        # 今日登录次数
        today_logins = UserActivityLog.objects.filter(activity_type="login", created_at__date=today).count()

        # 今日API调用次数
        today_api_calls = APIUsageStats.objects.filter(created_at__date=today).count()

        # 当前在线用户
        online_users = UserSessionStats.objects.filter(
            is_active=True, session_start__gte=timezone.now() - timedelta(minutes=30)
        ).count()

        # 最近活动
        recent_activities = UserActivityLog.objects.select_related("user").order_by("-created_at")[:20]
        activities_data = []
        for activity in recent_activities:
            activities_data.append(
                {
                    "user_name": activity.user.username if activity.user else "匿名用户",
                    "activity_type": activity.activity_type,
                    "activity_type_display": activity.get_activity_type_display(),
                    "ip_address": activity.ip_address,
                    "endpoint": activity.endpoint,
                    "created_at": activity.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "status_code": activity.status_code,
                }
            )

        # API使用统计
        api_stats = (
            APIUsageStats.objects.filter(created_at__date=today)
            .values("endpoint", "method")
            .annotate(count=Count("id"), avg_response_time=Avg("response_time"))
            .order_by("-count")[:10]
        )

        api_stats_data = []
        for stat in api_stats:
            api_stats_data.append(
                {
                    "endpoint": stat["endpoint"],
                    "method": stat["method"],
                    "count": stat["count"],
                    "avg_response_time": float(stat["avg_response_time"] or 0),
                }
            )

        # 活跃会话
        active_sessions = UserSessionStats.objects.select_related("user").filter(is_active=True).order_by("-session_start")

        sessions_data = []
        for session in active_sessions:
            sessions_data.append(
                {
                    "user_id": session.user.id,
                    "user_name": session.user.username,
                    "session_start": session.session_start.strftime("%Y-%m-%d %H:%M:%S"),
                    "ip_address": session.ip_address,
                    "user_agent": session.user_agent,
                    "is_active": session.is_active,
                }
            )

        return JsonResponse(
            {
                "success": True,
                "stats": {
                    "today_active_users": today_active_users,
                    "today_logins": today_logins,
                    "today_api_calls": today_api_calls,
                    "online_users": online_users,
                },
                "recent_activities": activities_data,
                "api_stats": api_stats_data,
                "active_sessions": sessions_data,
            },
            content_type="application/json",
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# 强制登出用户API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_force_logout_api(request, user_id):
    import json

    try:
        data = json.loads(request.body)
        reason = data.get("reason", "管理员强制登出")

        # 获取用户
        user = get_object_or_404(User, id=user_id)

        # 结束用户的所有活跃会话
        active_sessions = UserSessionStats.objects.filter(user=user, is_active=True)

        for session in active_sessions:
            session.is_active = False
            session.session_end = timezone.now()
            session.duration = int((session.session_end - session.session_start).total_seconds())
            session.save()

        # 记录强制登出活动
        UserActivityLog.objects.create(
            user=user,
            activity_type="logout",
            ip_address=request.client_ip if hasattr(request, "client_ip") else None,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            details={"logout_method": "force", "reason": reason, "admin_user": request.user.username},
        )

        # 记录管理员操作
        UserActionLog.objects.create(
            admin_user=request.user,
            target_user=user,
            action="force_logout",
            details=f"强制登出用户 {user.username}，原因：{reason}",
        )

        return JsonResponse({"success": True, "message": f"用户 {user.username} 已被强制登出"}, content_type="application/json")

    except json.JSONDecodeError:
        return JsonResponse({"error": "无效的JSON数据"}, status=400, content_type="application/json")
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# 主题API
@csrf_exempt
@require_http_methods(["GET", "POST"])
def theme_api(request):
    """用户主题设置API"""
    # 检查用户是否登录
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "用户未登录"}, status=401, content_type="application/json")
    
    try:
        if request.method == "GET":
            # 获取用户当前主题
            user_theme, created = UserTheme.objects.get_or_create(
                user=request.user, defaults={"mode": "work", "theme_style": "default"}
            )

            return JsonResponse(
                {
                    "success": True,
                    "data": {
                        "mode": user_theme.mode,
                        "theme_style": user_theme.theme_style,
                        "subtitle": user_theme.subtitle,
                        "switch_count": user_theme.switch_count,
                        "last_switch_time": user_theme.last_switch_time.isoformat() if user_theme.last_switch_time else None,
                    },
                }
            )

        elif request.method == "POST":
            # 更新用户主题
            data = json.loads(request.body)
            mode = data.get("mode", "work")

            # 验证模式是否有效
            valid_modes = ["work", "life", "training", "emo", "cyberpunk"]
            if mode not in valid_modes:
                return JsonResponse({"success": False, "error": "无效的主题模式"}, status=400, content_type="application/json")

            # 更新或创建用户主题
            user_theme, created = UserTheme.objects.get_or_create(
                user=request.user, defaults={"mode": mode, "theme_style": "default"}
            )

            if not created:
                # 记录切换统计
                if user_theme.mode != mode:
                    user_theme.switch_count += 1
                    user_theme.last_switch_time = timezone.now()
                user_theme.mode = mode
                user_theme.save()

            return JsonResponse(
                {
                    "success": True,
                    "data": {
                        "mode": user_theme.mode,
                        "theme_style": user_theme.theme_style,
                        "subtitle": user_theme.subtitle,
                        "switch_count": user_theme.switch_count,
                        "last_switch_time": user_theme.last_switch_time.isoformat() if user_theme.last_switch_time else None,
                    },
                }
            )

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"}, status=400, content_type="application/json")
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# 头像上传API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def upload_avatar(request):
    """用户头像上传API"""
    try:
        # 检查是否有文件上传
        if "avatar" not in request.FILES:
            return JsonResponse({"success": False, "message": "请选择要上传的头像文件"}, status=400, content_type="application/json")

        avatar_file = request.FILES["avatar"]

        # 验证文件类型
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if avatar_file.content_type not in allowed_types:
            return JsonResponse(
                {"success": False, "message": "只支持 JPG、PNG、GIF、WebP 格式的图片"},
                status=400,
                content_type="application/json",
            )

        # 验证文件大小（限制为5MB）
        if avatar_file.size > 5 * 1024 * 1024:
            return JsonResponse({"success": False, "message": "头像文件大小不能超过5MB"}, status=400, content_type="application/json")

        # 获取或创建用户资料
        try:
            profile, created = Profile.objects.get_or_create(user=request.user, defaults={"user": request.user})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"获取用户资料失败: {str(e)}"}, status=500)

        # 图片处理：压缩和调整大小
        try:
            import io
            import os

            from django.core.files.base import ContentFile

            from PIL import Image

            # 打开图片
            img = Image.open(avatar_file)

            # 转换为RGB模式（如果是RGBA，去除透明通道）
            if img.mode in ("RGBA", "LA", "P"):
                # 创建白色背景
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # 计算新的尺寸（强制正方形）
            target_size = (40, 40)  # 目标尺寸40x40像素

            # 计算缩放比例，取宽高的最大值
            width, height = img.size
            scale = max(target_size[0] / width, target_size[1] / height)
            new_width = int(width * scale)
            new_height = int(height * scale)

            # 先缩放到能包含目标尺寸的大小
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 然后裁剪成正方形
            left = (new_width - target_size[0]) // 2
            top = (new_height - target_size[1]) // 2
            right = left + target_size[0]
            bottom = top + target_size[1]

            # 裁剪成正方形
            img = img.crop((left, top, right, bottom))

            # 保存压缩后的图片到内存
            output = io.BytesIO()

            # 根据原始文件类型选择保存格式
            file_extension = os.path.splitext(avatar_file.name)[1].lower()
            if file_extension in [".jpg", ".jpeg"]:
                img.save(output, format="JPEG", quality=85, optimize=True)
                file_extension = ".jpg"
            elif file_extension == ".png":
                img.save(output, format="PNG", optimize=True)
            elif file_extension == ".webp":
                img.save(output, format="WEBP", quality=85, optimize=True)
            else:
                # 默认保存为JPEG
                img.save(output, format="JPEG", quality=85, optimize=True)
                file_extension = ".jpg"

            output.seek(0)

            # 生成文件名
            filename = f"avatar_{request.user.id}_{int(timezone.now().timestamp())}{file_extension}"

            # 创建ContentFile对象
            content_file = ContentFile(output.getvalue(), filename)

            # 保存到用户资料
            profile.avatar.save(filename, content_file, save=True)

            # 关闭图片对象
            img.close()
            output.close()

        except ImportError:
            # 如果没有Pillow库，使用原始文件
            import os

            file_extension = os.path.splitext(avatar_file.name)[1]
            if not file_extension:
                file_extension = ".jpg"

            filename = f"avatar_{request.user.id}_{int(timezone.now().timestamp())}{file_extension}"
            profile.avatar.save(filename, avatar_file, save=True)

        except Exception as e:
            return JsonResponse({"success": False, "message": f"图片处理失败: {str(e)}"}, status=500)

        # 记录用户操作
        try:
            UserActionLog.objects.create(user=request.user, action="avatar_upload", details=f"上传新头像: {filename}")
        except Exception as e:
            print(f"Failed to log avatar upload: {e}")

        return JsonResponse(
            {"success": True, "message": "头像上传成功", "avatar_url": profile.avatar.url if profile.avatar else None},
            content_type="application/json",
        )

    except Exception as e:
        import traceback

        print(f"Avatar upload error: {e}")
        print(traceback.format_exc())
        return JsonResponse({"success": False, "message": f"头像上传失败: {str(e)}"}, status=500)


# 头像上传测试页面
@login_required
def avatar_test_view(request):
    """头像上传测试页面"""
    return render(request, "avatar_test.html")


# 点击验证码相关视图


# 渐进式验证码相关视图
@csrf_exempt
@require_http_methods(["GET", "POST"])
def generate_progressive_captcha(request):
    """生成渐进式验证码"""
    try:
        # 确保session存在
        if not request.session.session_key:
            request.session.create()
            print(f"生成验证码时创建新session: {request.session.session_key}")

        captcha_service = ProgressiveCaptchaService()
        session_key = request.session.session_key

        if not session_key:
            return JsonResponse({"success": False, "message": "会话创建失败，请刷新页面重试"}, status=500)

        result = captcha_service.generate_captcha(session_key)
        print(f"生成验证码结果: {result}")
        return JsonResponse(result)

    except Exception as e:
        print(f"生成验证码异常: {str(e)}")
        return JsonResponse({"success": False, "message": f"生成验证码失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def verify_progressive_captcha(request):
    """验证渐进式验证码"""
    try:
        data = json.loads(request.body)
        captcha_id = data.get("captcha_id")
        captcha_type = data.get("captcha_type")
        user_input = data.get("user_input")

        # 添加调试信息
        print(f"验证码验证请求: captcha_id={captcha_id}, captcha_type={captcha_type}, user_input={user_input}")

        if not all([captcha_id, captcha_type, user_input is not None]):
            print(f"参数检查失败: captcha_id={captcha_id}, captcha_type={captcha_type}, user_input={user_input}")
            return JsonResponse({"success": False, "message": "缺少必要的验证参数"})

        # 确保session存在
        if not request.session.session_key:
            request.session.create()
            print(f"创建新session: {request.session.session_key}")

        captcha_service = ProgressiveCaptchaService()
        session_key = request.session.session_key

        if not session_key:
            return JsonResponse({"success": False, "message": "会话创建失败，请刷新页面重试"})

        result = captcha_service.verify_captcha(session_key, captcha_id, captcha_type, user_input)

        # 如果验证成功，在session中标记
        if result.get("success"):
            request.session["progressive_captcha_verified"] = True
            request.session.save()  # 确保session被保存

        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "请求数据格式错误"}, status=400)
    except Exception as e:
        print(f"验证码验证异常: {str(e)}")
        return JsonResponse({"success": False, "message": f"验证失败: {str(e)}"}, status=500)


# 用户登出API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def user_logout_api(request):
    """用户登出API - 清除所有认证信息和token"""
    try:
        user_id = request.user.id

        # 记录登出活动
        try:
            from django.core.cache import cache

            from .models import UserActivityLog, UserSessionStats

            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                ip = x_forwarded_for.split(",")[0]
            else:
                ip = request.META.get("REMOTE_ADDR")

            UserActivityLog.objects.create(
                user=request.user,
                activity_type="logout",
                ip_address=ip,
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                details={"logout_method": "api"},
            )

            # 结束活跃会话
            active_sessions = UserSessionStats.objects.filter(user=request.user, is_active=True)

            for session in active_sessions:
                session.is_active = False
                session.session_end = timezone.now()
                session.duration = int((session.session_end - session.session_start).total_seconds())
                session.save()

            # 清除用户相关的缓存token和数据
            cache_keys_to_clear = [
                f"boss_user_token_{user_id}",  # Boss直聘登录token
                f"user_profile_{user_id}",  # 用户配置缓存
                f"user_theme_{user_id}",  # 用户主题缓存
                f"user_session_{user_id}",  # 用户会话缓存
                f"boss_login_status_{user_id}",  # Boss登录状态缓存
                f"user_preferences_{user_id}",  # 用户偏好设置缓存
            ]

            for cache_key in cache_keys_to_clear:
                try:
                    cache.delete(cache_key)
                except Exception as cache_error:
                    print(f"清除缓存失败 {cache_key}: {cache_error}")

        except Exception as e:
            print(f"API登出记录失败: {e}")

        # Django内置登出
        logout(request)

        return JsonResponse(
            {
                "success": True,
                "message": "登出成功，所有认证信息已清除",
                "clear_storage": True,  # 通知前端清除本地存储
                "redirect_url": "/",
            },
            content_type="application/json",
        )

    except Exception as e:
        return JsonResponse({"success": False, "message": f"登出失败: {str(e)}"}, status=500, content_type="application/json")


# 登出功能测试页面
@login_required
def test_logout_view(request):
    """登出功能测试页面"""
    return render(request, "test_logout.html")


# Session延长API
@csrf_exempt
@require_http_methods(["POST"])
def extend_session_api(request):
    """延长用户session过期时间API"""
    try:
        if request.user.is_authenticated and hasattr(request, "session"):
            # 延长session过期时间到30天
            request.session.set_expiry(60 * 60 * 24 * 30)  # 30天
            request.session.save()

            # 记录session延长活动
            try:
                x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
                if x_forwarded_for:
                    ip = x_forwarded_for.split(",")[0]
                else:
                    ip = request.META.get("REMOTE_ADDR")

                UserActivityLog.objects.create(
                    user=request.user,
                    activity_type="session_extend",
                    ip_address=ip,
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                    details={"new_expiry": "30天", "extend_method": "api"},
                )
            except Exception as e:
                print(f"记录session延长活动失败: {e}")

            return JsonResponse({"success": True, "message": "Session已延长至30天", "expires_in": 60 * 60 * 24 * 30})  # 过期时间（秒）
        else:
            return JsonResponse({"success": False, "message": "用户未登录或session不可用"}, status=401)

    except Exception as e:
        return JsonResponse({"success": False, "message": f"Session延长失败: {str(e)}"}, status=500)


# 获取session状态API
@csrf_exempt
@require_http_methods(["GET"])
def session_status_api(request):
    """获取用户session状态API"""
    try:
        if request.user.is_authenticated and hasattr(request, "session"):
            # 获取session过期时间
            expiry_age = request.session.get_expiry_age()
            expiry_date = request.session.get_expiry_date()

            return JsonResponse(
                {
                    "success": True,
                    "data": {
                        "user_id": request.user.id,
                        "username": request.user.username,
                        "is_authenticated": request.user.is_authenticated,
                        "session_key": request.session.session_key,
                        "expiry_age": expiry_age,  # 剩余秒数
                        "expiry_date": expiry_date.isoformat() if expiry_date else None,
                        "expires_in_days": expiry_age // (60 * 60 * 24) if expiry_age else 0,
                    },
                }
            )
        else:
            return JsonResponse({"success": False, "message": "用户未登录或session不可用"}, status=401)

    except Exception as e:
        return JsonResponse({"success": False, "message": f"获取session状态失败: {str(e)}"}, status=500)


# user_login_api 已删除，使用现代化弹窗登录


# user_register_api 已删除，使用现代化弹窗登录


# 用户资料API
@csrf_exempt
@require_http_methods(["GET", "POST"])
def user_profile_api(request):
    """用户资料API"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, "message": "用户未登录"}, status=401)
        
        if request.method == "GET":
            # 获取用户资料
            profile, created = Profile.objects.get_or_create(user=request.user)
            return JsonResponse({
                "success": True,
                "data": {
                    "id": request.user.id,
                    "username": request.user.username,
                    "email": request.user.email,
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                    "date_joined": request.user.date_joined.isoformat(),
                    "last_login": request.user.last_login.isoformat() if request.user.last_login else None,
                    "profile": {
                        "bio": profile.bio if hasattr(profile, 'bio') else '',
                        "avatar": profile.avatar.url if hasattr(profile, 'avatar') and profile.avatar else None
                    }
                }
            })
        
        elif request.method == "POST":
            # 更新用户资料
            data = json.loads(request.body)
            profile, created = Profile.objects.get_or_create(user=request.user)
            
            if 'first_name' in data:
                request.user.first_name = data['first_name']
            if 'last_name' in data:
                request.user.last_name = data['last_name']
            if 'email' in data:
                request.user.email = data['email']
            
            request.user.save()
            
            return JsonResponse({
                "success": True,
                "message": "资料更新成功",
                "data": {
                    "id": request.user.id,
                    "username": request.user.username,
                    "email": request.user.email,
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name
                }
            })
            
    except Exception as e:
        return JsonResponse({"success": False, "message": f"操作失败: {str(e)}"}, status=500)


# 欢迎窗口API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def welcome_modal_api(request):
    """欢迎窗口API - 标记欢迎窗口已显示"""
    try:
        from ..models import UserWelcomeModal
        
        # 标记欢迎窗口已显示
        UserWelcomeModal.mark_welcome_shown(request.user)
        
        # 清除session中的标记
        if 'show_welcome_modal' in request.session:
            del request.session['show_welcome_modal']
        
        return JsonResponse({
            "success": True,
            "message": "欢迎窗口已标记为已显示"
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"操作失败: {str(e)}"
        }, status=500)


# 用户名验证API
@csrf_exempt
@require_http_methods(["POST"])
def validate_username_api(request):
    """用户名验证API - 检查用户名是否可用"""
    # 检查速率限制
    is_allowed, remaining, reset_time = RateLimitService.check_rate_limit(
        request, 'validate_username', max_attempts=20, window_minutes=5
    )
    
    if not is_allowed:
        return JsonResponse({
            "success": False,
            "available": False,
            "message": f"验证请求过于频繁，请{5}分钟后再试"
        }, status=429)
    
    try:
        data = json.loads(request.body)
        username = data.get("username", "").strip()
        
        if not username:
            return JsonResponse({
                "success": False,
                "available": False,
                "message": "用户名不能为空"
            })
        
        # 基础格式验证
        if len(username) < 3:
            return JsonResponse({
                "success": False,
                "available": False,
                "message": "用户名至少需要3个字符"
            })
        
        if len(username) > 30:
            return JsonResponse({
                "success": False,
                "available": False,
                "message": "用户名不能超过30个字符"
            })
        
        # 检查用户名格式（只允许字母、数字、下划线）
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            return JsonResponse({
                "success": False,
                "available": False,
                "message": "用户名只能包含字母、数字和下划线"
            })
        
        # 检查敏感词
        sensitive_words = ["admin", "root", "system", "test", "user", "guest", "moderator", "support"]
        if username.lower() in sensitive_words:
            return JsonResponse({
                "success": False,
                "available": False,
                "message": "用户名包含敏感词，请选择其他用户名"
            })
        
        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "success": True,
                "available": False,
                "message": "用户名已存在，请选择其他用户名"
            })
        
        return JsonResponse({
            "success": True,
            "available": True,
            "message": "用户名可用"
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "available": False,
            "message": "请求数据格式错误"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "available": False,
            "message": f"验证失败: {str(e)}"
        }, status=500)


# 邮箱验证API
@csrf_exempt
@require_http_methods(["POST"])
def validate_email_api(request):
    """邮箱验证API - 检查邮箱是否可用"""
    # 检查速率限制
    is_allowed, remaining, reset_time = RateLimitService.check_rate_limit(
        request, 'validate_email', max_attempts=20, window_minutes=5
    )
    
    if not is_allowed:
        return JsonResponse({
            "success": False,
            "available": False,
            "message": f"验证请求过于频繁，请{5}分钟后再试"
        }, status=429)
    
    try:
        data = json.loads(request.body)
        email = data.get("email", "").strip()
        
        # 如果邮箱为空，认为是可用的（因为邮箱是可选的）
        if not email:
            return JsonResponse({
                "success": True,
                "available": True,
                "message": "邮箱为空（可选）"
            })
        
        # 检查邮箱格式
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            return JsonResponse({
                "success": False,
                "available": False,
                "message": "邮箱格式不正确"
            })
        
        # 检查邮箱域名黑名单
        domain = email.split("@")[1] if "@" in email else ""
        blacklisted_domains = getattr(settings, "BLACKLISTED_EMAIL_DOMAINS", [
            "10minutemail.com", "tempmail.org", "guerrillamail.com", "mailinator.com"
        ])
        if domain.lower() in blacklisted_domains:
            return JsonResponse({
                "success": False,
                "available": False,
                "message": "该邮箱域名不被允许"
            })
        
        # 检查邮箱是否已存在
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                "success": True,
                "available": False,
                "message": "该邮箱已被注册，请使用其他邮箱"
            })
        
        return JsonResponse({
            "success": True,
            "available": True,
            "message": "邮箱可用"
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "available": False,
            "message": "请求数据格式错误"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "available": False,
            "message": f"验证失败: {str(e)}"
        }, status=500)
