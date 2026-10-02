"""Deterministic RAG ingestion and retrieval for requirement-driven testing."""

from __future__ import annotations

import hashlib
import math
import re
from pathlib import Path
from typing import Iterable

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.db.models import Q

from apps.tools.models import Feature
from apps.tools.models.rag_models import RequirementChunk, RequirementDocument
from apps.tools.services.site_capability_catalog import build_site_capability_cards


VECTOR_DIMENSIONS = 256
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120
SUPPORTED_SUFFIXES = {".md", ".markdown", ".txt", ".pdf", ".docx"}
SITE_CAPABILITIES_TITLE = "QAToolBox 当前网站能力（系统知识库）"
PRODUCT_GUIDE_TITLE = "ModeShift 产品功能说明书.md"
LEGACY_SYSTEM_TITLES = {SITE_CAPABILITIES_TITLE, PRODUCT_GUIDE_TITLE}
AUTO_CATALOG_SOURCE_TYPE = "catalog"
AUTO_CATALOG_MARKER = "证据目录版本：site-capability-v1"

# Keep the shared knowledge base aligned with the product's visible page
# structure.  One item becomes one searchable card/document; do not merge
# these into a single site-wide document because that makes retrieval too
# broad for test-case generation.
MODE_KNOWLEDGE_MODULES = [
    {
        "mode": "极客模式",
        "page": "测试用例生成器 / 生成入口",
        "route": "/tools/test_case_generator/",
        "content": "测试用例生成入口。用户填写产品需求和可选的补充 Prompt，搜索并选择知识库功能文档，选择当前可用的 DeepSeek 或本地 Ollama 模型，然后创建异步测试用例生成任务。补充 Prompt 是用户输入原文，可为空；系统默认规则不会覆盖用户输入。",
    },
    {
        "mode": "极客模式",
        "page": "测试用例生成器 / 知识库搜索",
        "route": "/tools/api/rag/documents/search/",
        "content": "测试用例生成器的知识库按模式、页面和功能模块拆分为独立文档卡片。用户搜索功能名或模块名后看到标题、来源、摘要和匹配度；点击卡片可查看全文详情，点击添加后只把文档 ID 作为生成上下文提交。共享文档和当前用户自己的文档可用，其他用户私有文档不可见。",
    },
    {
        "mode": "极客模式",
        "page": "测试用例生成器 / 人工执行用例",
        "route": "/tools/test_case_generator/manual/",
        "content": "人工执行用例工作区，用于查看、编辑和导出 DeepSeek 生成的 PMD/人工测试用例 Markdown。该页面只处理人工文档，不把人工用例直接交给 API 或 UI 执行 Agent。",
    },
    {
        "mode": "极客模式",
        "page": "测试用例生成器 / API 自动化",
        "route": "/tools/test_case_generator/api/",
        "content": "API 自动化工作区。DeepSeek 根据需求和已选功能文档单独生成 API 自动化 Markdown，要求包含 HTTP 方法、同源 path、headers/query/body 和状态码或 JSON 断言。执行 Agent 只接收 API 文档；默认只允许本机或 Docker 内部目标，写操作需要用户主动授权。",
    },
    {
        "mode": "极客模式",
        "page": "测试用例生成器 / UI 自动化",
        "route": "/tools/test_case_generator/ui/",
        "content": "UI 自动化工作区。DeepSeek 根据需求和已选功能文档单独生成 UI 自动化 Markdown，要求包含 open、fill、click、expect_text 或 expect_visible 等页面动作与断言。执行 Agent 只接收 UI 文档，无法确认定位器的用例必须转人工。",
    },
    {
        "mode": "极客模式",
        "page": "测试用例生成器 / 执行报告",
        "route": "/tools/test_case_generator/reports/",
        "content": "自动化执行报告工作区。报告按 API/UI 通道独立保存，展示执行状态、模型、总数、通过、失败、跳过、每条用例步骤、输入、响应或页面断言和失败原因。",
    },
    {
        "mode": "极客模式",
        "page": "PDF 转换器",
        "route": "/tools/pdf_converter/",
        "content": "PDF 转换器页面，提供 PDF 与 Word 等文档转换能力。实际可用格式和解析能力取决于部署环境的 PDF/Word 依赖。",
    },
    {
        "mode": "极客模式",
        "page": "3D 简历生成器",
        "route": "/tools/resume-3d-generator/",
        "content": "3D 简历生成器页面，用户上传或填写简历内容后生成可浏览的 3D 履历展示。",
    },
    {
        "mode": "极客模式",
        "page": "网页爬虫",
        "route": "/tools/web_crawler/",
        "content": "网页爬虫页面，用于配置目标网页并采集网页数据。执行效果依赖网络、目标站点和部署环境的浏览器或请求依赖。",
    },
    {
        "mode": "极客模式",
        "page": "ZIP 文件处理",
        "route": "/tools/zip-tool/",
        "content": "ZIP 文件处理页面，支持多文件打包和单文件压缩等文件处理操作。",
    },
    {
        "mode": "生活模式",
        "page": "生活日记",
        "route": "/tools/simple-diary/",
        "content": "生活日记页面，支持快速保存、心情保存、图片上传、模板、日历、历史、周报和成就等记录能力。",
    },
    {
        "mode": "生活模式",
        "page": "FitMatrix 健身",
        "route": "/tools/fitness/",
        "content": "FitMatrix 健身页面，提供健身资料、体重记录、训练计划、动作工具、训练记录和身体分析等能力。",
    },
    {
        "mode": "生活模式",
        "page": "冥想指南",
        "route": "/tools/meditation_guide/",
        "content": "冥想指南页面，提供引导式冥想内容，帮助用户进行放松和专注练习。",
    },
    {
        "mode": "生活模式",
        "page": "音乐疗愈",
        "route": "/tools/music_healing/",
        "content": "音乐疗愈页面，提供音乐播放和疗愈主题内容。实际曲目和播放能力取决于页面数据及媒体资源。",
    },
    {
        "mode": "生活模式",
        "page": "美食选择器 / 页面与筛选器",
        "route": "/tools/food_randomizer/",
        "content": "真实页面标题为“🍽️ 中午吃什么”，浏览器页面标题为“我其实一直有三个问题 - 美食选择器”。页面包含早餐、午餐、晚餐、夜宵单选项，准确 ID 是 #breakfast、#lunch、#dinner、#snack；心情准确 ID 是 #mood_happy、#mood_excited、#mood_calm、#mood_sad、#mood_angry、#mood_neutral；菜系准确 ID 是 #mixed、#chinese、#western、#japanese、#korean、#thai；价格准确 ID 是 #price_low、#price_medium、#price_high；限制准确 ID 是 #no_spicy、#vegetarian、#no_seafood、#no_pork、#low_sugar、#low_salt。主按钮为 #startButton（按条件随机）和 #pureRandomButton（纯随机），结果区域为 #resultContainer，图片 #foodImage，名称 #foodName，描述 #foodDescription，营养区 #nutritionInfo。营养区实际由脚本生成“卡路里/千卡、蛋白质/克、脂肪/克、碳水化合物/克、膳食纤维/克”等卡片，不要臆造“热量”文本断言。备选区 #alternativeGrid。页面依赖 32 条 FoodItem 本地数据。UI 自动化只允许使用 open/click/fill/expect_text/expect_visible/screenshot，不要输出 wait 动作。",
    },
    {
        "mode": "生活模式",
        "page": "美食选择器 / 纯随机接口",
        "route": "/tools/api/food-randomizer/pure-random/",
        "content": "真实接口 POST /tools/api/food-randomizer/pure-random/，JSON 字段为 cuisine_type（all/mixed 或具体菜系）、meal_type（all/breakfast/lunch/dinner/snack）、exclude_recent（布尔值）。视图使用 csrf_exempt，不应生成“缺少 csrftoken 必须 403”的断言；Content-Type: application/json 是请求格式要求。success=true 时返回 recommendation.food、recommendation.alternatives、recommendation.generated_at、recommendation.session_id；food 包含 id/name/cuisine/meal_type/calories/ingredients/description/image_url/difficulty/cooking_time/health_score/nutrition/tags。接口从 29 条 FoodItem 本地库筛选后随机返回，并为已登录用户写入 FoodRandomizationSession/FoodHistory，因此这是带副作用的真实写操作，不是安全 POST；匿名调用成功时 session_id 为 null。无匹配食物返回 404，JSON success=false。",
    },
    {
        "mode": "生活模式",
        "page": "美食选择器 / 结果与历史",
        "route": "/tools/api/food-randomizer/history/",
        "content": "结果卡片展示名称、描述、图片、食材、热量、蛋白质、脂肪、碳水、膳食纤维、标签和备选食物。GET /tools/api/food-randomizer/history/?limit=20&offset=0 返回 {success:true, history:[...], pagination:{total,limit,offset,has_more}}；history 每项真实字段为 id、food_name、cuisine、meal_type、calories、health_score、rating、selected、created_at、session_id、image_url、nutrition_summary（calories/protein/fat/carbohydrates/fiber/sodium）。匿名用户 history 为空且 pagination.total 为 0。该接口是只读 GET。",
    },
    {
        "mode": "生活模式",
        "page": "美食选择器 / 评分写入",
        "route": "/tools/api/food-randomizer/rate/",
        "content": "评分接口 POST /tools/api/food-randomizer/rate/，登录后提交 session_id、rating（1-5）和 feedback，更新当前用户 FoodHistory.rating/feedback 并重新计算 FoodItem.popularity_score。该接口是真正写操作，自动化执行必须显式允许写操作；错误输入返回 400，找不到当前用户历史返回 404。",
    },
    {
        "mode": "生活模式",
        "page": "美食选择器 / 统计接口",
        "route": "/tools/api/food-randomizer/statistics/",
        "content": "统计接口 GET /tools/api/food-randomizer/statistics/，只读返回 {success:true, stats:{total_foods,total_recommendations,most_popular_food,cuisine_distribution,meal_type_distribution,weekly_usage,user_stats,health_metrics}}。stats.total_foods 对应本地 FoodItem 数量；user_stats 在登录时包含 total_recommendations、favorite_cuisine、healthy_choices；匿名用户 user_stats 为空。该接口不写数据库。",
    },
    {
        "mode": "狂暴模式",
        "page": "自我分析",
        "route": "/tools/self_analysis/",
        "content": "自我分析页面，围绕用户问题提供心理、社会、发展和行动建议等分析维度。",
    },
    {
        "mode": "狂暴模式",
        "page": "故事板",
        "route": "/tools/storyboard/",
        "content": "故事板页面，根据用户描述生成治愈系故事内容和故事结构。",
    },
    {
        "mode": "狂暴模式",
        "page": "命运分析",
        "route": "/tools/fortune_analyzer/",
        "content": "命运分析页面，提供缘契和传统八字姻缘分析相关入口。",
    },
    {
        "mode": "Emo 模式",
        "page": "情感日记",
        "route": "/tools/emo_diary/",
        "content": "情感日记页面，用于记录情绪波动和情感状态，帮助用户回顾自己的情绪变化。",
    },
    {
        "mode": "Emo 模式",
        "page": "创意写作",
        "route": "/tools/creative_writer/",
        "content": "创意写作页面，结合 AI 协助用户创作文字内容，释放创意。",
    },
]


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


