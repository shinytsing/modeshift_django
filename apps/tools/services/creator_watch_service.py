"""Per-user daily creator snapshots across supported social platforms."""

from __future__ import annotations

from datetime import timedelta
from difflib import SequenceMatcher
from urllib.parse import quote

from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.core.validators import validate_email
from django.db import transaction
from django.utils import timezone

from apps.tools.models import SocialMediaNotification, SocialMediaSubscription
from apps.tools.services import creator_sources
from apps.tools.services import xiaohongshu_profile_agent as xhs
from apps.tools.services import xiaohongshu_watch_service as xhs_watch


AGENT_MARKER = "creatorWatchAgent"
STATE_KEY = "creator_agent"


def _creator_hint(message: str) -> str:
    """Return an explicit creator name left after removing query boilerplate."""
    value = message.lower()
    boilerplate = (
        "xiaohongshu",
        "小红书",
        "bilibili",
        "哔哩哔哩",
        "b站",
        "b 站",
        "网易云音乐",
        "网易云",
        "立即刷新",
        "重新检查",
        "强制刷新",
        "帮我查一下",
        "帮我看看",
        "查一下",
        "看一下",
        "看看",
        "请问",
        "今天",
        "昨天",
        "最近",
        "有没有更新",
        "是否更新",
        "更新了吗",
        "更新了么",
        "有更新吗",
        "发新内容了吗",
        "发笔记了吗",
        "更新",
        "了吗",
        "了么",
        "是否",
        "有吗",
    )
    for word in boilerplate:
        value = value.replace(word, "")
    for token in " ，。！？?：:、·-_/()（）[]【】\t\r\n":
        value = value.replace(token, "")
    return value.strip()


def _normalized_creator_name(value: str) -> str:
    value = (value or "").strip().lower()
    for token in " ，。！？?：:、·-_/()（）[]【】\t\r\n":
        value = value.replace(token, "")
    return value


def _candidate_score(nickname: str, wanted: str) -> float:
    """Rank public search hits without treating similarity as identity proof."""
    name = _normalized_creator_name(nickname)
    target = _normalized_creator_name(wanted)
    if not name or not target:
        return 0.0
    score = SequenceMatcher(None, name, target).ratio()
    if target in name or name in target:
        score += 0.35
    return min(score, 1.0)


def _search_platforms(message: str, watches: list[SocialMediaSubscription]) -> list[str]:
    aliases = (
        ("xiaohongshu", ("小红书", "xiaohongshu", "xhs")),
        ("bilibili", ("哔哩哔哩", "bilibili", "b站", "b 站")),
        ("netease", ("网易云音乐", "网易云")),
        ("weibo", ("微博", "weibo")),
    )
    lowered = message.lower()
    explicit = [platform for platform, names in aliases if any(name in lowered for name in names)]
    if explicit:
        return explicit
    subscribed = [item.platform for item in watches if item.platform in creator_sources.SUPPORTED_PLATFORMS]
    ordered = []
    for platform in subscribed + ["xiaohongshu", "bilibili", "netease"]:
        if platform not in ordered:
            ordered.append(platform)
    return ordered


