"""Optional email and Enterprise WeChat delivery for newly observed notes."""

from __future__ import annotations

import json
import os
import hashlib
from html import escape
from email.mime.image import MIMEImage
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.db import transaction

from apps.tools.models import SocialMediaSubscription
from apps.tools.models.chat_models import ChatMessage, ChatNotification, ChatRoom
from apps.tools.services.xiaohongshu_watch_service import STATE_KEY as XHS_STATE_KEY
from apps.tools.services.creator_watch_service import STATE_KEY as CREATOR_STATE_KEY


class DeliveryError(RuntimeError):
    pass


def _message(result: dict) -> str:
    lines = [result["answer"]]
    notes = result.get("new_notes", [])
    if notes:
        lines.append(f"\n最近一次更新（{result.get('checked_date') or result.get('update_date') or '本次'}，共 {len(notes)} 篇）")
    for note in notes:
        lines.append(f"\n《{note.get('title') or '未命名笔记'}》")
        if note.get("description"):
            lines.append(note["description"][:300])
        if note.get("url"):
            lines.append(note["url"])
    return "\n".join(lines)


def _https_url(value: object) -> str:
    if not isinstance(value, str):
        return ""
    if value.startswith("http://"):
        return "https://" + value[7:]
    return value if value.startswith("https://") else ""


def _latest_update(subscription: SocialMediaSubscription) -> dict:
    state_key = XHS_STATE_KEY if subscription.platform == "xiaohongshu" else CREATOR_STATE_KEY
    data = subscription.last_profile_data or {}
    state = data.get(state_key) or {}
    latest = state.get("latest_update") or {}
    notes = []
    for note in latest.get("notes") or []:
        if not isinstance(note, dict) or not note.get("id"):
            continue
        notes.append(
            {
                **{key: note.get(key, "") for key in ("id", "title", "description", "likes")},
                "cover": _https_url(note.get("cover")),
                "url": _https_url(note.get("url")),
            }
        )
    return {
        "date": latest.get("date"),
        "count": latest.get("count", len(notes)),
        "notes": notes,
    }


def _download_cover(value: object) -> tuple[str, bytes] | None:
    url = _https_url(value)
    host = (urlparse(url).hostname or "").lower()
    if not url or not (host == "xhscdn.com" or host.endswith(".xhscdn.com")):
        return None
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.xiaohongshu.com/"},
            timeout=12,
        )
        response.raise_for_status()
    except requests.RequestException:
        return None
    content_type = (response.headers.get("Content-Type") or "").split(";", 1)[0].lower()
    if not content_type.startswith("image/") or not response.content or len(response.content) > 5 * 1024 * 1024:
        return None
    return content_type, response.content


def _email_html(subscription: SocialMediaSubscription, result: dict, cover_cids: dict[str, str] | None = None) -> str:
    cover_cids = cover_cids or {}
    notes = result.get("new_notes") or []
    cards = []
    for note in notes:
        title = escape(str(note.get("title") or "未命名笔记"))
        cover = _https_url(note.get("cover"))
        image_source = f"cid:{cover_cids[cover]}" if cover in cover_cids else cover
        url = _https_url(note.get("url"))
        badge = '<span style="color:#247047;font-weight:700">新增</span><br>'
        image = (
            f'<img src="{escape(image_source, quote=True)}" alt="{title}" '
            'style="display:block;width:100%;max-width:240px;height:180px;object-fit:cover;border-radius:10px">'
            if cover
            else ""
        )
        content = f'{badge}{image}<strong style="display:block;margin-top:8px">{title}</strong>'
        if url:
            content = f'<a href="{escape(url, quote=True)}" style="color:#292321;text-decoration:none">{content}</a>'
        cards.append(
            '<td style="width:250px;vertical-align:top;padding:8px;border:1px solid #eee5e2;border-radius:12px">'
            + content
            + "</td>"
        )
    rows = "".join(f"<tr>{''.join(cards[index:index + 2])}</tr>" for index in range(0, len(cards), 2))
    answer = escape(str(result.get("answer") or "这是 Model Shift 博主更新提醒的邮件预览。"))
    date = escape(str(result.get("checked_date") or result.get("update_date") or "尚无日期"))
    return (
        '<div style="font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;color:#292321">'
        f'<h2 style="color:#cf2634">{escape(subscription.target_user_name)} · 最近更新</h2>'
        f"<p>{answer}</p><p>更新日期：{date} · 新增：{len(notes)} 篇</p>"
        f'<table role="presentation" cellspacing="10" style="border-collapse:separate">{rows}</table>'
        '<p style="color:#756c69">图片、标题和链接来自平台检测到的最近一次更新；邮件客户端可能需要允许显示外部图片。</p>'
        "</div>"
    )