def search_chunks(owner, query: str, limit: int = 5, document_ids: list[int] | None = None) -> list[dict]:
    if not query.strip():
        raise RagInputError("请输入搜索问题或测试生成请求")
    query_vector = embed(query)
    candidates = RequirementChunk.objects.filter(Q(document__owner=owner) | Q(document__owner__isnull=True))
    if document_ids is not None:
        candidates = candidates.filter(document_id__in=document_ids)
    candidates = candidates.select_related("document")
    ranked = sorted(
        ((cosine_similarity(query_vector, chunk.vector), chunk) for chunk in candidates),
        key=lambda item: item[0],
        reverse=True,
    )[: max(1, min(limit, 10))]
    return [
        {
            "document_id": chunk.document_id,
            "document": chunk.document.title,
            "source": "shared" if chunk.document.owner_id is None else "private",
            "chunk_id": chunk.id,
            "sequence": chunk.sequence,
            "content": chunk.content,
            "score": round(score, 4),
        }
        for score, chunk in ranked
        if score > 0
    ]


def search_documents(owner, query: str, limit: int = 10, mode: str | None = None) -> list[dict]:
    """Return authorized documents ranked by their best matching chunk."""
    query_text = query.strip().lower()
    matches = search_chunks(owner, query, limit=max(10, min(limit * 6, 60)))
    mode_prefix = f"ModeShift / {mode.strip()} /" if mode and mode.strip() else None
    documents: dict[int, dict] = {}
    for match in matches:
        if mode_prefix and not match["document"].startswith(mode_prefix):
            continue
        item = documents.setdefault(
            match["document_id"],
            {
                "id": match["document_id"],
                "title": match["document"],
                "score": match["score"],
                "snippet": match["content"][:280],
                "source": match["source"],
            },
        )
        item["score"] = max(item["score"], match["score"])
    for item in documents.values():
        title = item["title"].lower()
        if query_text and query_text in title:
            item["score"] = min(1.0, item["score"] + 0.35)
        else:
            query_terms = set(_tokens(query_text))
            title_terms = set(_tokens(title))
            overlap = len(query_terms & title_terms)
            if overlap:
                item["score"] = min(1.0, item["score"] + min(0.2, overlap * 0.04))
    return sorted(documents.values(), key=lambda item: (-item["score"], item["title"]))[: max(1, min(limit, 20))]


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


