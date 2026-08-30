"""Deterministic RAG ingestion and retrieval for requirement-driven testing."""

from __future__ import annotations

import hashlib
import math
import re
from pathlib import Path
from typing import Iterable

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from apps.tools.models.rag_models import RequirementChunk, RequirementDocument


VECTOR_DIMENSIONS = 256
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120
SUPPORTED_SUFFIXES = {".md", ".markdown", ".txt", ".pdf", ".docx"}


class RagInputError(ValueError):
    """A user-facing ingestion or search validation error."""


def _tokens(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]", text.lower())
    return words or list(text.lower())


def embed(text: str) -> list[float]:
    """Create a stable, local feature-hashing vector without an API dependency."""
    vector = [0.0] * VECTOR_DIMENSIONS
    for token in _tokens(text):
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=4).digest()
        index = int.from_bytes(digest, "big") % VECTOR_DIMENSIONS
        vector[index] += 1.0
    magnitude = math.sqrt(sum(value * value for value in vector))
    return [value / magnitude for value in vector] if magnitude else vector


def cosine_similarity(first: list[float], second: list[float]) -> float:
    return sum(a * b for a, b in zip(first, second))


def chunk_text(text: str) -> Iterable[str]:
    cleaned = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not cleaned:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(len(cleaned), start + CHUNK_SIZE)
        if end < len(cleaned):
            boundary = max(cleaned.rfind("\n", start, end), cleaned.rfind("。", start, end), cleaned.rfind(".", start, end))
            if boundary > start + CHUNK_SIZE // 2:
                end = boundary + 1
        chunks.append(cleaned[start:end].strip())
        if end == len(cleaned):
            break
        start = max(end - CHUNK_OVERLAP, start + 1)
    return [chunk for chunk in chunks if chunk]


def extract_text(upload: UploadedFile) -> tuple[str, str]:
    suffix = Path(upload.name).suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise RagInputError("仅支持 PDF、Word（.docx）、Markdown 和 TXT 文件")

    raw = upload.read()
    upload.seek(0)
    if suffix in {".md", ".markdown", ".txt"}:
        return raw.decode("utf-8-sig", errors="replace"), suffix.lstrip(".")
    if suffix == ".docx":
        from docx import Document

        document = Document(upload)
        return "\n".join(paragraph.text for paragraph in document.paragraphs), "docx"
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RagInputError("PDF 解析组件未安装，请安装 requirements.txt 后重试") from exc
    reader = PdfReader(upload)
    return "\n".join(page.extract_text() or "" for page in reader.pages), "pdf"


@transaction.atomic
def ingest_document(owner, upload: UploadedFile) -> RequirementDocument:
    text, source_type = extract_text(upload)
    pieces = list(chunk_text(text))
    if not pieces:
        raise RagInputError("文档未提取到可索引文本；扫描版 PDF 请先进行 OCR")
    document = RequirementDocument.objects.create(
        owner=owner,
        title=Path(upload.name).name,
        source_file=upload,
        source_type=source_type,
        extracted_text=text,
    )
    RequirementChunk.objects.bulk_create(
        [RequirementChunk(document=document, sequence=index + 1, content=piece, vector=embed(piece)) for index, piece in enumerate(pieces)]
    )
    return document


def search_chunks(owner, query: str, limit: int = 5) -> list[dict]:
    if not query.strip():
        raise RagInputError("请输入搜索问题或测试生成请求")
    query_vector = embed(query)
    candidates = RequirementChunk.objects.filter(document__owner=owner).select_related("document")
    ranked = sorted(
        ((cosine_similarity(query_vector, chunk.vector), chunk) for chunk in candidates),
        key=lambda item: item[0],
        reverse=True,
    )[: max(1, min(limit, 10))]
    return [
        {
            "document_id": chunk.document_id,
            "document": chunk.document.title,
            "chunk_id": chunk.id,
            "sequence": chunk.sequence,
            "content": chunk.content,
            "score": round(score, 4),
        }
        for score, chunk in ranked
        if score > 0
    ]


def build_testcase_prompt(request_text: str, sources: list[dict]) -> str:
    context = "\n\n".join(
        f"[来源: {source['document']}#分块{source['sequence']}; 相似度 {source['score']}]\n{source['content']}"
        for source in sources
    )
    return f"""你是资深测试开发工程师。仅依据给出的需求上下文生成可执行测试用例。
用户请求：{request_text}

需求上下文：
{context}

输出 Markdown，并按模块列出：用例标题、前置条件、步骤、预期结果、优先级、测试类型。
每条用例末尾必须标注使用的来源，例如：来源：[文档名#分块1]。不确定的信息要明确写为待确认，不得编造。"""
