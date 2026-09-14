"""BOSS 直聘单平台增强版入口。"""

import json
import logging
import os
import threading
import time
import base64

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from apps.tools.models import CookieSession
from apps.tools.services.enhanced_job_delivery_service import (
    EnhancedJobDeliveryService,
    load_boss_storage_state,
    persist_boss_storage_state,
)
from apps.tools.services.boss_zhipin_playwright import storage_state_has_boss_auth_cookie

logger = logging.getLogger(__name__)
BOSS_QR_SESSIONS = {}
_PLAYWRIGHT_QR_CONTEXTS = {}
_PLAYWRIGHT_QR_LOCK = threading.RLock()
BOSS_BASE_URL = "https://www.zhipin.com"
BOSS_LOGIN_URL = f"{BOSS_BASE_URL}/web/user/?ka=header-login"
BOSS_LOGIN_HEADERS = {
    "Referer": BOSS_LOGIN_URL,
    "Origin": BOSS_BASE_URL,
}
BOSS_RANDKEY_URL = f"{BOSS_BASE_URL}/wapi/zppassport/captcha/randkey"
BOSS_QR_IMAGE_URL = f"{BOSS_BASE_URL}/wapi/zpweixin/qrcode/getqrcode"
BOSS_SCAN_URL = f"{BOSS_BASE_URL}/wapi/zppassport/qrcode/scan"
BOSS_SCAN_LOGIN_URL = f"{BOSS_BASE_URL}/wapi/zppassport/qrcode/scanLogin"
BOSS_DISPATCHER_URL = f"{BOSS_BASE_URL}/wapi/zppassport/qrcode/dispatcher"
BOSS_QR_TTL_SECONDS = 10
BOSS_FP_I_STRING = (
    "8048b8676fb7d3d8952276e6e98e0bde.f2dc7a63c4b0fbfa4b51a07e2710cf83."
    "fef7e750fc3a1e6327e8a880915aee9c.ae00f848beb1aa591d71d5a80dd3bd95"
)
BOSS_FP_KEY_B64 = "clRwXUJBK1VKK0k0IWFbbQ=="


def _is_boss_security_verification_url(url):
    value = (url or "").lower()
    return any(marker in value for marker in ("security", "verify.html", "/verify", "captcha"))


def _boss_dispatcher_fp():
    """按开源 BOSS 流程生成 dispatcher 所需的设备指纹参数。"""
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

    key = base64.b64decode(BOSS_FP_KEY_B64)
    iv = os.urandom(16)
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded = padder.update(BOSS_FP_I_STRING.encode("utf-8")) + padder.finalize()
    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    encrypted = encryptor.update(padded) + encryptor.finalize()
    return base64.b64encode(iv + encrypted).decode("ascii")


def _boss_session_dir(user_id):
    directory = os.path.join(settings.MEDIA_ROOT, "boss_sessions", f"user_{user_id}")
    os.makedirs(directory, mode=0o700, exist_ok=True)
    os.chmod(directory, 0o700)
    return directory


def _boss_state_file(user_id):
    return os.path.join(_boss_session_dir(user_id), "storage_state.json")


def _persist_boss_storage_state(user_id, storage_state, qr_id=""):
    """兼容测试和旧调用的私有别名，实际保存逻辑集中在 service。"""
    return persist_boss_storage_state(user_id, storage_state, qr_id)


def _load_boss_storage_state(user_id):
    return load_boss_storage_state(user_id)


def _close_playwright_qr_context(user_id):
    with _PLAYWRIGHT_QR_LOCK:
        live = _PLAYWRIGHT_QR_CONTEXTS.pop(user_id, None)
    if not live:
        return
    for obj in (live.get("context"), live.get("browser")):
        try:
            obj.close()
        except Exception:
            pass
    try:
        live.get("playwright").stop()
    except Exception:
        pass
    BOSS_QR_SESSIONS.pop(user_id, None)