@transaction.atomic
def _sync_shared_document(title: str, content: str, source_type: str) -> RequirementDocument:
    """Create or refresh a public document and its local searchable chunks."""
    document, _ = RequirementDocument.objects.get_or_create(
        owner=None,
        title=title,
        defaults={"source_type": source_type, "extracted_text": content, "source_file": ""},
    )
    if document.extracted_text == content and document.chunks.exists():
        return document
    document.source_type = source_type
    document.source_file = ""
    document.extracted_text = content
    document.save(update_fields=["source_type", "source_file", "extracted_text"])
    document.chunks.all().delete()
    RequirementChunk.objects.bulk_create(
        [
            RequirementChunk(document=document, sequence=index + 1, content=piece, vector=embed(piece))
            for index, piece in enumerate(chunk_text(content))
        ]
    )
    return document


def sync_product_guide() -> RequirementDocument | None:
    """Return the primary granular module document.

    The full product guide remains a human-readable file under ``docs/`` but
    is intentionally not indexed as one giant RAG document.  The module list
    below is the retrieval source so a query returns a feature card instead
    of the whole product manual.
    """
    primary = MODE_KNOWLEDGE_MODULES[0]
    return RequirementDocument.objects.filter(
        owner=None,
        title=f"ModeShift / {primary['mode']} / {primary['page']}",
    ).first()


