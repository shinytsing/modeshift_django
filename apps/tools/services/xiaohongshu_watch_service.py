"""Daily Xiaohongshu note snapshots shared by web and future message channels."""

from __future__ import annotations

from datetime import timedelta
from urllib.parse import quote

from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone

from apps.tools.models import SocialMediaNotification, SocialMediaSubscription
from apps.tools.services import xiaohongshu_profile_agent as profile_agent


AGENT_MARKER = "xhsProfileAgent"
STATE_KEY = "xhs_agent"


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
        "profile_counts": snapshot.get("profile_counts") or {},
        "notes": [_public_note(note) for note in snapshot.get("notes") or [] if isinstance(note, dict)],
    }


def _snapshot(profile: dict, date: str) -> dict:
    notes = [
        {key: note.get(key, "") for key in ("id", "xsec_token", "title", "cover", "likes", "url")}
        for note in profile.get("notes", [])
        if note.get("id")
    ]
    return {
        "date": date,
        "checked_at": timezone.now().isoformat(),
        "source_fetched_at": profile.get("fetched_at") or timezone.now().isoformat(),
        # An empty list can mean the MCP did not expose note IDs, not that the
        # creator has zero notes. Preserve that distinction in the snapshot.
        "visible_count": None if profile.get("notes_unavailable") else len(notes),
        "notes_unavailable": bool(profile.get("notes_unavailable")),
        "is_truncated": bool(profile.get("is_truncated")),
        "profile_counts": profile.get("counts") or {},
        "notes": notes,
    }


def _count_changes(previous: dict | None, current: dict) -> dict:
    previous = previous or {}
    current = current or {}
    labels = {"fans": "粉丝", "follows": "关注", "interaction": "点赞/收藏", "likes": "点赞"}
    changes = {}
    for key in sorted(set(previous) | set(current)):
        before, after = previous.get(key, ""), current.get(key, "")
        if before != after and (before != "" or after != ""):
            changes[key] = {"label": labels.get(key, key), "before": before, "after": after}
    return changes


def _avatar(profile: dict) -> str:
    value = profile.get("avatar") or ""
    return value if isinstance(value, str) and len(value) <= 200 else ""


def _state(subscription: SocialMediaSubscription) -> dict:
    data = subscription.last_profile_data or {}
    return data.get(STATE_KEY, {}) if isinstance(data, dict) else {}


def list_watches(user) -> list[SocialMediaSubscription]:
    return [
        item
        for item in SocialMediaSubscription.objects.filter(user=user, platform="xiaohongshu")
        if AGENT_MARKER in (item.subscription_types or [])
    ]


def serialize_watch(subscription: SocialMediaSubscription) -> dict:
    state = _state(subscription)
    history = state.get("history", [])
    latest = history[-1] if history else {}
    latest_update = state.get("latest_update") or None
    recent_notes = [
        _public_note(note) for note in (latest.get("notes") or [])[:6] if isinstance(note, dict) and note.get("id")
    ]
    trend = [{"date": item.get("date"), "profile_counts": item.get("profile_counts") or {}} for item in history[-14:]]
    if latest_update:
        freshest_notes = {
            note.get("id"): note
            for snapshot in reversed(history)
            for note in snapshot.get("notes") or []
            if isinstance(note, dict) and note.get("id")
        }
        latest_update = {
            **latest_update,
            "notes": [
                _public_note({**note, **freshest_notes.get(note.get("id"), {})})
                for note in latest_update.get("notes") or []
                if isinstance(note, dict)
            ],
        }
    return {
        "id": subscription.pk,
        "user_id": subscription.target_user_id,
        "nickname": subscription.target_user_name,
        "avatar": subscription.avatar_url or "",
        "profile_url": (
            f"https://www.xiaohongshu.com/user/profile/{subscription.target_user_id}"
            f"?xsec_token={quote(str(state.get('xsec_token') or ''), safe='')}&xsec_source=pc_user"
            if state.get("xsec_token")
            else f"https://www.xiaohongshu.com/user/profile/{subscription.target_user_id}"
        ),
        "status": subscription.status,
        "last_checked_at": latest.get("checked_at"),
        "last_visible_count": latest.get("visible_count"),
        "last_snapshot_date": latest.get("date"),
        "profile_counts": latest.get("profile_counts") or {},
        "recent_notes": recent_notes,
        "alert_email": state.get("alert_email", ""),
        "latest_update": latest_update,
        "trend": trend,
    }


