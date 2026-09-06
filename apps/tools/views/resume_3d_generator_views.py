"""Upload a resume and turn its source text into a shareable 3D resume view."""

import base64
import io
import re

from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


MAX_RESUME_SIZE = 10 * 1024 * 1024
SUPPORTED_RESUME_TYPES = {".pdf", ".docx"}
CITY_NAMES = ("北京", "上海", "广州", "深圳", "武汉", "杭州", "成都", "南京", "苏州", "西安", "长沙", "厦门", "重庆", "天津")
COMPANY_MARKS = (
    {"keys": ("顺丰航空",), "detail_keys": ("顺丰航空",), "url": "https://www.sf-airlines.com/sf/template/upimg/logo.svg", "label": "顺丰航空"},
    {"keys": ("高途", "悦学帮"), "detail_keys": ("高途",), "url": "https://about.gaotu.cn/images/gaotulogo.png", "label": "高途"},
    {"keys": ("微派", "青藤之恋"), "detail_keys": ("微派", "青藤之恋"), "url": "https://www.wepie.com/favicon.ico", "label": "微派网络"},
    {"keys": ("奇安信",), "detail_keys": ("奇安信", "鹰图"), "url": "https://www.qianxin.com/static/images/logo-95015.png", "label": "奇安信"},
)
DATE_RANGE = re.compile(r"(?:19|20)\d{2}(?:[./年-]\d{1,2})?\s*(?:-|—|至|~)\s*(?:(?:19|20)\d{2}(?:[./年-]\d{1,2})?|至今|现在)")


def _extension(filename):
    return "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def extract_resume_text(upload):
    """Return normalized resume text without writing the user document to disk."""
    extension = _extension(upload.name)
    if extension not in SUPPORTED_RESUME_TYPES:
        raise ValueError("仅支持 PDF 或 DOCX 格式的简历。")
    if upload.size > MAX_RESUME_SIZE:
        raise ValueError("简历文件不能超过 10 MB。")

    raw_bytes = upload.read()
    if extension == ".pdf":
        try:
            from pypdf import PdfReader

            text = "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(raw_bytes)).pages)
        except Exception as error:
            raise ValueError("无法读取该 PDF，请上传可复制文字的 PDF 简历。") from error
    else:
        try:
            from docx import Document

            document = Document(io.BytesIO(raw_bytes))
            text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        except Exception as error:
            raise ValueError("无法读取该 DOCX，请检查文件是否损坏。") from error

    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if not text:
        raise ValueError("没有识别到简历文字；扫描件请先转为可复制文字的 PDF。")
    return text


def _company_mark(text):
    for company in COMPANY_MARKS:
        if any(keyword in text for keyword in company["keys"]):
            return {"url": company["url"], "label": company["label"]}
    return None


def _explicit_city(text):
    for line in text.splitlines():
        compact = line.replace(" ", "")
        for city in CITY_NAMES:
            if compact == city or re.search(rf"(?:工作地点|地点|所在(?:地|城市)?|城市)[:：]?{city}", compact):
                return city
    return None


def _heading(lines):
    for line in lines[:8]:
        compact = line.replace(" ", "")
        if 1 < len(compact) <= 8 and re.fullmatch(r"[\u4e00-\u9fff·A-Za-z]+", compact):
            return compact
    return "3D 简历"


def parse_resume(text):
    """Keep every source line while adding only explicitly detectable job metadata."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    date_indexes = [
        index
        for index, line in enumerate(lines)
        if DATE_RANGE.search(line) and not any(keyword in line for keyword in ("教育", "本科", "硕士", "博士"))
    ]
    detail_sections = {}
    detail_starts = [index for index, line in enumerate(lines) if "业务背景" in line]
    for position, start in enumerate(detail_starts):
        details = lines[start : detail_starts[position + 1] if position + 1 < len(detail_starts) else len(lines)]
        details_text = "\n".join(details)
        for company in COMPANY_MARKS:
            if any(keyword in details_text for keyword in company["detail_keys"]):
                detail_sections[company["label"]] = details
                break
    jobs = []
    for position, start in enumerate(date_indexes):
        end = date_indexes[position + 1] if position + 1 < len(date_indexes) else len(lines)
        section = lines[start:end]
        details = "\n".join(section)
        period_match = DATE_RANGE.search(section[0])
        period = period_match.group(0) if period_match else section[0]
        company_line = DATE_RANGE.sub("", section[0]).strip(" |-—")
        if not company_line:
            company_line = next((line for line in section[1:4] if len(line) <= 80), "工作经历")
        mark = _company_mark(company_line)
        job_details = detail_sections.get(mark["label"], []) if mark else []
        jobs.append(
            {
                "period": period,
                "company": company_line,
                "location": _explicit_city(details),
                "mark": mark,
                "details": job_details or section[1:] or ["简历未提供该段的补充描述。"],
            }
        )
    return {"name": _heading(lines), "jobs": jobs, "source_lines": lines, "source_text": text}


def avatar_data_url(upload):
    if not upload:
        return ""
    if upload.size > 3 * 1024 * 1024 or not (upload.content_type or "").startswith("image/"):
        raise ValueError("头像需为 3 MB 以内的图片文件。")
    encoded = base64.b64encode(upload.read()).decode("ascii")
    return f"data:{upload.content_type};base64,{encoded}"


@require_http_methods(["GET", "POST"])
def resume_3d_generator(request):
    if request.method == "GET":
        return render(request, "tools/resume_3d_generator.html")

    resume = request.FILES.get("resume")
    if not resume:
        return HttpResponseBadRequest("请选择一份 PDF 或 DOCX 简历。")
    try:
        result = parse_resume(extract_resume_text(resume))
        result["avatar_url"] = avatar_data_url(request.FILES.get("avatar"))
    except ValueError as error:
        return render(request, "tools/resume_3d_generator.html", {"error": str(error)}, status=400)
    return render(request, "tools/resume_3d_generated.html", result)