def _discover_creator(user, message: str, watches: list[SocialMediaSubscription], hint: str) -> dict:
    searched = []
    related = []
    related_candidates = []
    errors = []
    exact_matches = []
    wanted = _normalized_creator_name(hint)
    for platform in _search_platforms(message, watches):
        label = creator_sources.PLATFORM_LABELS.get(platform, platform)
        searched.append(label)
        try:
            cache_key = f"creator-agent-search:{platform}:{_normalized_creator_name(hint)}"
            candidates = cache.get(cache_key)
            if candidates is None:
                candidates = creator_sources.search_candidates(platform, hint)
                cache.set(cache_key, candidates, timeout=300)
        except xhs.XhsServiceError as exc:
            errors.append(f"{label}：{exc}")
            continue
        exact = [
            candidate for candidate in candidates if _normalized_creator_name(str(candidate.get("nickname") or "")) == wanted
        ]
        for candidate in exact:
            exact_matches.append({**candidate, "platform": platform, "platform_label": label})
        related.extend(
            f"{label} {candidate.get('nickname') or '未知用户'}" for candidate in candidates[:3] if candidate.get("nickname")
        )
        for candidate in candidates[:8]:
            if candidate.get("nickname"):
                related_candidates.append(
                    {
                        **candidate,
                        "platform": platform,
                        "platform_label": label,
                        "match_score": _candidate_score(str(candidate.get("nickname") or ""), hint),
                    }
                )
    if len(exact_matches) > 1:
        labels = "、".join(dict.fromkeys(item["platform_label"] for item in exact_matches))
        return {
            "answer": f"Agent 已搜索{labels}，找到多个昵称为“{hint}”的账号。请从下面选择正确账号后再关注。",
            "new_notes": [],
            "discovered": False,
            "discovery_candidates": exact_matches,
        }
    if len(exact_matches) == 1:
        candidate = exact_matches[0]
        platform = candidate["platform"]
        label = candidate["platform_label"]
        try:
            item, created = subscribe(
                user, platform, str(candidate.get("user_id") or ""), str(candidate.get("xsec_token") or "")
            )
        except (xhs.XhsInputError, xhs.XhsServiceError) as exc:
            errors.append(f"{label}：找到同名账号，但主页读取失败（{exc}）")
        else:
            watch = serialize_watch(item)
            action = "已自动关注" if created else "已找到已有关注"
            return {
                "answer": f"Agent 在{label}找到昵称精确匹配的“{watch['nickname']}”，{action}。已建立今天的首次快照，本次可见 {watch['last_visible_count'] or 0} 条；因为没有昨天的记录，今天暂时不能判断是否更新，之后会自动对比。",
                "comparison": "baseline",
                "baseline_date": None,
                "checked_date": watch["last_snapshot_date"],
                "previous_visible_count": None,
                "current_visible_count": watch["last_visible_count"] or 0,
                "new_count": 0,
                "new_notes": [],
                "watch": watch,
                "discovered": True,
            }
    if related:
        examples = "、".join(dict.fromkeys(related))
        answer = (
            f"Agent 已搜索{'、'.join(searched)}，找到相关结果（{examples}），"
            f"但没有昵称精确匹配“{hint}”的账号，为避免关注错人没有自动订阅。"
            "已按相关度排列候选；请先选择最可能的账号，或直接粘贴该用户的主页完整链接。"
        )
    else:
        answer = f"Agent 已搜索{'、'.join(searched)}，没有找到“{hint}”。建议直接粘贴该用户的主页完整链接。"
    if errors:
        answer += f" 部分平台暂时不可用：{'；'.join(errors)}。"
    related_candidates.sort(key=lambda item: item.get("match_score", 0), reverse=True)
    return {
        "answer": answer,
        "new_notes": [],
        "discovered": False,
        "discovery_candidates": related_candidates[:3],
        "web_search_url": f"https://www.xiaohongshu.com/search_result?keyword={quote(hint)}",
    }


def _https_url(value: object) -> str:
    if not isinstance(value, str):
        return ""
    if value.startswith("http://"):
        return "https://" + value[7:]
    return value if value.startswith("https://") else ""


def _public_note(note: dict) -> dict:
    return {
        **{key: note.get(key, "") for key in ("id", "title", "description", "likes")},
        "cover": _https_url(note.get("cover")),
        "url": _https_url(note.get("url")),
    }


def _public_snapshot(snapshot: dict) -> dict:
    return {
        "date": snapshot.get("date"),
        "checked_at": snapshot.get("checked_at"),
        "source_fetched_at": snapshot.get("source_fetched_at"),
        "visible_count": snapshot.get("visible_count", 0),
        "is_truncated": bool(snapshot.get("is_truncated")),
        "notes": [_public_note(note) for note in snapshot.get("notes") or [] if isinstance(note, dict)],
    }


def _key(item: SocialMediaSubscription) -> str:
    return xhs_watch.STATE_KEY if item.platform == "xiaohongshu" else STATE_KEY


def _state(item: SocialMediaSubscription) -> dict:
    data = item.last_profile_data or {}
    if not isinstance(data, dict):
        return {}
    state = data.get(_key(item)) or {}
    return state if isinstance(state, dict) else {}