def send_snapshot_email(
    subscription: SocialMediaSubscription,
    recipient: str,
    *,
    result: dict | None = None,
    subject: str | None = None,
) -> int:
    from apps.tools.services.creator_email_policy import reserve_send

    reserve_send(subscription.user_id)
    result = dict(result or {})
    latest_update = _latest_update(subscription)
    state_key = XHS_STATE_KEY if subscription.platform == "xiaohongshu" else CREATOR_STATE_KEY
    stored_state = (subscription.last_profile_data or {}).get(state_key) or {}
    stored_result = stored_state.get("last_result") or {}
    result.setdefault("new_notes", latest_update["notes"])
    result.setdefault("update_date", latest_update["date"])
    result.setdefault("answer", stored_result.get("answer") or "这是 Model Shift 最近一次博主更新的邮件预览。")
    result.setdefault("count_changes", stored_result.get("count_changes") or {})
    email = EmailMultiAlternatives(
        subject or f"博主更新：{subscription.target_user_name}",
        _message(result),
        settings.DEFAULT_FROM_EMAIL,
        [recipient],
    )
    cover_cids = {}
    inline_images = []
    for note in result["new_notes"]:
        cover = _https_url(note.get("cover"))
        if not cover or cover in cover_cids:
            continue
        downloaded = _download_cover(cover)
        if downloaded is None:
            continue
        content_type, content = downloaded
        cid = f"creator-{hashlib.sha256(cover.encode()).hexdigest()[:20]}"
        image = MIMEImage(content, _subtype=content_type.split("/", 1)[1])
        image.add_header("Content-ID", f"<{cid}>")
        image.add_header("Content-Disposition", "inline", filename=f"{cid}.{content_type.split('/', 1)[1]}")
        cover_cids[cover] = cid
        inline_images.append(image)
    email.attach_alternative(_email_html(subscription, result, cover_cids), "text/html")
    email.mixed_subtype = "related"
    for image in inline_images:
        email.attach(image)
    return email.send(fail_silently=False)