def set_alert_email(user, watch_id: int, email: str) -> SocialMediaSubscription:
    if not isinstance(email, str) or len(email) > 254:
        raise profile_agent.XhsInputError("邮箱地址格式不正确")
    email = email.strip()
    if email:
        try:
            validate_email(email)
        except ValidationError as exc:
            raise profile_agent.XhsInputError("邮箱地址格式不正确") from exc
    with transaction.atomic():
        subscription = (
            SocialMediaSubscription.objects.select_for_update().filter(pk=watch_id, user=user, platform="xiaohongshu").first()
        )
        if not subscription or AGENT_MARKER not in (subscription.subscription_types or []):
            raise profile_agent.XhsInputError("找不到这个订阅")
        data = subscription.last_profile_data or {}
        state = data.get(STATE_KEY) or {}
        state["alert_email"] = email
        data[STATE_KEY] = state
        subscription.last_profile_data = data
        subscription.save(update_fields=["last_profile_data", "updated_at"])
    return subscription


def subscribe(user, user_id: str, xsec_token: str) -> tuple[SocialMediaSubscription, bool]:
    """Read a real profile first, then create a baseline without claiming updates."""
    profile = profile_agent.read_profile(user_id, xsec_token)
    today = timezone.localdate().isoformat()
    with transaction.atomic():
        subscription, created = SocialMediaSubscription.objects.select_for_update().get_or_create(
            user=user,
            platform="xiaohongshu",
            target_user_id=user_id,
            defaults={
                "target_user_name": profile["nickname"],
                "avatar_url": _avatar(profile),
                "subscription_types": [AGENT_MARKER],
                "last_profile_data": {STATE_KEY: {"xsec_token": xsec_token, "history": [_snapshot(profile, today)]}},
            },
        )
        if not created:
            types = list(subscription.subscription_types or [])
            if AGENT_MARKER not in types:
                types.append(AGENT_MARKER)
            data = subscription.last_profile_data or {}
            state = data.get(STATE_KEY) or {}
            state["xsec_token"] = xsec_token
            if not state.get("history"):
                state["history"] = [_snapshot(profile, today)]
            data[STATE_KEY] = state
            subscription.subscription_types = types
            subscription.last_profile_data = data
            subscription.target_user_name = profile["nickname"]
            subscription.avatar_url = _avatar(profile)
            subscription.status = "active"
            subscription.save()
    return subscription, created