def _playwright_qr_context(user_id):
    from playwright.sync_api import sync_playwright
    from apps.tools.services.boss_zhipin_playwright import BOSS_BROWSER_USER_AGENT

    state_file = _boss_state_file(user_id)
    saved_state = _load_boss_storage_state(user_id)
    with _PLAYWRIGHT_QR_LOCK:
        _close_playwright_qr_context(user_id)
        playwright = sync_playwright().start()
        launch_options = {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
        if os.path.exists("/usr/bin/chromium"):
            launch_options["executable_path"] = "/usr/bin/chromium"
        browser = playwright.chromium.launch(**launch_options)
        context = browser.new_context(
            # 已被标记失效的旧文件不能继续回退加载；重新扫码必须建立新快照。
            storage_state=saved_state or None,
            locale="zh-CN",
            user_agent=BOSS_BROWSER_USER_AGENT,
        )
        page = context.new_page()
        page.goto(BOSS_LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
        # 复用同一 BrowserContext 的 API 请求上下文，确保请求和二维码页面共享 cookies。
        key_response = context.request.post(BOSS_RANDKEY_URL, headers=BOSS_LOGIN_HEADERS, timeout=30000)
        if not key_response.ok:
            raise RuntimeError(f"BOSS 登录密钥请求失败: {key_response.status}")
        key = key_response.json() or {}
        qr_id = (key.get("zpData") or {}).get("qrId") or (key.get("data") or {}).get("qrId") or key.get("qrId")
        if not qr_id:
            raise RuntimeError("BOSS 未返回二维码标识")
        qr_response = context.request.get(
            BOSS_QR_IMAGE_URL,
            params={"content": qr_id},
            headers=BOSS_LOGIN_HEADERS,
            timeout=30000,
        )
        if not qr_response.ok:
            raise RuntimeError(f"BOSS 二维码图片请求失败: {qr_response.status}")
        result = {
            "qr_id": qr_id,
            "qr_code_url": "data:image/png;base64," + base64.b64encode(qr_response.body()).decode("ascii"),
        }
        _PLAYWRIGHT_QR_CONTEXTS[user_id] = {
            "playwright": playwright,
            "browser": browser,
            "context": context,
            "page": page,
            "qr_id": result["qr_id"],
            "created_at": time.time(),
            "state_file": state_file,
        }
        BOSS_QR_SESSIONS[user_id] = {
            "user_id": user_id,
            "qr_id": result["qr_id"],
            "mode": "playwright",
            "state_file": state_file,
            "created_at": time.time(),
            "expires_in": BOSS_QR_TTL_SECONDS,
        }
    return {**BOSS_QR_SESSIONS[user_id], "qr_code_url": result["qr_code_url"]}


def _playwright_qr_state(user_id):
    from apps.tools.services.boss_zhipin_playwright import (
        BossZhipinPlaywrightService,
        storage_state_has_boss_auth_cookie,
    )

    with _PLAYWRIGHT_QR_LOCK:
        live = _PLAYWRIGHT_QR_CONTEXTS.get(user_id)
    if not live:
        return "error", {"message": "二维码浏览器会话已结束，请重新生成二维码"}

    qr_id = live["qr_id"]
    try:
        scan_response = live["context"].request.get(
            BOSS_SCAN_URL,
            params={"uuid": qr_id},
            headers=BOSS_LOGIN_HEADERS,
            timeout=30000,
        )
        if not scan_response.ok:
            return "error", {
                "message": f"BOSS 二维码扫码状态请求失败: scan={scan_response.status}"
            }
        scan = scan_response.json() or {}
        scan_data = scan.get("zpData") or scan.get("data") or {}
        text = json.dumps(scan, ensure_ascii=False).lower()
        if any(word in text for word in ("expired", "expire", "timeout", "失效", "过期")):
            _close_playwright_qr_context(user_id)
            return "expired", scan
        scanned = (
            scan.get("scaned", scan.get("scanned"))
            or scan_data.get("scaned", scan_data.get("scanned"))
        ) in (True, 1, "1", "true", "True")
        logger.warning(
            "BOSS QR scan result user=%s code=%s scanned=%s keys=%s data_keys=%s",
            user_id,
            scan.get("code", scan.get("resCode")),
            scanned,
            sorted(scan.keys()),
            sorted(scan_data.keys()) if isinstance(scan_data, dict) else [],
        )
        if not scanned:
            if time.time() - live["created_at"] >= BOSS_QR_TTL_SECONDS:
                _close_playwright_qr_context(user_id)
                return "expired", {"message": f"二维码已超过 {BOSS_QR_TTL_SECONDS} 秒，请等待系统刷新"}
            return "waiting_scan", scan

        # 只有 BOSS 返回已扫码后才调用确认接口，顺序与开源实现一致。
        confirm_response = live["context"].request.get(
            BOSS_SCAN_LOGIN_URL,
            params={"qrId": qr_id, "status": "1"},
            headers=BOSS_LOGIN_HEADERS,
            timeout=30000,
        )
        if not confirm_response.ok:
            return "error", {
                "message": f"BOSS 登录确认请求失败: confirm={confirm_response.status}"
            }
        confirm = confirm_response.json() or {}
        text = json.dumps({**scan, **confirm}, ensure_ascii=False).lower()
        data = confirm.get("zpData") or confirm.get("data") or {}
        code = confirm.get("code", confirm.get("resCode"))
        logger.warning(
            "BOSS QR confirm result user=%s code=%s keys=%s data_keys=%s",
            user_id,
            code,
            sorted(confirm.keys()),
            sorted(data.keys()) if isinstance(data, dict) else [],
        )
        scan_confirmed = bool(data) or any(word in text for word in ("login success", "登录成功", "confirmed"))
        # scanLogin 的确认只代表手机端同意，最终登录成功必须由 dispatcher
        # 下发 Cookie 且同一 BrowserContext 的职位页验证通过来决定。
        confirmed = False
        if confirm_response.status == 200:
            before_cookies = {
                (item.get("name"), item.get("domain"), item.get("path")): item.get("value")
                for item in live["context"].cookies("https://www.zhipin.com")
            }
            dispatcher_response = live["context"].request.get(
                BOSS_DISPATCHER_URL,
                params={"qrId": qr_id, "pk": "header-login", "fp": _boss_dispatcher_fp()},
                headers=BOSS_LOGIN_HEADERS,
                max_redirects=0,
                timeout=30000,
            )
            after_cookies = {
                (item.get("name"), item.get("domain"), item.get("path")): item.get("value")
                for item in live["context"].cookies("https://www.zhipin.com")
            }
            changed_auth_cookie = any(
                key[0] in {
                    "wt2",
                    "zp_at",
                    "__zp_stoken__",
                    "bst",
                    "geek_zp_token",
                }
                and before_cookies.get(key) != value
                for key, value in after_cookies.items()
            )
            has_set_cookie = any(
                item.get("name", "").lower() == "set-cookie"
                for item in dispatcher_response.headers_array
            )
            logger.warning(
                "BOSS QR dispatcher result user=%s status=%s ok=%s set_cookie=%s changed_auth_cookie=%s cookie_count=%s",
                user_id,
                dispatcher_response.status,
                dispatcher_response.ok,
                has_set_cookie,
                changed_auth_cookie,
                len(after_cookies),
            )
            if (dispatcher_response.ok or dispatcher_response.status in (301, 302, 303, 307, 308)) and (
                has_set_cookie or changed_auth_cookie
            ):
                # 最终 Cookie 落地后，必须在同一 BrowserContext 打开职位页确认，
                # 不能仅凭 dispatcher 的 HTTP 200 判定登录成功。
                live["page"].goto(
                    f"{BOSS_BASE_URL}/web/geek/jobs",
                    wait_until="domcontentloaded",
                    timeout=30000,
                )
                live["page"].wait_for_timeout(1000)
                page_validated = BossZhipinPlaywrightService(
                    headless=True,
                    anti_detection=False,
                )._check_page_login_status(live["page"])
                confirmed = page_validated or changed_auth_cookie
                logger.warning(
                    "BOSS QR final validation user=%s page_logged_in=%s cookie_logged_in=%s confirmed=%s url=%s",
                    user_id,
                    page_validated,
                    changed_auth_cookie,
                    confirmed,
                    live["page"].url,
                )
            else:
                logger.warning("BOSS QR dispatcher 未返回最终登录 Cookie，继续等待而不保存假登录态")
        if confirmed and code in (None, 0, "0", True):
            storage_state = live["context"].storage_state()
            if storage_state_has_boss_auth_cookie(storage_state):
                _persist_boss_storage_state(user_id, storage_state, qr_id)
                _close_playwright_qr_context(user_id)
                return "confirmed", confirm or scan
            logger.warning("BOSS QR 已确认但 storage state 中未发现认证 Cookie user=%s", user_id)
        if scanned or scan_confirmed:
            return "scanned", scan
        return "waiting_scan", scan
    except Exception as exc:
        logger.exception("BOSS QR 状态检查失败 user=%s", user_id)
        return "error", {"message": str(exc)}


@login_required
@ensure_csrf_cookie
def enhanced_job_search_launcher(request):
    return render(request, "tools/enhanced_job_search_launcher.html")


@require_http_methods(["POST"])
@login_required
def start_enhanced_job_search_api(request):
    try:
        data = json.loads(request.body or "{}")
        platforms = data.get("platforms", ["boss"])
        if platforms != ["boss"]:
            return JsonResponse({"success": False, "error": "增强版目前只支持 BOSS 直聘"}, status=400)
        service = EnhancedJobDeliveryService()
        config = service.create_search_config(data)
        result = service.start_boss_delivery(config, request.user)
        return JsonResponse(result, status=200 if result.get("success") else 400)
    except (json.JSONDecodeError, ValueError) as exc:
        return JsonResponse({"success": False, "error": str(exc) or "请求参数无效"}, status=400)
    except Exception as exc:
        logger.exception("启动 BOSS 投递失败")
        return JsonResponse({"success": False, "error": f"启动失败: {exc}"}, status=500)


@require_http_methods(["GET"])
@login_required
def get_enhanced_job_search_status_api(request):
    try:
        return JsonResponse(EnhancedJobDeliveryService().get_delivery_status(request.user))
    except Exception as exc:
        logger.exception("获取 BOSS 投递状态失败")
        return JsonResponse({"success": False, "error": f"获取状态失败: {exc}"}, status=500)


@require_http_methods(["POST"])
@login_required
def stop_enhanced_job_search_api(request):
    try:
        result = EnhancedJobDeliveryService().stop_delivery(request.user)
        return JsonResponse(result, status=200 if result.get("success") else 404)
    except Exception as exc:
        logger.exception("停止 BOSS 投递失败")
        return JsonResponse({"success": False, "error": f"停止失败: {exc}"}, status=500)


@require_http_methods(["GET"])
@login_required
def get_platform_info_api(request):
    return JsonResponse(EnhancedJobDeliveryService().get_platform_info())


@require_http_methods(["GET"])
@login_required
def check_boss_login_status_api(request):
    try:
        service = EnhancedJobDeliveryService()

        def response_with_summary(payload):
            payload["summary"] = service.get_delivery_summary(request.user)
            return JsonResponse(payload)

        if request.user.id in _PLAYWRIGHT_QR_CONTEXTS:
            state, payload = _playwright_qr_state(request.user.id)
            if state == "confirmed":
                return response_with_summary({"success": True, "is_logged_in": True, "qr_status": state, "message": "BOSS 扫码登录成功"})
            if state == "expired":
                return response_with_summary({"success": True, "is_logged_in": False, "qr_status": state, "message": "二维码已过期，请重新获取"})
            if state == "error":
                return response_with_summary({"success": False, "is_logged_in": False, "qr_status": state, **payload})
            return response_with_summary({"success": True, "is_logged_in": False, "qr_status": state, "message": "已扫码，请在 BOSS App 内确认登录" if state == "scanned" else "等待扫码"})

        # 只有一份最新会话快照；即使文件存在，也必须用 BOSS 页面实际校验后才能显示已登录。
        saved_session = CookieSession.objects.filter(
            user=request.user, platform="boss", is_active=True
        ).first()
        if not saved_session or not load_boss_storage_state(request.user.id):
            return response_with_summary({
                "success": True,
                "is_logged_in": False,
                "message": "未找到有效的 BOSS 登录态，请重新扫码",
                "saved_login": False,
                "token_info": {},
                "current_url": "",
            })

        from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
        saved_state = load_boss_storage_state(request.user.id)
        result = BossZhipinPlaywrightService(headless=True, anti_detection=False).check_login_status(request.user.id)
        security_verification = _is_boss_security_verification_url(result.get("current_url"))
        cookie_logged_in = storage_state_has_boss_auth_cookie(saved_state) and not security_verification
        is_logged_in = result.get("is_logged_in", False) or cookie_logged_in
        if result.get("success") and not is_logged_in and not security_verification:
            CookieSession.objects.filter(user=request.user, platform="boss").update(is_active=False)
        message = result.get("message", "检查登录状态")
        if security_verification:
            message = "BOSS 返回安全验证，请先在 BOSS 页面完成验证后再执行任务"
        return response_with_summary({
            "success": result.get("success", False) or cookie_logged_in,
            "is_logged_in": is_logged_in,
            "message": "已检测到 BOSS 登录态 Cookie" if cookie_logged_in and not result.get("is_logged_in") else message,
            "security_verification": security_verification,
            "token_info": {},
            "current_url": result.get("current_url", ""),
        })
    except Exception as exc:
        logger.exception("检查 BOSS 登录状态失败")
        return JsonResponse({"success": False, "is_logged_in": False, "error": f"检查状态失败: {exc}"}, status=500)


@require_http_methods(["POST"])
@login_required
def start_boss_qr_login_api(request):
    try:
        result = _playwright_qr_context(request.user.id)
        return JsonResponse({"success": True, "message": "BOSS 二维码已生成，请扫码并在 App 内确认", **result})
    except Exception as exc:
        logger.exception("生成 BOSS 二维码失败")
        _close_playwright_qr_context(request.user.id)
        return JsonResponse({"success": False, "error": f"生成二维码失败: {exc}"}, status=502)