def list_watches(user) -> list[SocialMediaSubscription]:
    """Show every subscription owned by this Model Shift user, including older rows."""
    return list(SocialMediaSubscription.objects.filter(user=user).order_by("-created_at"))


def serialize_watch(item: SocialMediaSubscription) -> dict:
    from apps.tools.services.creator_email_policy import get_email

    state = _state(item)
    history = state.get("history") or []
    latest = history[-1] if history else {}
    latest_update = state.get("latest_update") or None
    trend = [{"date": entry.get("date"), "profile_counts": entry.get("profile_counts") or {}} for entry in history[-14:]]
    if latest_update:
        latest_update = {
            **latest_update,
            "notes": [_public_note(note) for note in latest_update.get("notes") or [] if isinstance(note, dict)],
        }
    return {
        "id": item.pk,
        "platform": item.platform,
        "platform_label": creator_sources.PLATFORM_LABELS.get(item.platform, item.platform),
        "user_id": item.target_user_id,
        "nickname": item.target_user_name,
        "avatar": item.avatar_url or "",
        "status": item.status,
        "monitoring_enabled": bool(history),
        "last_checked_at": latest.get("checked_at"),
        "last_snapshot_date": latest.get("date"),
        "last_visible_count": latest.get("visible_count"),
        "alert_email": get_email(item.user_id),
        "latest_update": latest_update,
        "trend": trend,
    }


def set_alert_email(user, watch_id: int, email: str) -> SocialMediaSubscription:
    if not isinstance(email, str) or len(email) > 254:
        raise xhs.XhsInputError("邮箱地址格式不正确")
    email = email.strip()
    if email:
        try:
            validate_email(email)
        except ValidationError as exc:
            raise xhs.XhsInputError("邮箱地址格式不正确") from exc
    with transaction.atomic():
        item = SocialMediaSubscription.objects.filter(pk=watch_id, user=user).first()
        if not item:
            raise xhs.XhsInputError("找不到这个订阅")
        from apps.tools.services.creator_email_policy import set_email

        set_email(user.pk, email)
    return item


def _snapshot(profile: dict, date: str) -> dict:
    return {
        "date": date,
        "checked_at": timezone.now().isoformat(),
        "source_fetched_at": profile.get("fetched_at") or timezone.now().isoformat(),
        "visible_count": len(profile["notes"]),
        "is_truncated": bool(profile.get("is_truncated")),
        "notes": [
            {key: note.get(key, "") for key in ("id", "title", "description", "cover", "url", "likes")}
            for note in profile["notes"]
            if note.get("id")
        ],
    }


def subscribe(user, platform: str, user_id: str, token: str = "") -> tuple[SocialMediaSubscription, bool]:
    if platform == "xiaohongshu":
        return xhs_watch.subscribe(user, user_id, token)
    if platform not in creator_sources.SUPPORTED_PLATFORMS:
        raise xhs.XhsInputError("该平台暂无可用的真实主页读取源")
    profile = creator_sources.read_profile(platform, user_id)
    today = timezone.localdate().isoformat()
    with transaction.atomic():
        item, created = SocialMediaSubscription.objects.select_for_update().get_or_create(
            user=user,
            platform=platform,
            target_user_id=user_id,
            defaults={
                "target_user_name": profile["nickname"],
                "avatar_url": profile.get("avatar") or "",
                "subscription_types": [AGENT_MARKER],
                "last_profile_data": {STATE_KEY: {"history": [_snapshot(profile, today)]}},
            },
        )
        if not created:
            data = item.last_profile_data or {}
            state = data.get(STATE_KEY) or {}
            if not state.get("history"):
                state["history"] = [_snapshot(profile, today)]
            data[STATE_KEY] = state
            types = list(item.subscription_types or [])
            if AGENT_MARKER not in types:
                types.append(AGENT_MARKER)
            item.subscription_types = types
            item.last_profile_data = data
            item.target_user_name = profile["nickname"]
            item.avatar_url = profile.get("avatar") or ""
            item.status = "active"
            item.save()
    return item, created