def send_digest_email(user_id: int, recipient: str, updates: list[tuple[SocialMediaSubscription, dict]]) -> int:
    """Send one consolidated daily email for all creators checked in a run."""
    from apps.tools.services.creator_email_policy import reserve_send
    if not updates:
        return 0
    reserve_send(user_id)
    sections = []
    cover_cids = {}
    inline_images = []
    for subscription, result in updates:
        notes = result.get("new_notes") or []
        changes = result.get("count_changes") or {}
        lines = [f"<h3 style='margin-bottom:6px'>{escape(subscription.target_user_name)}</h3>"]
        if changes:
            labels = [f"{escape(str(v.get('label', k)))}：{escape(str(v.get('before') or '没有'))} → {escape(str(v.get('after') or '没有'))}" for k, v in changes.items()]
            lines.append("<p>" + "；".join(labels) + "</p>")
        if notes:
            lines.append(f"<p><strong>更新内容：{len(notes)} 篇</strong></p><ul>")
            for note in notes[:3]:
                title = escape(str(note.get("title") or "未命名笔记"))
                url = _https_url(note.get("url"))
                cover = _https_url(note.get("cover"))
                if cover and cover not in cover_cids:
                    downloaded = _download_cover(cover)
                    if downloaded:
                        content_type, content = downloaded
                        cid = f"digest-{hashlib.sha256(cover.encode()).hexdigest()[:20]}"
                        image = MIMEImage(content, _subtype=content_type.split("/", 1)[1])
                        image.add_header("Content-ID", f"<{cid}>")
                        image.add_header("Content-Disposition", "inline", filename=f"{cid}.{content_type.split('/', 1)[1]}")
                        inline_images.append(image)
                        cover_cids[cover] = cid
                image_src = f"cid:{cover_cids[cover]}" if cover in cover_cids else cover
                image = f"<img src='{escape(image_src, quote=True)}' alt='{title}' style='width:180px;height:120px;object-fit:cover;border-radius:8px;display:block;margin:6px 0'>" if image_src else ""
                link = f"<a href='{escape(url, quote=True)}'>{title}</a>" if url else title
                lines.append(f"<li>{image}{link}</li>")
            lines.append("</ul>")
        if not changes and not notes:
            lines.append("<p>本次没有检测到粉丝、关注或内容更新。</p>")
        sections.append("<section style='padding:10px 0;border-bottom:1px solid #eee5e2'>" + "".join(lines) + "</section>")
    html = "<div style='font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;color:#292321'><h2 style='color:#cf2634'>Peep 关注更新日报</h2>" + "".join(sections) + "<p style='color:#756c69'>同一轮检查的所有关注对象合并为一封邮件。</p></div>"
    text_parts = ["Peep 关注更新日报"]
    for subscription, result in updates:
        text_parts.append(subscription.target_user_name)
        text_parts.append(result.get("answer") or "")
        for note in (result.get("new_notes") or [])[:3]:
            text_parts.append(f"更新内容：{note.get('title', '未命名笔记')} {note.get('url', '')}")
    email = EmailMultiAlternatives("Peep 关注更新日报", "\n".join(text_parts), settings.DEFAULT_FROM_EMAIL, [recipient])
    email.attach_alternative(html, "text/html")
    email.mixed_subtype = "related"
    for image in inline_images:
        email.attach(image)
    return email.send(fail_silently=False)


def _wecom_recipient(subscription: SocialMediaSubscription) -> str:
    try:
        mapping = json.loads(os.environ.get("XHS_WECOM_USER_MAP", "{}"))
    except ValueError as exc:
        raise DeliveryError("企业微信用户映射配置不是有效 JSON") from exc
    recipient = mapping.get(str(subscription.user_id), "") if isinstance(mapping, dict) else ""
    return recipient if isinstance(recipient, str) else ""


