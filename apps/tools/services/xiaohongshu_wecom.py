"""Enterprise WeChat callback encryption and user mapping for cached replies."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import struct
import time
import xml.etree.ElementTree as ET

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from django.contrib.auth import get_user_model

from apps.tools.services.creator_watch_service import reply_to_message
from apps.tools.services.xiaohongshu_profile_agent import XhsInputError


class WeComError(ValueError):
    pass


def _config() -> tuple[str, bytes, str]:
    token = os.environ.get("XHS_WECOM_CALLBACK_TOKEN", "")
    key_text = os.environ.get("XHS_WECOM_ENCODING_AES_KEY", "")
    corp_id = os.environ.get("XHS_WECOM_CORP_ID", "")
    if not token or len(key_text) != 43 or not corp_id:
        raise WeComError("企业微信回调尚未配置")
    try:
        key = base64.b64decode(key_text + "=", validate=True)
    except ValueError as exc:
        raise WeComError("企业微信回调密钥不正确") from exc
    if len(key) != 32:
        raise WeComError("企业微信回调密钥不正确")
    return token, key, corp_id


def _signature(token: str, timestamp: str, nonce: str, encrypted: str) -> str:
    return hashlib.sha1("".join(sorted((token, timestamp, nonce, encrypted))).encode()).hexdigest()


def _verify(token: str, timestamp: str, nonce: str, encrypted: str, signature: str) -> None:
    if not hmac.compare_digest(_signature(token, timestamp, nonce, encrypted), signature or ""):
        raise WeComError("企业微信签名验证失败")


def _decrypt(key: bytes, encrypted: str, corp_id: str) -> str:
    try:
        cipher = Cipher(algorithms.AES(key), modes.CBC(key[:16]))
        decryptor = cipher.decryptor()
        ciphertext = base64.b64decode(encrypted, validate=True)
        plain = decryptor.update(ciphertext) + decryptor.finalize()
        padding = plain[-1]
        if padding < 1 or padding > 32 or plain[-padding:] != bytes([padding]) * padding:
            raise WeComError("企业微信消息填充不正确")
        plain = plain[:-padding]
        length = struct.unpack(">I", plain[16:20])[0]
        if len(plain) < 20 + length or plain[20 + length :].decode() != corp_id:
            raise WeComError("企业微信企业 ID 不匹配")
        return plain[20 : 20 + length].decode()
    except (ValueError, IndexError, UnicodeDecodeError, struct.error) as exc:
        raise WeComError("企业微信消息无法解密") from exc


def _encrypt(key: bytes, value: str, corp_id: str) -> str:
    content = value.encode()
    plain = secrets.token_bytes(16) + struct.pack(">I", len(content)) + content + corp_id.encode()
    padding = 32 - len(plain) % 32
    plain += bytes([padding]) * padding
    cipher = Cipher(algorithms.AES(key), modes.CBC(key[:16]))
    encryptor = cipher.encryptor()
    return base64.b64encode(encryptor.update(plain) + encryptor.finalize()).decode()


def verify_url(query) -> str:
    token, key, corp_id = _config()
    timestamp, nonce, encrypted = query.get("timestamp", ""), query.get("nonce", ""), query.get("echostr", "")
    _verify(token, timestamp, nonce, encrypted, query.get("msg_signature", ""))
    return _decrypt(key, encrypted, corp_id)


def _user_for_wecom_id(wecom_id: str):
    try:
        mapping = json.loads(os.environ.get("XHS_WECOM_USER_MAP", "{}"))
    except ValueError as exc:
        raise WeComError("企业微信用户映射配置不正确") from exc
    if not isinstance(mapping, dict):
        raise WeComError("企业微信用户映射配置不正确")
    model_ids = [key for key, value in mapping.items() if value == wecom_id]
    if len(model_ids) != 1:
        return None
    return get_user_model().objects.filter(pk=model_ids[0]).first()


def handle_message(query, body: bytes) -> str:
    token, key, corp_id = _config()
    try:
        envelope = ET.fromstring(body)
        encrypted = envelope.findtext("Encrypt") or ""
        timestamp, nonce = query.get("timestamp", ""), query.get("nonce", "")
        _verify(token, timestamp, nonce, encrypted, query.get("msg_signature", ""))
        message = ET.fromstring(_decrypt(key, encrypted, corp_id))
    except ET.ParseError as exc:
        raise WeComError("企业微信 XML 格式不正确") from exc
    sender = message.findtext("FromUserName") or ""
    receiver = message.findtext("ToUserName") or ""
    if message.findtext("MsgType") != "text" or not sender or not receiver:
        answer = "请发送文字，例如：某某今天更新了吗？"
    else:
        user = _user_for_wecom_id(sender)
        if user:
            try:
                answer = reply_to_message(user, message.findtext("Content") or "", refresh=False)["answer"]
            except XhsInputError as exc:
                answer = str(exc)
        else:
            answer = "该企业微信账号尚未绑定 Model Shift 用户。"
    response = ET.Element("xml")
    for tag, value in (
        ("ToUserName", sender),
        ("FromUserName", receiver),
        ("CreateTime", str(int(time.time()))),
        ("MsgType", "text"),
        ("Content", answer[:1800]),
    ):
        ET.SubElement(response, tag).text = value
    encrypted_response = _encrypt(key, ET.tostring(response, encoding="unicode"), corp_id)
    response_timestamp = str(int(time.time()))
    response_nonce = secrets.token_hex(8)
    result = ET.Element("xml")
    for tag, value in (
        ("Encrypt", encrypted_response),
        ("MsgSignature", _signature(token, response_timestamp, response_nonce, encrypted_response)),
        ("TimeStamp", response_timestamp),
        ("Nonce", response_nonce),
    ):
        ET.SubElement(result, tag).text = value
    return ET.tostring(result, encoding="unicode")