def check_watch(item: SocialMediaSubscription) -> dict:
    if item.platform == "xiaohongshu":
        if xhs_watch.AGENT_MARKER not in (item.subscription_types or []):
            raise xhs.XhsInputError("旧小红书订阅缺少主页访问令牌，请在上方重新粘贴主页链接建立基线")
        return xhs_watch.check_watch(item)
    if item.platform not in creator_sources.SUPPORTED_PLATFORMS:
        raise xhs.XhsServiceError(f"{creator_sources.PLATFORM_LABELS.get(item.platform, '该平台')} 暂无可用的真实读取源")
    profile = creator_sources.read_profile(item.platform, item.target_user_id)
    today = timezone.localdate()
    today_string = today.isoformat()
    yesterday = (today - timedelta(days=1)).isoformat()
    current = _snapshot(profile, today_string)
    with transaction.atomic():
        locked = SocialMediaSubscription.objects.select_for_update().get(pk=item.pk)
        data = locked.last_profile_data or {}
        state = data.get(STATE_KEY) or {}
        history = [entry for entry in state.get("history") or [] if isinstance(entry, dict)]
        earlier = [entry for entry in history if entry.get("date", "") < today_string]
        baseline = next((entry for entry in reversed(earlier) if entry.get("date") == yesterday), None)
        if baseline is None and earlier:
            baseline = earlier[-1]
        seen_ids = {note.get("id") for entry in earlier for note in entry.get("notes") or []}
        new_notes = [note.copy() for note in current["notes"] if baseline and note["id"] not in seen_ids]
        history = [entry for entry in history if entry.get("date") != today_string]
        history.append(current)
        state["history"] = history[-14:]
        data[STATE_KEY] = state
        locked.last_profile_data = data
        locked.target_user_name = profile["nickname"]
        locked.avatar_url = profile.get("avatar") or ""
        types = list(locked.subscription_types or [])
        if AGENT_MARKER not in types:
            types.append(AGENT_MARKER)
        locked.subscription_types = types
        locked.save()
        for note in new_notes:
            if not SocialMediaNotification.objects.filter(
                subscription=locked, notification_type="newPosts", data__item_id=note["id"]
            ).exists():
                SocialMediaNotification.objects.create(
                    subscription=locked,
                    notification_type="newPosts",
                    title=f"{profile['nickname']} 发布了新内容",
                    content=note["title"],
                    external_url=note["url"] if len(note["url"]) <= 200 else "",
                    data={"source": STATE_KEY, "item_id": note["id"], "snapshot_date": today_string},
                )
    label = creator_sources.PLATFORM_LABELS[item.platform]
    if baseline is None:
        comparison = "baseline"
        answer = f"已记录 {label} · {profile['nickname']} 的今天快照：本次读取 {current['visible_count']} 条可见内容。还没有昨天的快照，暂时不能判断是否更新。"
    else:
        comparison = "yesterday" if baseline["date"] == yesterday else "earlier"
        reference = "昨天" if comparison == "yesterday" else f"上次记录（{baseline['date']}）"
        if new_notes:
            titles = "；".join(f"《{entry['title']}》" for entry in new_notes[:5])
            answer = f"{label} · {profile['nickname']} 与{reference}相比，发现 {len(new_notes)} 条新内容：{titles}。"
        else:
            answer = f"{label} · {profile['nickname']} 与{reference}相比，在本次可见内容中没有发现新增。"
        answer += f" {reference}读取 {baseline['visible_count']} 条，本次读取 {current['visible_count']} 条。"
    if current["is_truncated"]:
        answer += " 内容列表未完整加载，结果可能不完整。"
    public_new_notes = [_public_note(note) for note in new_notes]
    with transaction.atomic():
        locked = SocialMediaSubscription.objects.select_for_update().get(pk=item.pk)
        data = locked.last_profile_data or {}
        state = data.get(STATE_KEY) or {}
        state["last_result"] = {"answer": answer, "checked_at": timezone.now().isoformat()}
        if public_new_notes:
            state["latest_update"] = {
                "date": today_string,
                "checked_at": timezone.now().isoformat(),
                "count": len(public_new_notes),
                "notes": public_new_notes,
            }
        data[STATE_KEY] = state
        locked.last_profile_data = data
        locked.save(update_fields=["last_profile_data", "updated_at"])
    return {
        "answer": answer,
        "comparison": comparison,
        "baseline_date": baseline["date"] if baseline else None,
        "checked_date": today_string,
        "source_fetched_at": current["source_fetched_at"],
        "previous_visible_count": baseline.get("visible_count") if baseline else None,
        "current_visible_count": current["visible_count"],
        "new_count": len(public_new_notes),
        "new_notes": public_new_notes,
        "watch": serialize_watch(locked),
    }


