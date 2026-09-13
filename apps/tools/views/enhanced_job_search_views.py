"""
增强版AI找工作视图 - 融合get_jobs项目功能
支持多平台投递和完整的登录流程
"""
import json
import logging
import os
import time
import base64
import requests
import urllib.parse
import threading
from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.conf import settings
from apps.tools.services.enhanced_job_delivery_service import EnhancedJobDeliveryService, JobSearchConfig

logger = logging.getLogger(__name__)
BOSS_QR_SESSIONS = {}
_PLAYWRIGHT_QR_CONTEXTS = {}
_PLAYWRIGHT_QR_LOCK = threading.RLock()

def _boss_session_dir(user_id):
    """Return a private, durable directory for one BOSS account."""
    path = os.path.join(getattr(settings, 'MEDIA_ROOT', 'media'), 'boss_sessions', f'user_{user_id}')
    os.makedirs(path, mode=0o700, exist_ok=True)
    return path

def _persist_boss_session(user_id, session, qr_id):
    """Persist cookies/QR metadata so a worker restart does not mix accounts."""
    directory = _boss_session_dir(user_id)
    os.chmod(directory, 0o700)
    cookies = []
    for c in session.cookies:
        cookies.append({'name': c.name, 'value': c.value, 'domain': c.domain or '.zhipin.com', 'path': c.path or '/'})
    with open(os.path.join(directory, 'cookies.json'), 'w', encoding='utf-8') as fh:
        json.dump(cookies, fh, ensure_ascii=False)
    with open(os.path.join(directory, 'session.json'), 'w', encoding='utf-8') as fh:
        json.dump({'qr_id': qr_id, 'updated_at': time.time()}, fh)
    return directory

