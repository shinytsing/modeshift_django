"""Read-only, normalized creator profiles for the daily watch Agent."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from urllib.parse import parse_qs, urlparse

import requests
from django.core.cache import cache
from django.utils import timezone

from apps.tools.services import xiaohongshu_profile_agent as xhs


SUPPORTED_PLATFORMS = {"xiaohongshu": "小红书", "bilibili": "B 站", "netease": "网易云音乐", "weibo": "微博"}
PLATFORM_LABELS = {**SUPPORTED_PLATFORMS, "douyin": "抖音", "weibo": "微博"}


def parse_profile_link(platform: str, value: str) -> tuple[str, str]:
    if not isinstance(platform, str) or not isinstance(value, str):
        raise xhs.XhsInputError("平台或主页链接格式不正确")
    if platform == "xiaohongshu":
        return xhs.parse_profile_link(value)
    parsed = urlparse((value or "").strip())
    if parsed.scheme not in ("http", "https") or len(value or "") > 2048:
        raise xhs.XhsInputError("请粘贴完整的用户主页链接")
    host = (parsed.hostname or "").lower()
    if platform == "bilibili":
        match = re.fullmatch(r"/(\d{1,20})/?", parsed.path)
        if host != "space.bilibili.com" or not match:
            raise xhs.XhsInputError("请粘贴 space.bilibili.com/数字UID 形式的 B 站主页")
        return match.group(1), ""
    if platform == "netease":
        if host != "music.163.com":
            raise xhs.XhsInputError("请粘贴 music.163.com 的用户主页")
        route = parsed.fragment if parsed.fragment.startswith("/user/") else parsed.path + "?" + parsed.query
        route_parsed = urlparse(route)
        user_id = parse_qs(route_parsed.query).get("id", [""])[0]
        if not route_parsed.path.rstrip("/").endswith("/user/home") or not re.fullmatch(r"\d{1,20}", user_id):
            raise xhs.XhsInputError("网易云链接需指向用户主页并包含数字 ID")
        return user_id, ""
    if platform == "weibo":
        match = re.fullmatch(r"/(?:u/)?(\d{1,20})/?", parsed.path)
        if host not in {"weibo.com", "www.weibo.com", "m.weibo.cn"} or not match:
            raise xhs.XhsInputError("请粘贴 weibo.com/u/数字ID 形式的微博主页")
        return match.group(1), ""
    raise xhs.XhsInputError(f"{PLATFORM_LABELS.get(platform, '该平台')} 尚未配置可靠的主页读取")


def _netease_call(path: str, *, payload: dict | None = None) -> dict:
    url = "https://music.163.com" + path
    try:
        response = (
            requests.post(
                url, data=payload, timeout=12, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://music.163.com/"}
            )
            if payload is not None
            else requests.get(url, timeout=12, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://music.163.com/"})
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise xhs.XhsServiceError("网易云音乐接口暂时无法读取，请稍后再试") from exc
    if not isinstance(data, dict) or data.get("code") != 200:
        raise xhs.XhsServiceError("网易云音乐未返回有效结果，请检查主页或登录状态")
    return data


def _weibo_call(path: str, *, params: dict | None = None) -> dict:
    try:
        response = requests.get("https://m.weibo.cn" + path, params=params, timeout=12,
                               headers={"User-Agent": "Mozilla/5.0", "Referer": "https://m.weibo.cn/"})
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise xhs.XhsServiceError("微博接口暂时无法读取，请稍后再试") from exc
    if not isinstance(data, dict) or data.get("ok") != 1:
        raise xhs.XhsServiceError("微博未返回有效结果，请稍后再试")
    return data


def _bili_call(*args: str) -> object:
    cooldown_key = "creator-source:bilibili:blocked"
    if cache.get(cooldown_key):
        raise xhs.XhsServiceError("B 站视频接口触发平台风控，已暂停请求 1 小时，请稍后再试")
    binary = shutil.which("bili")
    if not binary:
        # Keep the service usable on a clean Linux/Windows install.  The
        # optional bili-cli is preferred, but public B 站 card data can be
        # read without a local executable.  This deliberately avoids
        # scraping HTML and only uses the public API.
        if args and args[0] == "user" and len(args) >= 2:
            try:
                response = requests.get(
                    "https://api.bilibili.com/x/web-interface/card",
                    params={"mid": args[1]},
                    headers={"User-Agent": "Mozilla/5.0", "Referer": "https://space.bilibili.com/"},
                    timeout=12,
                )
                response.raise_for_status()
                payload = response.json()
                if payload.get("code") == 0:
                    card = payload.get("data", {}).get("card", {})
                    return {"user": card, "relation": {"follower": payload.get("data", {}).get("follower", 0)}}
            except (requests.RequestException, ValueError):
                pass
        raise xhs.XhsServiceError("B 站读取工具尚未安装，且公开接口暂时不可用，请管理员安装 bilibili-cli")
    try:
        run = subprocess.run([binary, *args, "--json"], capture_output=True, text=True, timeout=25, check=False)
        data = json.loads(run.stdout)
    except (subprocess.TimeoutExpired, ValueError, OSError) as exc:
        raise xhs.XhsServiceError("B 站接口暂时无法读取，请稍后再试") from exc
    if isinstance(data, dict) and data.get("ok") is False:
        error = data.get("error") or {}
        if "412" in str(error):
            cache.set(cooldown_key, True, timeout=3600)
            raise xhs.XhsServiceError("B 站视频接口触发平台风控，已暂停请求 1 小时，请稍后再试")
    if run.returncode != 0 or not isinstance(data, dict) or data.get("ok") is not True:
        raise xhs.XhsServiceError("B 站未返回有效结果，请检查用户 UID 或登录状态")
    return data.get("data")


def search_candidates(platform: str, keyword: str) -> list[dict]:
    if not isinstance(platform, str) or not isinstance(keyword, str):
        raise xhs.XhsInputError("平台或昵称格式不正确")
    keyword = (keyword or "").strip()
    if len(keyword) < 2 or len(keyword) > 80:
        raise xhs.XhsInputError("请输入 2 到 80 个字符的昵称")
    if platform == "xiaohongshu":
        try:
            from apps.tools.services.xiaohongshu_user_search import search_users
            users = search_users(keyword)
            if users:
                return [{**item, "platform": platform, "platform_label": PLATFORM_LABELS[platform]} for item in users]
        except xhs.XhsServiceError:
            # The browser-session adapter is optional; retain the official
            # MCP fallback when its persistent profile is not logged in.
            pass
        return xhs.search_profile_candidates(keyword)
    if platform == "bilibili":
        users = _bili_call("search", keyword, "--type", "user", "-n", "8")
        candidates = [
            {
                "user_id": str(user.get("id")),
                "nickname": user.get("name") or "未知用户",
                "avatar": user.get("face") or user.get("avatar") or "",
                "source_note": f"粉丝 {user.get('fans', 0)}",
                "xsec_token": "",
            }
            for user in users or []
            if user.get("id")
        ]
        # bili-cli versions differ in whether they include faces. Enrich a
        # small candidate set from the public card endpoint for a consistent
        # avatar-first picker without making eight extra requests.
        for candidate in candidates[:3]:
            if candidate.get("avatar"):
                continue
            try:
                card = requests.get(
                    "https://api.bilibili.com/x/web-interface/card",
                    params={"mid": candidate["user_id"]},
                    headers={"User-Agent": "Mozilla/5.0", "Referer": "https://space.bilibili.com/"},
                    timeout=5,
                ).json()
                candidate["avatar"] = ((card.get("data") or {}).get("card") or {}).get("face") or ""
            except (requests.RequestException, ValueError):
                pass
        return candidates
    if platform == "netease":
        data = _netease_call("/api/search/get", payload={"s": keyword, "type": 1002, "limit": 8, "offset": 0})
        users = (data.get("result") or {}).get("userprofiles") or []
        return [
            {
                "user_id": str(user["userId"]),
                "nickname": user.get("nickname") or "未知用户",
                "avatar": user.get("avatarUrl") or "",
                "source_note": user.get("signature") or "",
                "xsec_token": "",
            }
            for user in users
            if user.get("userId")
        ]
    if platform == "weibo":
        try:
            run = subprocess.run(["weibo-cli", "users", keyword, "-n", "8"], capture_output=True, text=True, timeout=20, check=False)
            cli_users = json.loads(run.stdout) if run.returncode == 0 else []
        except (OSError, subprocess.TimeoutExpired, ValueError):
            cli_users = []
        if isinstance(cli_users, list) and cli_users:
            return [{"user_id": str(u["id"]), "nickname": u.get("screen_name") or "未知用户", "avatar": u.get("avatar_hd") or u.get("profile_image_url") or "", "source_note": u.get("description") or "", "xsec_token": ""} for u in cli_users if u.get("id")]
        data = _weibo_call("/api/container/getIndex", params={"containerid": "100103type=3", "q": keyword})
        candidates = []
        for card in (data.get("data") or {}).get("cards") or []:
            for item in card.get("card_group") or []:
                user = item.get("user") or {}
                if user.get("id"):
                    candidates.append({"user_id": str(user["id"]), "nickname": user.get("screen_name") or "未知用户",
                                      "avatar": user.get("profile_image_url") or "", "source_note": user.get("description") or "", "xsec_token": ""})
        return candidates[:8]
    raise xhs.XhsInputError(f"{PLATFORM_LABELS.get(platform, '该平台')} 暂未配置可用的数据源")


def read_profile(platform: str, user_id: str, token: str = "") -> dict:
    if not isinstance(platform, str) or not isinstance(user_id, str):
        raise xhs.XhsInputError("平台或用户 ID 格式不正确")
    if platform == "xiaohongshu":
        return xhs.read_profile(user_id, token)
    if platform not in SUPPORTED_PLATFORMS or not re.fullmatch(r"\d{1,20}", user_id or ""):
        raise xhs.XhsInputError("平台或用户 ID 格式不正确")
    cache_key = f"creator-source:{platform}:{user_id}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    if platform == "bilibili":
        data = _bili_call("user", user_id)
        try:
            videos = _bili_call("user-videos", user_id, "-n", "30")
        except xhs.XhsServiceError:
            # Profile metrics remain useful when the video endpoint is
            # rate-limited; do not discard a valid public profile snapshot.
            videos = []
        user = data.get("user") or {}
        relation = data.get("relation") or {}
        notes = [
            {
                "id": video["bvid"],
                "title": video.get("title") or "未命名视频",
                "description": video.get("description") or "",
                "url": video.get("url") or "",
                "cover": video.get("pic") or "",
                "likes": (video.get("stats") or {}).get("like") or "",
            }
            for video in videos or []
            if video.get("bvid")
        ]
        profile = {
            "nickname": user.get("name") or "未知用户",
            "avatar": user.get("face") or "",
            "description": user.get("sign") or "",
            "counts": {"fans": relation.get("follower")},
            "notes": notes,
            "is_truncated": bool(len(videos or []) >= 30),
        }
    elif platform == "weibo":
        data = _weibo_call("/api/container/getIndex", params={"containerid": f"100505{user_id}", "type": "uid", "value": user_id})
        user = (data.get("data") or {}).get("userInfo") or {}
        profile = {
            "nickname": user.get("screen_name") or "未知用户",
            "avatar": user.get("profile_image_url") or "",
            "description": user.get("description") or "",
            "counts": {"fans": user.get("followers_count"), "follows": user.get("follow_count")},
            "notes": [], "is_truncated": False,
        }
    else:
        data = _netease_call(f"/api/v1/user/detail/{user_id}")
        events = _netease_call(
            f"/api/event/get/{user_id}",
            payload={"getcounts": "true", "time": -1, "limit": 30, "total": "false", "fromRN": "true"},
        )
        user = data.get("profile") or {}
        notes = []
        for event in events.get("events") or []:
            event_id = event.get("id")
            if event_id is None:
                continue
            try:
                content = json.loads(event.get("json") or "{}")
            except ValueError:
                content = {}
            description = content.get("msg") or "" if isinstance(content, dict) else ""
            if not isinstance(description, str):
                description = str(description)
            notes.append(
                {
                    "id": str(event_id),
                    "title": (description.splitlines() or ["音乐动态"])[0][:100] or "音乐动态",
                    "description": description[:800],
                    "url": f"https://music.163.com/#/event?id={event_id}",
                    "cover": ((event.get("pics") or [{}])[0].get("originUrl") or "") if event.get("pics") else "",
                    "likes": (event.get("info") or {}).get("likedCount") or "",
                    "published_at": event.get("eventTime"),
                }
            )
        profile = {
            "nickname": user.get("nickname") or "未知用户",
            "avatar": user.get("avatarUrl") or "",
            "description": user.get("signature") or "",
            "counts": {"fans": user.get("followeds")},
            "notes": notes,
            "is_truncated": bool(events.get("more")),
        }
    if not profile["notes"] and platform == "xiaohongshu":
        raise xhs.XhsServiceError("主页未返回有效内容 ID，暂不建立更新快照")
    profile.update(
        {
            "user_id": user_id,
            "platform": platform,
            "note_count_loaded": len(profile["notes"]),
            "fetched_at": timezone.now().isoformat(),
        }
    )
    cache.set(cache_key, profile, timeout=300)
    return profile