def _today_result(item: SocialMediaSubscription) -> dict | None:
    if item.platform == "xiaohongshu":
        return xhs_watch._today_result(item)
    state = _state(item)
    today = timezone.localdate().isoformat()
    last_result = state.get("last_result") or {}
    if not str(last_result.get("checked_at") or "").startswith(today):
        return None
    history = [entry for entry in state.get("history") or [] if isinstance(entry, dict)]
    current = next((entry for entry in reversed(history) if entry.get("date") == today), None)
    if current is None:
        return None
    earlier = [entry for entry in history if entry.get("date", "") < today]
    baseline = earlier[-1] if earlier else None
    latest = state.get("latest_update") or {}
    notes = latest.get("notes") or [] if latest.get("date") == today else []
    public_notes = [_public_note(note) for note in notes if isinstance(note, dict)]
    answer = str(last_result.get("answer") or "暂无检查结果") + " 这是今天已保存的检查结果。"
    yesterday = (timezone.localdate() - timedelta(days=1)).isoformat()
    return {
        "answer": answer,
        "comparison": "yesterday" if baseline and baseline.get("date") == yesterday else "earlier",
        "baseline_date": baseline.get("date") if baseline else None,
        "checked_date": today,
        "source_fetched_at": current.get("source_fetched_at"),
        "previous_visible_count": baseline.get("visible_count") if baseline else None,
        "current_visible_count": current.get("visible_count", 0),
        "new_count": len(public_notes),
        "new_notes": public_notes,
        "cached": True,
        "watch": serialize_watch(item),
    }


def reply_to_message(user, message: str, *, refresh: bool = True) -> dict:
    message = (message or "").strip()
    if not message or len(message) > 300:
        raise xhs.XhsInputError("请输入不超过 300 字的查询消息")
    watches = [item for item in list_watches(user) if item.status == "active"]
    if not watches:
        hint = _creator_hint(message)
        if hint:
            return _discover_creator(user, message, watches, hint)
        return {"answer": "你还没有订阅用户。请先搜索或粘贴主页链接后订阅。", "new_notes": []}
    matches = [item for item in watches if item.target_user_name in message or item.target_user_id in message]
    if len(matches) > 1:
        narrowed = [item for item in matches if creator_sources.PLATFORM_LABELS.get(item.platform, "") in message]
        matches = narrowed if len(narrowed) == 1 else matches
    if len(matches) == 1:
        target = matches[0]
    elif len(watches) == 1 and not _creator_hint(message):
        target = watches[0]
    else:
        names = "、".join(
            f"{creator_sources.PLATFORM_LABELS.get(item.platform, item.platform)} {item.target_user_name}"
            for item in watches[:8]
        )
        hint = _creator_hint(message)
        if not matches and hint:
            return _discover_creator(user, message, watches, hint)
        return {"answer": f"你订阅了多个用户，请写出平台和昵称：{names}。", "new_notes": []}
    force_refresh = any(word in message for word in ("立即刷新", "重新检查", "强制刷新"))
    if refresh and not force_refresh:
        cached = _today_result(target)
        if cached:
            return cached
    if refresh:
        return check_watch(target)
    last_result = _state(target).get("last_result") or {}
    if not last_result:
        return {"answer": f"{target.target_user_name} 尚未完成每日检查，请稍后在网页查询。", "new_notes": []}
    return {"answer": f"{last_result.get('answer', '暂无检查结果')}\n检查时间：{last_result.get('checked_at', '未知')}", "new_notes": []}