def sync_site_capabilities() -> RequirementDocument:
    """Index one shared RAG document per actual mode/page/feature module.

    Curated modules remain authoritative where they exist. Route cards are
    generated from first-party source evidence and are synchronized only when
    the current catalog marker/count is absent, so normal search requests do
    not rewrite hundreds of rows.
    """
    RequirementDocument.objects.filter(owner=None, title__in=LEGACY_SYSTEM_TITLES).delete()
    public_features = Feature.objects.filter(is_active=True, is_public=True).order_by("category", "name")
    modules = list(MODE_KNOWLEDGE_MODULES)
    for feature in public_features:
        modules.append(
            {
                "mode": "系统功能目录",
                "page": feature.name,
                "route": feature.url_name,
                "content": f"系统登记的公开功能模块：{feature.name}。功能分类：{feature.get_category_display()}；功能类型：{feature.get_feature_type_display()}；功能说明：{feature.description or '暂无额外说明'}；路由名：{feature.url_name}。",
            }
        )

    route_modules = list(build_site_capability_cards())
    expected_auto_titles = {f"ModeShift / {item['mode']} / {item['page']}" for item in route_modules}
    auto_qs = RequirementDocument.objects.filter(owner=None, source_type=AUTO_CATALOG_SOURCE_TYPE)
    auto_ready = auto_qs.filter(extracted_text__contains=AUTO_CATALOG_MARKER).count() == len(expected_auto_titles)
    auto_titles_match = auto_ready and not auto_qs.exclude(title__in=expected_auto_titles).exists()
    if not auto_titles_match:
        auto_qs.exclude(title__in=expected_auto_titles).delete()
    needs_auto_sync = not auto_titles_match or auto_qs.filter(title__in=expected_auto_titles).count() != len(expected_auto_titles)

    documents = []
    for module in modules:
        title = f"ModeShift / {module['mode']} / {module['page']}"
        content = (
            f"# {title}\n\n"
            f"所属模式：{module['mode']}\n"
            f"页面或接口：{module['route']}\n\n"
            f"{module['content']}\n\n"
            "检索提示：这是一个独立功能模块文档；生成测试用例时只引用与当前需求直接相关的事实。"
        )
        documents.append(_sync_shared_document(title, content, "system"))
    if needs_auto_sync:
        for module in route_modules:
            title = f"ModeShift / {module['mode']} / {module['page']}"
            content = f"{module['content']}\n\n{AUTO_CATALOG_MARKER}\n检索提示：本卡由注册路由、视图源码和实际模板控件自动提取；没有列出的行为必须待确认。"
            _sync_shared_document(title, content, AUTO_CATALOG_SOURCE_TYPE)
    return documents[0]