def _wecom_send(recipient: str, message: str) -> None:
    corp_id = os.environ.get("XHS_WECOM_CORP_ID", "")
    secret = os.environ.get("XHS_WECOM_APP_SECRET", "")
    agent_id = os.environ.get("XHS_WECOM_AGENT_ID", "")
    if not all((corp_id, secret, agent_id)):
        raise DeliveryError("企业微信应用凭据未配置")
    token_key = f"xhs-agent:wecom-token:{corp_id}"
    token = cache.get(token_key)
    try:
        if not token:
            response = requests.get(
                "https://qyapi.weixin.qq.com/cgi-bin/gettoken",
                params={
                    "corpid": corp_id,
                    "corpsecret": secret,
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            if data.get("errcode") != 0 or not data.get("access_token"):
                raise DeliveryError("企业微信 access_token 获取失败")
            token = data["access_token"]
            cache.set(token_key, token, timeout=max(60, int(data.get("expires_in", 7200)) - 300))
        response = requests.post(
            "https://qyapi.weixin.qq.com/cgi-bin/message/send",
            params={
                "access_token": token,
            },
            json={
                "touser": recipient,
                "msgtype": "text",
                "agentid": int(agent_id),
                "text": {"content": message[:1900]},
                "safe": 0,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        if data.get("errcode") != 0 or data.get("invaliduser") or data.get("unlicenseduser"):
            raise DeliveryError("企业微信消息发送失败，请检查用户和应用可见范围")
    except (requests.RequestException, ValueError) as exc:
        raise DeliveryError("企业微信接口连接失败") from exc


def _system_send(subscription: SocialMediaSubscription, notes: list[dict]) -> None:
    """Add creator updates to the existing site-wide unread notification bell."""
    room, _ = ChatRoom.objects.get_or_create(
        room_id=f"creator-watch-{subscription.user_id}",
        defaults={
            "name": "博主更新提醒",
            "description": "关注的博主有新内容",
            "room_type": "system",
            "user1": subscription.user,
        },
    )
    updates = [
        {
            "id": note["id"],
            "title": (note.get("title") or "新内容")[:100],
            "cover": (
                f"/tools/api/xiaohongshu-agent/watches/{subscription.pk}/covers/{note['id']}/"
                if subscription.platform == "xiaohongshu" and note.get("cover")
                else _https_url(note.get("cover"))
            ),
            "url": _https_url(note.get("url")),
        }
        for note in notes
    ]
    titles = "、".join(f"《{entry['title']}》" for entry in updates[:5])
    if len(updates) > 5:
        titles += f"等 {len(updates)} 篇"
    message = ChatMessage.objects.create(
        room=room,
        sender=subscription.user,
        message_type="system",
        content=f"{subscription.target_user_name} 更新了 {len(updates)} 篇：{titles}",
        metadata={
            "jump_url": "/tools/peep/#xhs-watches-panel",
            "source": "creator_watch",
            "note_ids": [entry["id"] for entry in updates],
            "cover": updates[0]["cover"] if updates else "",
            "updates": updates,
        },
    )
    ChatNotification.objects.create(user=subscription.user, room=room, message=message)


def deliver_updates(subscription: SocialMediaSubscription, result: dict) -> dict:
    """Send only unsent note IDs for each configured channel; mark after success."""
    notes = [note for note in result.get("new_notes", []) if note.get("id")]
    if not notes:
        return {}
    state_key = XHS_STATE_KEY if subscription.platform == "xiaohongshu" else CREATOR_STATE_KEY
    status = {}
    try:
        wecom_recipient = _wecom_recipient(subscription)
    except DeliveryError as exc:
        wecom_recipient = ""
        status["wecom"] = f"失败：{exc}"
    channels = ("system", "wecom") if result.get("skip_email") else ("system", "email", "wecom")
    for channel in channels:
        try:
            with transaction.atomic():
                locked = SocialMediaSubscription.objects.select_for_update().get(pk=subscription.pk)
                data = locked.last_profile_data or {}
                latest_state = data.get(state_key) or {}
                from apps.tools.services.creator_email_policy import get_email

                recipient = get_email(subscription.user_id) if channel == "email" else wecom_recipient
                if channel != "system" and not recipient:
                    continue
                all_sent = latest_state.get("sent_note_ids") or {}
                sent_ids = set(all_sent.get(channel) or [])
                pending = [note for note in notes if note["id"] not in sent_ids]
                if not pending:
                    continue
                message = _message({**result, "new_notes": pending})
                if channel == "system":
                    _system_send(locked, pending)
                elif channel == "email":
                    if settings.EMAIL_BACKEND == "django.core.mail.backends.console.EmailBackend":
                        raise DeliveryError("当前环境是控制台邮件后端，请配置 SMTP 后再发送")
                    delivered = send_snapshot_email(locked, recipient, result={**result, "new_notes": pending})
                    if delivered != 1:
                        raise DeliveryError("邮件服务没有确认投递，请检查 SMTP 配置")
                else:
                    _wecom_send(recipient, message)
                all_sent[channel] = list(dict.fromkeys([*all_sent.get(channel, []), *[note["id"] for note in pending]]))[-200:]
                latest_state["sent_note_ids"] = all_sent
                locked.refresh_from_db(fields=["last_profile_data"])
                data = locked.last_profile_data or {}
                data[state_key] = latest_state
                locked.last_profile_data = data
                locked.save(update_fields=["last_profile_data", "updated_at"])
        except Exception as exc:
            status[channel] = f"失败：{exc}"
            continue
        status[channel] = f"已发送 {len(pending)} 篇"
    return status