def _load_boss_session(user_id):
    """Load a user's QR session from shared media when requests hit another worker."""
    directory = _boss_session_dir(user_id)
    try:
        with open(os.path.join(directory, 'session.json'), encoding='utf-8') as fh:
            meta = json.load(fh)
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/152.0.0.0 Safari/537.36', 'Referer': 'https://www.zhipin.com/', 'Origin': 'https://www.zhipin.com', 'Accept': 'application/json, text/plain, */*', 'X-Requested-With': 'XMLHttpRequest'})
        with open(os.path.join(directory, 'cookies.json'), encoding='utf-8') as fh:
            for c in json.load(fh):
                session.cookies.set(c['name'], c['value'], domain=c.get('domain'), path=c.get('path', '/'))
        return {'session': session, 'qr_id': meta['qr_id'], 'user_id': user_id, 'created_at': meta.get('updated_at', time.time()), 'directory': directory, 'mode': meta.get('mode', 'requests'), 'state_file': meta.get('state_file')}
    except (FileNotFoundError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None

def _playwright_launch_options():
    return {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"]}


def _close_playwright_qr_context(user_id):
    """Release a live QR context only after success, expiry, or cancellation."""
    with _PLAYWRIGHT_QR_LOCK:
        live = _PLAYWRIGHT_QR_CONTEXTS.pop(user_id, None)
    if not live:
        return
    for obj in (live.get("context"), live.get("browser")):
        try: obj.close()
        except Exception: pass
    try: live.get("playwright").stop()
    except Exception: pass


def _playwright_qr_context(user_id):
    """Generate QR in a live browser context kept alive through mobile approval."""
    from playwright.sync_api import sync_playwright
    directory = _boss_session_dir(user_id)
    state_file = os.path.join(directory, "storage_state.json")
    login_url = "https://www.zhipin.com/web/user/?ka=header-login"
    with _PLAYWRIGHT_QR_LOCK:
        _close_playwright_qr_context(user_id)
        pw = sync_playwright().start()
        options = _playwright_launch_options()
        if os.path.exists("/usr/bin/chromium"):
            options["executable_path"] = "/usr/bin/chromium"
        browser = pw.chromium.launch(**options)
        context = browser.new_context(storage_state=state_file if os.path.exists(state_file) else None,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36", locale="zh-CN")
        page = context.new_page()
        page.goto(login_url, wait_until="domcontentloaded", timeout=30000)
        result = page.evaluate("""async () => {
          const r = await fetch('/wapi/zppassport/captcha/randkey', {credentials:'include'});
          const j = await r.json();
          const id = j?.zpData?.qrId || j?.data?.qrId || j?.qrId;
          if (!id) throw new Error('BOSS 未返回二维码标识');
          const q = await fetch('/wapi/zpweixin/qrcode/getqrcode?content=' + encodeURIComponent(id), {credentials:'include'});
          if (!q.ok) throw new Error('BOSS 二维码图片请求失败: ' + q.status);
          const b = await q.arrayBuffer(); let s = '';
          for (const x of new Uint8Array(b)) s += String.fromCharCode(x);
          return {qr_id:id, qr_code_url:'data:image/png;base64,' + btoa(s)};
        }""")
        context.storage_state(path=state_file)
        _PLAYWRIGHT_QR_CONTEXTS[user_id] = {"playwright": pw, "browser": browser, "context": context,
            "page": page, "qr_id": result["qr_id"], "created_at": time.time(), "state_file": state_file}
        with open(os.path.join(directory, "session.json"), "w", encoding="utf-8") as fh:
            json.dump({"qr_id": result["qr_id"], "mode": "playwright", "state_file": state_file,
                       "updated_at": time.time()}, fh)
    return {"qr_id": result["qr_id"], "qr_code_url": result["qr_code_url"], "user_id": user_id,
            "directory": directory, "state_file": state_file, "mode": "playwright", "created_at": time.time()}

def _playwright_qr_state(qr_session):
    """Poll scan and confirmation through the exact context that generated QR."""
    user_id = qr_session.get("user_id")
    with _PLAYWRIGHT_QR_LOCK:
        live = _PLAYWRIGHT_QR_CONTEXTS.get(user_id)
    if not live:
        return "error", {"message": "二维码浏览器会话已结束，请重新生成二维码"}
    api, qr_id = live["context"].request, live["qr_id"]
    def _get(path):
        try:
            response = api.get("https://www.zhipin.com" + path,
                headers={"Referer": "https://www.zhipin.com/web/user/?ka=header-login"}, timeout=8000)
            try: body = response.json()
            except Exception: body = {}
            return {"status": response.status, "json": body}
        except Exception as exc:
            logger.warning("BOSS QR poll request failed: %s", exc)
            return {"status": 0, "json": {}}
    try:
        scan = _get("/wapi/zppassport/qrcode/scan?uuid=" + urllib.parse.quote(qr_id))
        confirm = _get("/wapi/zppassport/qrcode/scanLogin?qrId=" + urllib.parse.quote(qr_id) + "&status=1")
        payload, cp = scan.get("json") or {}, confirm.get("json") or {}
        text = json.dumps({**payload, **cp}, ensure_ascii=False).lower()
        if any(x in text for x in ("expired", "expire", "timeout", "失效", "过期")):
            _close_playwright_qr_context(user_id); return "expired", cp or payload
        flag = payload.get("scaned", payload.get("scanned"))
        data = cp.get("zpData") or cp.get("data") or {}
        code = cp.get("code", cp.get("resCode"))
        confirmed = (isinstance(data, dict) and bool(data)) or any(x in text for x in ("login success", "登录成功", "confirmed"))
        if confirmed and code in (None, 0, "0", True):
            live["context"].storage_state(path=live["state_file"])
            _close_playwright_qr_context(user_id); return "confirmed", cp or payload
        if flag in (True, 1, "1", "true", "True"):
            return "scanned", payload
        return "waiting_scan", payload
    except Exception as exc:
        logger.exception("BOSS live QR state check failed: %s", exc)
        return "error", {"message": str(exc)}

def _boss_payload(response):
    """Decode BOSS's JSON envelope without treating HTTP 200 as success."""
    try:
        payload = response.json()
    except (ValueError, requests.exceptions.JSONDecodeError):
        return {}, 'error'
    # The QR endpoints do not consistently use the normal zpData envelope.
    # In particular /qrcode/scan returns {"scaned": true} at the top level.
    if payload.get('scaned') in (True, 1, '1', 'true', 'True') or payload.get('scanned') in (True, 1, '1', 'true', 'True'):
        return payload, 'scanned'
    if str(payload.get('msg', '')).lower() in ('timeout', 'expired', 'invalid'):
        return payload, 'expired'
    data = payload.get('zpData') or payload.get('data') or {}
    code = payload.get('code', payload.get('resCode', payload.get('statusCode')))
    # BOSS uses code=0 for a valid response; some deployments omit code.
    valid = code in (None, 0, '0', True)
    raw = data.get('status', data.get('scanStatus', data.get('qrStatus', payload.get('status')))) if isinstance(data, dict) else payload.get('status')
    text = str(raw).lower() if raw is not None else ''
    if any(x in text for x in ('expire', 'invalid', 'timeout')) or raw in (3, '3', -1, '-1'):
        state = 'expired'
    elif any(x in text for x in ('confirm', 'login', 'success')) or raw in (2, '2'):
        state = 'confirmed'
    elif any(x in text for x in ('scan', 'read')) or raw in (1, '1'):
        state = 'scanned'
    elif valid and response.status_code == 200:
        state = 'waiting_scan'
    else:
        state = 'error'
    return payload, state

def _boss_qr_state(qr_session):
    """Poll both endpoints; scanLogin is authoritative after app approval."""
    if qr_session.get('mode') == 'playwright':
        return _playwright_qr_state(qr_session)
    session, qr_id = qr_session['session'], qr_session['qr_id']
    scan = session.get(f"https://www.zhipin.com/wapi/zppassport/qrcode/scan?uuid={qr_id}", timeout=10)
    scan_payload, state = _boss_payload(scan)
    # Some BOSS deployments leave /scan at status=0 after the mobile app
    # approves. Always call scanLogin so the approval is not missed.
    confirm = session.get(f"https://www.zhipin.com/wapi/zppassport/qrcode/scanLogin?qrId={qr_id}&status=1", timeout=10)
    confirm_payload, confirm_state = _boss_payload(confirm)
    confirm_data = confirm_payload.get('zpData') or confirm_payload.get('data') or {}
    logger.info("BOSS QR poll user=%s scan=%s confirm=%s", qr_session.get('user_id'), state, confirm_state)
    if state == 'expired' or confirm_state == 'expired':
        return 'expired', confirm_payload or scan_payload
    # A bare HTTP 200 is only a waiting response. Successful scanLogin has a
    # populated data envelope and must be persisted for this user.
    # Open-source implementations treat a 200 scanLogin response as the
    # approval edge, even when BOSS returns an empty zpData object.  The
    # endpoint is a stateful session call; the session cookies are the
    # authoritative result.
    if (state in ('scanned', 'confirmed') and confirm.status_code == 200
            and confirm_payload.get('code') in (0, '0', None)):
        _persist_boss_session(qr_session.get('user_id'), session, qr_id)
        return 'confirmed', confirm_payload
    if state in ('scanned', 'confirmed'):
        return 'scanned', scan_payload
    return state, scan_payload


@login_required
def enhanced_job_search_launcher(request):
    """增强版AI一键投递启动器页面"""
    return render(request, "tools/enhanced_job_search_launcher.html")


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def start_enhanced_job_search_api(request):
    """启动增强版AI一键投递API"""
    try:
        # 暂时移除认证检查，让检测逻辑能够执行
        # if not request.user.is_authenticated:
        #     logger.warning(f"未认证用户尝试访问投递API: {request.META.get('REMOTE_ADDR')}")
        #     return JsonResponse({"success": False, "error": "请先登录"})
        
        logger.info(f"用户 {request.user.username} 启动增强版投递任务")
        
        data = json.loads(request.body)
        
        # 获取平台列表
        platforms = data.get('platforms', ['boss'])
        if not isinstance(platforms, list):
            platforms = [data.get('platform', 'boss')]
        
        # 创建搜索配置
        service = EnhancedJobDeliveryService()
        config = service.create_search_config(data)
        
        # 验证配置
        if not config.keywords:
            return JsonResponse({"success": False, "error": "请填写搜索关键词"})
        
        if not config.cities:
            return JsonResponse({"success": False, "error": "请选择工作城市"})
        
        # 启动投递任务
        result = service.start_multi_platform_delivery(platforms, config, request.user)
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"})
    except Exception as e:
        logger.error(f"启动增强版投递失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"启动失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_enhanced_job_search_status_api(request):
    """获取增强版投递状态API"""
    try:
        service = EnhancedJobDeliveryService()
        status = service.get_delivery_status(request.user)
        return JsonResponse(status)
    except Exception as e:
        logger.error(f"获取增强版投递状态失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"获取状态失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def stop_enhanced_job_search_api(request):
    """停止增强版投递API"""
    try:
        service = EnhancedJobDeliveryService()
        result = service.stop_delivery(request.user)
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"停止增强版投递失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"停止失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_platform_info_api(request):
    """获取平台信息API"""
    try:
        service = EnhancedJobDeliveryService()
        result = service.get_platform_info()
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"获取平台信息失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"获取平台信息失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def boss_login_with_token_api(request):
    """使用Token登录BOSS直聘API"""
    try:
        data = json.loads(request.body)
        token = data.get('token', '').strip()
        
        if not token:
            return JsonResponse({"success": False, "error": "Token不能为空"})
        
        # 保存token到文件
        token_file = os.path.join(settings.BASE_DIR, 'get_jobs_integration', f'boss_token_{request.user.id}.json')
        os.makedirs(os.path.dirname(token_file), exist_ok=True)
        
        token_data = {
            'token': token,
            'login_time': time.time(),
            'user_id': request.user.id,
            'login_method': 'token'
        }
        
        with open(token_file, 'w', encoding='utf-8') as f:
            json.dump(token_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"用户 {request.user.username} 使用Token登录成功")
        
        return JsonResponse({
            "success": True,
            "message": "Token登录成功",
            "token": token[:20] + "..."  # 只返回部分token用于显示
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的请求数据"})
    except Exception as e:
        logger.error(f"Token登录失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"Token登录失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def check_boss_login_status_api(request):
    """检查BOSS直聘登录状态API"""
    try:
        qr_session = BOSS_QR_SESSIONS.get(request.user.id) or _load_boss_session(request.user.id)
        if qr_session:
            try:
                state, _ = _boss_qr_state(qr_session)
                if state == 'confirmed':
                    return JsonResponse({'success': True, 'is_logged_in': True, 'qr_status': state, 'message': 'BOSS 扫码登录成功'})
                if state == 'expired':
                    return JsonResponse({'success': True, 'is_logged_in': False, 'qr_status': state, 'message': '二维码已过期，请重新获取'})
                if state == 'error':
                    return JsonResponse({'success': False, 'is_logged_in': False, 'qr_status': state,
                                         'message': '二维码会话已断开，请重新生成二维码'})
                return JsonResponse({'success': True, 'is_logged_in': False, 'qr_status': state,
                                     'message': '已扫码，请在 BOSS App 内确认登录' if state == 'scanned' else '等待扫码'})
            except Exception as qr_error:
                logger.debug(f'扫码状态轮询失败: {qr_error}')
        from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
        
        playwright_service = BossZhipinPlaywrightService(headless=True)
        result = playwright_service.check_login_status(request.user.id)
        
        return JsonResponse({
            "success": result.get('success', False),
            "is_logged_in": result.get('is_logged_in', False),
            "message": result.get('message', '检查登录状态'),
            "token_info": result.get('token_info', {}),
            "current_url": result.get('current_url', ''),
            "user_info": result.get('user_info', {})
        })
        
    except Exception as e:
        logger.error(f"检查BOSS直聘登录状态失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"检查状态失败: {str(e)}"})

@login_required
def boss_login_events_api(request):
    """实时推送当前用户 BOSS 扫码登录状态。"""
    def events():
        # Gunicorn's sync worker must not be held by a long lived stream;
        # the browser's status poll provides the durable real-time loop.
        for _ in range(1):
            session = BOSS_QR_SESSIONS.get(request.user.id) or _load_boss_session(request.user.id)
            if session:
                BOSS_QR_SESSIONS[request.user.id] = session
            state = 'waiting_scan'
            if session:
                try:
                    state, _ = _boss_qr_state(session)
                except Exception:
                    pass
            yield f"data: {json.dumps({'status': 'logged_in' if state == 'confirmed' else state}, ensure_ascii=False)}\n\n"
            if state in ('confirmed', 'expired'):
                break
    return StreamingHttpResponse(events(), content_type='text/event-stream')


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def start_boss_qr_login_api(request):
    """启动BOSS直聘二维码登录API"""
    try:
        login_url = 'https://www.zhipin.com/web/user/?ka=header-login'
        try:
            qr = _playwright_qr_context(request.user.id)
        except Exception as qr_error:
            logger.exception('Playwright BOSS QR flow failed')
            return JsonResponse({'success': False, 'error': f'无法生成二维码：{qr_error}'}, status=502)
        BOSS_QR_SESSIONS[request.user.id] = qr
        return JsonResponse({'success': True, 'message': '二维码登录已启动', 'login_url': login_url,
                             'qr_code_url': qr['qr_code_url']})
        
    except Exception as e:
        logger.error(f"启动BOSS直聘二维码登录失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"启动二维码登录失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def start_boss_phone_login_api(request):
    """启动BOSS直聘手机号登录API"""
    try:
        data = json.loads(request.body)
        phone = data.get('phone', '').strip()
        
        if not phone:
            return JsonResponse({"success": False, "error": "请填写手机号"})
        
        if len(phone) != 11 or not phone.isdigit():
            return JsonResponse({"success": False, "error": "请输入正确的手机号"})
        
        # 这里可以集成真实的手机号登录逻辑
        # 暂时返回成功，实际需要调用BOSS直聘的短信验证码接口
        
        return JsonResponse({
            "success": True,
            "message": "验证码已发送，请查收短信",
            "phone": phone[:3] + "****" + phone[7:]  # 隐藏手机号
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的请求数据"})
    except Exception as e:
        logger.error(f"启动BOSS直聘手机号登录失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"启动手机号登录失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def verify_boss_phone_code_api(request):
    """验证BOSS直聘手机验证码API"""
    try:
        data = json.loads(request.body)
        phone = data.get('phone', '').strip()
        code = data.get('code', '').strip()
        
        if not phone or not code:
            return JsonResponse({"success": False, "error": "请填写手机号和验证码"})
        
        if len(code) != 6 or not code.isdigit():
            return JsonResponse({"success": False, "error": "请输入6位验证码"})
        
        # 这里可以集成真实的验证码验证逻辑
        # 暂时模拟验证成功
        
        # 保存登录状态
        login_file = os.path.join(settings.BASE_DIR, 'get_jobs_integration', f'boss_login_{request.user.id}.json')
        os.makedirs(os.path.dirname(login_file), exist_ok=True)
        
        login_data = {
            'phone': phone,
            'login_time': time.time(),
            'user_id': request.user.id,
            'login_method': 'phone'
        }
        
        with open(login_file, 'w', encoding='utf-8') as f:
            json.dump(login_data, f, ensure_ascii=False, indent=2)
        
        return JsonResponse({
            "success": True,
            "message": "手机号登录成功",
            "phone": phone[:3] + "****" + phone[7:]
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的请求数据"})
    except Exception as e:
        logger.error(f"验证BOSS直聘手机验证码失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"验证验证码失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_boss_iframe_login_url_api(request):
    """获取BOSS直聘iframe登录URL API"""
    try:
        from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
        
        playwright_service = BossZhipinPlaywrightService(headless=True)
        result = playwright_service.get_login_page_url(request.user.id)
        
        if result.get('success'):
            return JsonResponse({
                "success": True,
                "message": "获取登录页面URL成功",
                "login_url": result.get('login_url'),
                "iframe_url": result.get('login_url')
            })
        else:
            return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"获取BOSS直聘iframe登录URL失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"获取登录URL失败: {str(e)}"})