def check_watch(subscription: SocialMediaSubscription) -> dict:
    """Check now, compare to yesterday when available, and persist today's snapshot."""
    if AGENT_MARKER not in (subscription.subscription_types or []):
        raise profile_agent.XhsInputError("这不是小红书主页 Agent 的订阅")
    state = _state(subscription)
    token = state.get("xsec_token") or ""
    if not token:
        raise profile_agent.XhsInputError("该订阅缺少访问令牌，请重新粘贴主页链接")
    profile = profile_agent.read_profile(subscription.target_user_id, token)

    today = timezone.localdate()
    yesterday = (today - timedelta(days=1)).isoformat()
    today_string = today.isoformat()
    current = _snapshot(profile, today_string)
    with transaction.atomic():
        locked = SocialMediaSubscription.objects.select_for_update().get(pk=subscription.pk)
        data = locked.last_profile_data or {}
        state = data.get(STATE_KEY) or {}
        history = [item for item in (state.get("history") or []) if isinstance(item, dict)]
        existing_today = next((item for item in reversed(history) if item.get("date") == today_string), None)
        existing_count = existing_today.get("visible_count") if existing_today else None
        current_count = current.get("visible_count")
        if existing_today and existing_count is not None and current_count is not None and existing_count > current_count:
            existing_ids = {note.get("id") for note in existing_today.get("notes") or []}
            current_ids = {note.get("id") for note in current.get("notes") or []}
            if current_ids and current_ids.issubset(existing_ids):
                current = existing_today
        earlier = [item for item in history if item.get("date", "") < today_string]
        baseline = next((item for item in reversed(earlier) if item.get("date") == yesterday), None)
        if baseline is None and earlier:
            baseline = earlier[-1]
        observed_ids = {note.get("id") for snapshot in earlier for note in snapshot.get("notes", [])}
        new_notes = [item.copy() for item in current["notes"] if baseline and item["id"] not in observed_ids]
        history = [item for item in history if item.get("date") != today_string]
        history.append(current)
        state.update({"xsec_token": token, "history": history[-14:]})
        data[STATE_KEY] = state
        locked.last_profile_data = data
        locked.target_user_name = profile["nickname"]
        locked.avatar_url = _avatar(profile)
        locked.save()

        for note in new_notes:
            if not SocialMediaNotification.objects.filter(
                subscription=locked, notification_type="newPosts", data__note_id=note["id"]
            ).exists():
                SocialMediaNotification.objects.create(
                    subscription=locked,
                    notification_type="newPosts",
                    title=f"{profile['nickname']} 发布了新笔记",
                    content=note["title"],
                    external_url=note["url"] if len(note["url"]) <= 200 else "",
                    data={"source": STATE_KEY, "note_id": note["id"], "snapshot_date": today_string, "url": note["url"]},
                )

    for note in new_notes[:3]:
        if not note.get("xsec_token"):
            continue
        try:
            note.update(profile_agent.read_note_detail(note["id"], note["xsec_token"]))
        except profile_agent.XhsServiceError:
            note["description"] = ""

    if baseline is None:
        comparison = "baseline"
        answer = f"已记录 {profile['nickname']} 的今天快照：读取到 {current['visible_count']} 篇可见笔记。还没有昨天的快照，暂时不能判断是否更新。"
    else:
        comparison = "yesterday" if baseline["date"] == yesterday else "earlier"
        reference = "昨天" if comparison == "yesterday" else f"上次记录（{baseline['date']}）"
        if new_notes:
            titles = "；".join(f"《{item['title']}》" for item in new_notes[:5])
            answer = f"{profile['nickname']} 与{reference}相比，在可见笔记中发现 {len(new_notes)} 篇新笔记：{titles}。"
        else:
            answer = f"{profile['nickname']} 与{reference}相比，在可见笔记中没有发现新笔记。"
        answer += f" {reference}读取 {baseline['visible_count']} 篇，本次读取 {current['visible_count']} 篇。"
    count_changes = (
        _count_changes(baseline.get("profile_counts") if baseline else None, current.get("profile_counts") or {})
        if baseline
        else {}
    )
    if count_changes:
        summary = "；".join(
            f"{item['label']} {item['before'] or '没有'}→{item['after'] or '没有'}" for item in count_changes.values()
        )
        answer += f" 账号数据变化：{summary}。"
    if current["is_truncated"]:
        answer += " 本次笔记列表超过读取上限，结果可能不完整。"
    public_new_notes = [_public_note(note) for note in new_notes]
    with transaction.atomic():
        locked = SocialMediaSubscription.objects.select_for_update().get(pk=subscription.pk)
        data = locked.last_profile_data or {}
        state = data.get(STATE_KEY) or {}
        state["last_result"] = {
            "answer": answer,
            "checked_at": timezone.now().isoformat(),
            "count_changes": count_changes,
        }
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
        "count_changes": count_changes,
        "watch": serialize_watch(locked),
    }


def _today_result(subscription: SocialMediaSubscription) -> dict | None:
    state = _state(subscription)
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
    yesterday = (timezone.localdate() - timedelta(days=1)).isoformat()
    if public_notes:
        reference = "昨天" if baseline and baseline.get("date") == yesterday else "上次记录"
        titles = "；".join(f"《{note.get('title') or '未命名笔记'}》" for note in public_notes[:5])
        answer = (
            f"{subscription.target_user_name} 与{reference}相比，发现 {len(public_notes)} 篇新笔记：{titles}。"
            " 这是今天已保存的检查结果。"
        )
    else:
        answer = str(last_result.get("answer") or "暂无检查结果") + " 这是今天已保存的检查结果。"
    count_changes = last_result.get("count_changes") or _count_changes(
        baseline.get("profile_counts") if baseline else None,
        current.get("profile_counts") or {},
    )
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
        "count_changes": count_changes,
        "cached": True,
        "watch": serialize_watch(subscription),
    }


def reply_to_message(user, message: str, *, refresh: bool = True) -> dict:
    """Channel-neutral query: web, WeChat and email adapters can call this."""
    message = (message or "").strip()
    if not message or len(message) > 300:
        raise profile_agent.XhsInputError("请输入不超过 300 字的查询消息")
    watches = [item for item in list_watches(user) if item.status == "active"]
    if not watches:
        return {"answer": "你还没有订阅博主。请先搜索并选择要关注的小红书用户。", "new_notes": []}
    matches = [item for item in watches if item.target_user_name in message or item.target_user_id in message]
    if len(matches) == 1:
        target = matches[0]
    elif len(matches) > 1:
        return {"answer": "找到多个匹配的订阅，请写出完整昵称。", "new_notes": []}
    elif len(watches) == 1:
        target = watches[0]
    else:
        names = "、".join(item.target_user_name for item in watches[:8])
        return {"answer": f"你订阅了多个博主，请在消息中写出要查的昵称：{names}。", "new_notes": []}
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
    return {
        "answer": f"{last_result.get('answer', '暂无检查结果')}\n检查时间：{last_result.get('checked_at', '未知')}",
        "new_notes": [],
    }
