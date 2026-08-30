"""Authenticated requirement RAG page and APIs."""

from __future__ import annotations

import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from apps.tools.services.llm_service import DeepSeekService
from apps.tools.services.rag_service import (
    RagInputError,
    build_testcase_prompt,
    ingest_document,
    search_chunks,
    sync_site_capabilities,
)


def _api_login_required(view):
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "请先登录后使用需求知识库"}, status=401)
        return view(request, *args, **kwargs)

    return wrapped


@login_required
@require_GET
def requirement_rag_page(request):
    # Keep the shared system knowledge document current without requiring a
    # manual bootstrap action after every deployment or feature update.
    sync_site_capabilities()
    return render(request, "tools/rag_testcase_generator.html")


@require_POST
@_api_login_required
def rag_upload_api(request):
    upload = request.FILES.get("file")
    if not upload:
        return JsonResponse({"error": "请选择需求文档"}, status=400)
    try:
        document = ingest_document(request.user, upload)
    except RagInputError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    return JsonResponse(
        {"id": document.id, "title": document.title, "chunks": document.chunks.count(), "message": "文档已完成分块并写入 RAG 知识库"},
        status=201,
    )


@require_POST
@_api_login_required
def rag_sync_site_capabilities_api(request):
    document = sync_site_capabilities()
    return JsonResponse(
        {"id": document.id, "title": document.title, "chunks": document.chunks.count(), "message": "本站能力已同步到共享 RAG 知识库"}
    )


@require_GET
@_api_login_required
def rag_search_api(request):
    try:
        sync_site_capabilities()
        results = search_chunks(request.user, request.GET.get("q", ""), int(request.GET.get("limit", 5)))
    except (RagInputError, ValueError) as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    return JsonResponse({"results": results})


@require_POST
@_api_login_required
def rag_generate_api(request):
    payload = json.loads(request.body or "{}")
    request_text = str(payload.get("request", "")).strip()
    try:
        sync_site_capabilities()
        sources = search_chunks(request.user, request_text, int(payload.get("limit", 5)))
    except (RagInputError, ValueError) as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    if not sources:
        return JsonResponse({"error": "知识库中没有匹配片段，请先上传更相关的需求文档"}, status=404)
    if not settings.DEEPSEEK_API_KEY:
        return JsonResponse({"error": "未配置 DEEPSEEK_API_KEY；已返回检索来源，可配置后生成测试用例", "sources": sources}, status=503)
    try:
        answer = DeepSeekService().generate_content(
            build_testcase_prompt(request_text, sources), temperature=0.2, max_tokens=4000
        )
    except Exception as exc:
        return JsonResponse({"error": f"DeepSeek 生成失败：{exc}", "sources": sources}, status=502)
    return JsonResponse({"test_cases": answer, "sources": sources})
