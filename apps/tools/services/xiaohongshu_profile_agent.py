"""Read-only adapter for the separately hosted xiaohongshu-mcp service."""

from __future__ import annotations

import os
import re
import hashlib
import secrets
import tempfile
import time
from urllib.parse import parse_qs, quote, urlparse

if os.name == "nt":
    import msvcrt
else:
    import fcntl

import requests
from django.core.cache import cache
from django.utils import timezone


class XhsInputError(ValueError):
    pass


class XhsServiceError(RuntimeError):
    pass


_PROFILE_PATH = re.compile(r"^/user/profile/([A-Za-z0-9]+)/*$")
_HOSTS = {"xiaohongshu.com", "www.xiaohongshu.com", "m.xiaohongshu.com"}


def _lock_file(fd: int) -> None:
    if os.name == "nt":
        if os.fstat(fd).st_size == 0:
            os.write(fd, b"0")
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        os.lseek(fd, 1, os.SEEK_SET)
    else:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)


def _unlock_file(fd: int) -> None:
    if os.name == "nt":
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
    else:
        fcntl.flock(fd, fcntl.LOCK_UN)


def parse_profile_link(value: str) -> tuple[str, str]:
    """Extract upstream-required user ID and xsec_token without fetching a URL."""
    value = (value or "").strip()
    if not value or len(value) > 2048:
        raise XhsInputError("请粘贴完整的小红书用户主页链接")
    parsed = urlparse(value)
    if parsed.hostname == "xhslink.cn" and parsed.path.startswith("/o/"):
        try:
            resolved = requests.get(value, allow_redirects=True, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
            value = resolved.url
            parsed = urlparse(value)
            redirect_path = parse_qs(parsed.query).get("redirectPath", [""])[0]
            if redirect_path:
                value = redirect_path
                parsed = urlparse(value)
        except requests.RequestException as exc:
            raise XhsInputError("小红书短链接暂时无法解析，请粘贴完整主页链接") from exc
    if parsed.scheme not in {"http", "https"} or parsed.hostname not in _HOSTS:
        raise XhsInputError("请输入 xiaohongshu.com 的用户主页链接")
    match = _PROFILE_PATH.fullmatch(parsed.path)
    if not match:
        raise XhsInputError("链接不是小红书用户主页；请从用户主页复制链接")
    token = parse_qs(parsed.query).get("xsec_token", [""])[0]
    if not token or len(token) > 1024:
        raise XhsInputError("链接缺少 xsec_token；请从小红书搜索结果打开主页后复制完整地址")
    return match.group(1), token


def _data(response: dict) -> dict:
    data = response.get("data", {})
    # MCP releases have returned one or two envelope layers over time.
    while isinstance(data, dict) and "data" in data and isinstance(data["data"], dict):
        data = data["data"]
    return data if isinstance(data, dict) else {}


def _note_id_and_token(feed: dict, card: dict) -> tuple[str, str]:
    """Accept the several note shapes returned by different XHS page builds."""
    note_id = (
        feed.get("id") or feed.get("noteId") or feed.get("note_id") or
        card.get("id") or card.get("noteId") or card.get("note_id") or ""
    )
    token = feed.get("xsecToken") or feed.get("xsec_token") or card.get("xsecToken") or ""
    for value in (feed.get("url"), feed.get("link"), card.get("url"), card.get("link")):
        if not isinstance(value, str):
            continue
        match = re.search(r"/explore/([A-Za-z0-9]+)", value)
        if match and not note_id:
            note_id = match.group(1)
        if "xsec_token=" in value and not token:
            token = parse_qs(urlparse(value).query).get("xsec_token", [""])[0]
    # Newer MCP builds sometimes wrap the note card several levels deep.
    if not note_id:
        def walk(value: object) -> str:
            if isinstance(value, dict):
                for key in ("noteId", "note_id", "feedId", "feed_id"):
                    candidate = value.get(key)
                    if isinstance(candidate, str) and re.fullmatch(r"[A-Za-z0-9]{16,64}", candidate):
                        return candidate
                for child in value.values():
                    found = walk(child)
                    if found:
                        return found
            elif isinstance(value, list):
                for child in value:
                    found = walk(child)
                    if found:
                        return found
            return ""
        note_id = walk(feed)
    return str(note_id), str(token)


def _cover_url(feed: dict, card: dict) -> str:
    candidates = []
    for obj in (card.get("cover"), feed.get("cover"), card.get("image"), feed.get("image")):
        if isinstance(obj, dict):
            candidates.extend(obj.get(key, "") for key in ("urlDefault", "url_default", "urlPre", "url_pre", "url", "src"))
        elif isinstance(obj, str):
            candidates.append(obj)
    for key in ("imageList", "image_list", "images"):
        values = card.get(key) or feed.get(key) or []
        if isinstance(values, list):
            for obj in values:
                if isinstance(obj, dict):
                    candidates.extend(obj.get(k, "") for k in ("urlDefault", "url_default", "urlPre", "url_pre", "url", "src"))
                elif isinstance(obj, str):
                    candidates.append(obj)
    return next((value for value in candidates if isinstance(value, str) and value.startswith(("http://", "https://"))), "")


def _call_mcp(method: str, path: str, *, payload: dict | None = None, timeout: int = 30) -> dict:
    base = os.environ.get("XHS_MCP_BASE_URL", "http://127.0.0.1:18060").rstrip("/")
    token = os.environ.get("XHS_MCP_TOKEN", "")
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    lock_key = "xhs-agent:mcp-operation"
    lock_value = secrets.token_hex(12)
    if not cache.add(lock_key, lock_value, timeout=timeout + 15):
        raise XhsServiceError("小红书服务正在处理另一个查询，请稍后重试")
    lock_fd = None
    file_locked = False
    try:
        # The production settings may use DummyCache. A host-wide file lock still
        # serializes every Django worker that shares this local MCP browser.
        lock_path = os.environ.get("XHS_MCP_LOCK_FILE") or os.path.join(tempfile.gettempdir(), "modeshift-xhs-mcp.lock")
        try:
            lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
        except OSError as exc:
            raise XhsServiceError("小红书服务访问锁不可用，请联系管理员检查配置") from exc
        try:
            _lock_file(lock_fd)
            file_locked = True
        except OSError as exc:
            raise XhsServiceError("小红书服务正在处理另一个查询，请稍后重试") from exc
        try:
            if os.name != "nt":
                os.lseek(lock_fd, 0, os.SEEK_SET)
            last_call = float(os.read(lock_fd, 64) or b"0")
        except ValueError:
            last_call = 0
        wait = 2.0 - (time.monotonic() - last_call)
        if 0 < wait <= 2.0:
            time.sleep(wait)
        try:
            daily_limit = max(1, min(int(os.environ.get("XHS_MCP_DAILY_REQUEST_LIMIT", "80")), 1000))
        except ValueError:
            daily_limit = 80
        budget_key = f"xhs-agent:mcp-daily-requests:{timezone.localdate().isoformat()}"
        daily_count = int(cache.get(budget_key, 0) or 0)
        if daily_count >= daily_limit:
            raise XhsServiceError("小红书今日安全访问额度已用完，请明天再试；不会继续请求以降低账号风险")
        cache.set(budget_key, daily_count + 1, timeout=27 * 60 * 60)
        response = requests.request(method, f"{base}{path}", json=payload, headers=headers, timeout=timeout)
    except requests.Timeout as exc:
        raise XhsServiceError("小红书页面加载超时，请稍后重试或直接粘贴完整主页链接") from exc
    except requests.RequestException as exc:
        raise XhsServiceError("小红书 MCP 服务未连接，请联系管理员启动服务") from exc
    finally:
        if lock_fd is not None:
            if file_locked:
                os.lseek(lock_fd, 1 if os.name == "nt" else 0, os.SEEK_SET)
                os.write(lock_fd, f"{time.monotonic():.6f}".ljust(32).encode())
                _unlock_file(lock_fd)
            os.close(lock_fd)
        if cache.get(lock_key) == lock_value:
            cache.delete(lock_key)
    if response.status_code == 401:
        raise XhsServiceError("小红书 MCP 鉴权失败，请管理员检查服务密钥")
    if response.status_code in {500, 502, 504}:
        # The MCP browser can lose the target during XHS navigation. A single
        # delayed retry lets it create a fresh page without turning a transient
        # browser crash into a permanent profile failure.
        time.sleep(1.2)
        try:
            retry = requests.request(method, f"{base}{path}", json=payload, headers=headers, timeout=timeout)
            if retry.status_code < 400:
                response = retry
            else:
                raise XhsServiceError("小红书 MCP 浏览器读取页面失败，请稍后重试")
        except requests.RequestException as exc:
            raise XhsServiceError("小红书 MCP 浏览器读取页面失败，请稍后重试") from exc
    if response.status_code >= 400:
        raise XhsServiceError("小红书 MCP 查询失败，请确认已登录并稍后重试")
    try:
        body = response.json()
    except ValueError as exc:
        raise XhsServiceError("小红书 MCP 返回了无法解析的数据") from exc
    if not isinstance(body, dict) or body.get("success") is not True:
        raise XhsServiceError("小红书 MCP 未返回查询结果，请确认登录状态")
    return body


def login_status() -> dict:
    data = _data(_call_mcp("GET", "/api/v1/login/status", timeout=15))
    return {"is_logged_in": bool(data.get("is_logged_in")), "username": data.get("username", "")}


def login_qrcode() -> dict:
    data = _data(_call_mcp("GET", "/api/v1/login/qrcode", timeout=60))
    image = data.get("img", "")
    if data.get("is_logged_in") and not image:
        return {"is_logged_in": True, "timeout": data.get("timeout", "0s")}
    if not isinstance(image, str) or not image.startswith("data:image/png;base64,"):
        raise XhsServiceError("小红书 MCP 未返回登录二维码")
    return {"img": image, "timeout": data.get("timeout", "300")}


def search_profile_candidates(keyword: str) -> list[dict]:
    keyword = (keyword or "").strip()
    if len(keyword) < 2 or len(keyword) > 80:
        raise XhsInputError("请输入 2 到 80 个字符的昵称或关键词")
    # The upstream GET variant accepts a keyword query; POST keeps it out of URL logs.
    cache_key = "xhs-agent:search:" + hashlib.sha256(keyword.encode()).hexdigest()
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    if cache.get(cache_key + ":failed"):
        raise XhsServiceError("该关键词刚查询失败，请稍后重试或粘贴完整主页链接")
    try:
        body = _call_mcp("POST", "/api/v1/feeds/search", payload={"keyword": keyword}, timeout=60)
    except XhsServiceError:
        cache.set(cache_key + ":failed", True, timeout=120)
        raise
    feeds = _data(body).get("feeds", [])
    if not isinstance(feeds, list):
        return []
    candidates = []
    seen = set()
    for feed in feeds:
        if not isinstance(feed, dict):
            continue
        user = (feed.get("noteCard") or {}).get("user") or {}
        user_id = user.get("userId", "")
        token = feed.get("xsecToken", "")
        if not user_id or not token or user_id in seen:
            continue
        seen.add(user_id)
        candidates.append(
            {
                "user_id": user_id,
                "xsec_token": token,
                "nickname": user.get("nickname") or user.get("nickName") or "未知用户",
                "avatar": user.get("avatar") or "",
                "source_note": (feed.get("noteCard") or {}).get("displayTitle") or "",
            }
        )
        # Keep the complete first search page. A unique creator can appear
        # below the first dozen notes even when the keyword is exact.
        if len(candidates) >= 50:
            break
    keyword_folded = keyword.casefold()
    candidates.sort(key=lambda item: (0 if str(item.get("nickname", "")).casefold() == keyword_folded else 1, -len(str(item.get("nickname", "")))))
    cache.set(cache_key, candidates, timeout=300)
    return candidates


def read_profile(user_id: str, xsec_token: str) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9]{1,64}", user_id or ""):
        raise XhsInputError("用户 ID 格式不正确")
    if not xsec_token or len(xsec_token) > 1024:
        raise XhsInputError("缺少有效的 xsec_token")
    cache_key = "xhs-agent:profile:" + hashlib.sha256(f"{user_id}:{xsec_token}".encode()).hexdigest()
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    if cache.get(cache_key + ":failed"):
        raise XhsServiceError("该主页刚查询失败，请稍后再试")
    try:
        data = _data(
            _call_mcp(
                "POST",
                "/api/v1/user/profile",
                # Let the MCP use its default profile tab. Some accounts expose
                # notes under a different tab and the forced "note" tab waits
                # until Rod's deadline even though the profile is readable.
                payload={"user_id": user_id, "xsec_token": xsec_token, "tab": ""},
                timeout=75,
            )
        )
    except XhsServiceError:
        cache.set(cache_key + ":failed", True, timeout=120)
        raise
    info = data.get("userBasicInfo") or {}
    interactions = data.get("interactions") or []
    counts = {item.get("type"): item.get("count", "") for item in interactions if isinstance(item, dict)}
    feeds = data.get("feeds") or []
    # A public profile can legitimately have no visible notes, or the
    # upstream page may omit the feed tab while still returning profile
    # counts. Keep the profile usable for following/count monitoring.
    if not isinstance(feeds, list):
        feeds = []
    notes = []
    for feed in feeds[:200]:
        if not isinstance(feed, dict):
            continue
        card = feed.get("noteCard") or feed.get("feedCard") or feed.get("note_card") or {}
        cover = card.get("cover") or {}
        note_id, note_token = _note_id_and_token(feed, card)
        if not note_id:
            continue
        note_url = ""
        if note_id and note_token:
            note_url = (
                f"https://www.xiaohongshu.com/explore/{quote(note_id, safe='')}"
                f"?xsec_token={quote(note_token, safe='')}&xsec_source=pc_user"
            )
        notes.append(
            {
                "id": note_id,
                "xsec_token": note_token,
                "title": card.get("displayTitle") or "未命名笔记",
                "cover": _cover_url(feed, card).replace("http://", "https://", 1),
                "likes": (card.get("interactInfo") or {}).get("likedCount") or "",
                "url": note_url,
            }
        )
    notes_unavailable = not notes
    profile = {
        "user_id": user_id,
        "nickname": info.get("nickname") or "未知用户",
        "description": info.get("desc") or "",
        "avatar": info.get("images") or "",
        "red_id": info.get("redId") or "",
        "counts": counts,
        "notes": notes,
        "note_count_loaded": len(notes),
        "notes_unavailable": notes_unavailable,
        "is_truncated": len(feeds) > len(notes),
        "fetched_at": timezone.now().isoformat(),
    }
    cache.set(cache_key, profile, timeout=300)
    return profile


def read_note_detail(note_id: str, xsec_token: str) -> dict:
    """Fetch a newly observed note's description and pictures for the alert."""
    if not re.fullmatch(r"[A-Za-z0-9]{1,64}", note_id or "") or not xsec_token:
        raise XhsInputError("笔记参数不完整")
    data = _data(
        _call_mcp(
            "POST",
            "/api/v1/feeds/detail",
            payload={"feed_id": note_id, "xsec_token": xsec_token, "load_all_comments": False},
            timeout=20,
        )
    )
    note = data.get("note") or {}
    return {
        "description": (note.get("desc") or "")[:800],
        "images": [
            image.get("urlDefault") or image.get("url")
            for image in (note.get("imageList") or [])[:3]
            if isinstance(image, dict) and (image.get("urlDefault") or image.get("url"))
        ],
        "published_at": note.get("time"),
    }
