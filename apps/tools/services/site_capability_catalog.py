"""Evidence-only RAG cards for registered first-party pages and APIs.

The catalogue intentionally records what can be verified from URL patterns,
view source and rendered templates. It never infers an endpoint's business
success from a suggestive name or treats an uninspected POST as read-only.
"""

from __future__ import annotations

import ast
import inspect
import re
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path

from django.urls import URLPattern, URLResolver, get_resolver


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FIRST_PARTY_MODULES = ("apps.", "views", "testing_views", "urls")
SKIP_PREFIXES = ("admin/", "__debug__/", "static/", "media/", "favicon.ico")
CONTROL_TAGS = {"input", "button", "select", "textarea", "form"}
REQUEST_SOURCES = {"GET", "POST", "FILES", "data", "query_params"}
WRITE_METHODS = {"save", "delete", "create", "update", "bulk_create", "bulk_update", "get_or_create", "update_or_create"}


def _module_group(route: str) -> tuple[str, str]:
    segments = [part for part in route.split("/") if part and not part.startswith("<")]
    stem = "/".join(part for part in segments if part != "api")
    if route.startswith("tools/"):
        stem = stem.removeprefix("tools/")
    first = stem.split("/", 1)[0]
    if first in {
        "fitness",
        "fitness_center",
        "training",
        "training_mode",
        "training_plan_editor",
        "guitar-training",
        "guitar-progress",
        "guitar-theory",
        "guitar-songs",
        "guitar-practice",
    } or stem.startswith(("training_plans/", "fitness_", "guitar_")):
        return "训练模式", "健身与训练" if "guitar" not in stem else "吉他训练"
    if first in {
        "life",
        "life_mode",
        "diary",
        "simple-diary",
        "food_randomizer",
        "food-randomizer",
        "food_photo_binding",
        "food_image_correction",
        "travel_guide",
        "travel_posts",
        "travel_cities",
        "shipbao",
        "meditation_guide",
        "music_healing",
        "nutrition",
        "life_goals",
    } or stem.startswith(("travel_", "diary_", "food_")):
        group = (
            "美食选择器"
            if "food" in stem
            else "旅行与社区" if "travel" in stem or "shipbao" in stem else "生活日记" if "diary" in stem else "生活工具"
        )
        return "生活模式", group
    if first in {
        "emo",
        "emo_mode",
        "self_analysis",
        "storyboard",
        "fortune_analyzer",
        "tarot",
        "meetsomeone",
        "heart_link",
        "chat",
        "video-chat",
        "multi-video-chat",
        "buddy",
        "number-match",
        "creative_writer",
    }:
        return "Emo 模式", "情感与社交"
    if first in {
        "vanity_os",
        "vanity_rewards",
        "vanity_todo_list",
        "desire_dashboard",
        "triple_awakening",
        "based_dev_avatar",
        "sponsor_hall_of_fame",
    }:
        return "狂暴模式", "成就与目标"
    if route.startswith(("users/", "accounts/", "auth/")):
        return "账号与系统", "账号与登录"
    if route.startswith(("content/", "share/")):
        return "账号与系统", "内容与分享"
    if route.startswith("api/grading/"):
        return "极客模式", "作业批改"
    if first in {
        "test_case_generator",
        "requirement-rag",
        "testing-dashboard",
        "testing-functional",
        "testing-api",
        "testing-performance",
        "testing-security",
    } or stem.startswith(("rag/", "async/", "automation-cases/", "llm/", "generate-testcases/", "tests/")):
        return "极客模式", "测试与知识库"
    if first in {"job-search", "java-job", "boss"}:
        return "极客模式", "招聘自动化"
    if first in {
        "pdf_converter",
        "resume-3d-generator",
        "web_crawler",
        "audio_converter",
        "zip-tool",
        "redbook_generator",
        "proxy-dashboard",
    }:
        return "极客模式", "效率工具"
    return "系统功能目录", first.replace("_", " ") or "首页"


def _first_party_patterns(patterns, prefix=""):
    for pattern in patterns:
        route = prefix + str(pattern.pattern)
        if route.startswith(SKIP_PREFIXES):
            continue
        if isinstance(pattern, URLResolver):
            yield from _first_party_patterns(pattern.url_patterns, route)
        elif isinstance(pattern, URLPattern):
            callback = getattr(pattern.callback, "view_class", None) or inspect.unwrap(pattern.callback)
            module = getattr(callback, "__module__", "")
            if module.startswith(FIRST_PARTY_MODULES):
                yield route, pattern, callback


class _ControlParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.controls = []

    def handle_starttag(self, tag, attrs):
        if tag not in CONTROL_TAGS:
            return
        attr = dict(attrs)
        identity = attr.get("id") or attr.get("name")
        if not identity or "{{" in identity or "{%" in identity:
            return
        details = [f"{tag} #{identity}" if attr.get("id") else f"{tag} name={identity}"]
        if tag == "input" and attr.get("type"):
            details.append(f"type={attr['type']}")
        if attr.get("placeholder") and len(attr["placeholder"]) < 100:
            details.append(f"placeholder={attr['placeholder']}")
        self.controls.append("; ".join(details))


def _view_evidence(callback):
    try:
        source_file = Path(inspect.getsourcefile(callback) or "")
        source = inspect.getsource(callback)
        tree = ast.parse(inspect.cleandoc(source))
    except (OSError, IOError, TypeError, SyntaxError, ValueError):
        return {
            "source": "",
            "description": "",
            "methods": [],
            "auth": [],
            "params": [],
            "response_keys": [],
            "statuses": [],
            "writes": [],
            "templates": [],
        }

    try:
        relative_source = str(source_file.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        relative_source = ""
    doc_lines = [line.strip() for line in (inspect.getdoc(callback) or "").splitlines() if line.strip()]
    doc = doc_lines[0] if doc_lines else ""
    doc = re.sub(r"\s+", " ", doc)[:120]
    methods, auth, params, response_keys, statuses, writes, templates = set(), set(), set(), set(), set(), set(), set()
    function = next(
        (node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))), None
    )
    for decorator in getattr(function, "decorator_list", []):
        name = ast.unparse(decorator)
        if "login_required" in name or "permission_required" in name:
            auth.add(name[:100])
        if "csrf_exempt" in name:
            auth.add("csrf_exempt")
        if "require_GET" in name:
            methods.add("GET")
        if "require_POST" in name:
            methods.add("POST")
        if "require_http_methods" in name or "api_view" in name:
            methods.update(re.findall(r"['\"](GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)['\"]", name))

    for node in ast.walk(tree):
        if isinstance(node, ast.Compare) and isinstance(node.left, ast.Attribute) and node.left.attr == "method":
            methods.update(
                value.value
                for value in node.comparators
                if isinstance(value, ast.Constant) and value.value in {"GET", "POST", "PUT", "PATCH", "DELETE"}
            )
        if not isinstance(node, ast.Call):
            continue
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "get"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            receiver = node.func.value
            if (
                isinstance(receiver, ast.Attribute)
                and receiver.attr in REQUEST_SOURCES
                and isinstance(receiver.value, ast.Name)
                and receiver.value.id == "request"
            ):
                params.add(f"{receiver.attr}.{node.args[0].value}")
            elif isinstance(receiver, ast.Name) and receiver.id in {"data", "payload", "body", "params", "request_data"}:
                params.add(f"body.{node.args[0].value}")
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "render"
            and len(node.args) > 1
            and isinstance(node.args[1], ast.Constant)
            and isinstance(node.args[1].value, str)
        ):
            templates.add(node.args[1].value)
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "JsonResponse"
            and node.args
            and isinstance(node.args[0], ast.Dict)
        ):
            response_keys.update(
                key.value for key in node.args[0].keys if isinstance(key, ast.Constant) and isinstance(key.value, str)
            )
            statuses.update(
                kw.value.value
                for kw in node.keywords
                if kw.arg == "status" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, int)
            )
        if isinstance(node.func, ast.Attribute) and node.func.attr in WRITE_METHODS:
            expression = ast.unparse(node.func)
            if len(expression) < 110:
                writes.add(expression)
    if isinstance(function, ast.ClassDef):
        for node in function.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.lower() in {
                "get",
                "post",
                "put",
                "patch",
                "delete",
            }:
                methods.add(node.name.upper())
            if (
                isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == "template_name" for target in node.targets)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                templates.add(node.value.value)
    return {
        "source": relative_source,
        "description": doc,
        "methods": sorted(methods),
        "auth": sorted(auth),
        "params": sorted(params)[:40],
        "response_keys": sorted(response_keys)[:40],
        "statuses": sorted(statuses),
        "writes": sorted(writes)[:15],
        "templates": sorted(templates),
    }


def _template_evidence(template_name: str):
    path = PROJECT_ROOT / "templates" / template_name
    if not path.is_file() or not path.resolve().is_relative_to(PROJECT_ROOT / "templates"):
        return []
    parser = _ControlParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return list(dict.fromkeys(parser.controls))[:60]


@lru_cache(maxsize=1)
def build_site_capability_cards() -> tuple[dict, ...]:
    """Return deterministic, granular facts for each reachable first-party route."""
    cards, seen = [], set()
    for route, pattern, callback in _first_party_patterns(get_resolver().url_patterns):
        if route in seen:
            continue  # The first registration wins; later duplicates are not reachable.
        seen.add(route)
        evidence = _view_evidence(callback)
        mode, group = _module_group(route)
        kind = "API" if "/api/" in f"/{route}" or route.startswith("api/") else "页面"
        name = pattern.name or getattr(callback, "__name__", "route")
        label = evidence["description"] or name.replace("_", " ")
        label = label[:48]
        title = f"ModeShift / {mode} / {group} / {kind} {label} [{name}]"
        if len(title) > 255:
            title = title[:252] + "..."
        template_controls = []
        for template in evidence["templates"][:3]:
            template_controls.extend(_template_evidence(template))
        lines = [f"# {title}", "", f"类型：{kind}", f"注册路径：/{route}", f"路由名：{name}"]
        if evidence["source"]:
            lines.append(f"视图源码：{evidence['source']}::{getattr(callback, '__name__', callback.__class__.__name__)}")
        if evidence["description"]:
            lines.append(f"视图说明：{evidence['description']}")
        lines.append(
            "HTTP 方法（源码显式约束/分支）："
            + ("、".join(evidence["methods"]) if evidence["methods"] else "未见显式声明；不可据此推断其他方法可用")
        )
        lines.append(
            "权限/CSRF 证据："
            + ("、".join(evidence["auth"]) if evidence["auth"] else "当前视图未见显式装饰器；仍须检查中间件、父视图和调用链")
        )
        if evidence["templates"]:
            lines.append("实际渲染模板：" + "、".join(evidence["templates"]))
        if template_controls:
            lines.append("模板实际表单控件（ID/name/type/placeholder）：" + "；".join(template_controls[:60]))
        if evidence["params"]:
            lines.append("视图显式读取的请求字段：" + "、".join(evidence["params"]))
        if evidence["response_keys"]:
            lines.append("JsonResponse 显式字面量顶层字段：" + "、".join(evidence["response_keys"]))
        if evidence["statuses"]:
            lines.append("JsonResponse 显式状态码：" + "、".join(str(value) for value in evidence["statuses"]))
        lines.append(
            "视图源码中的写操作调用："
            + (
                "、".join(evidence["writes"])
                if evidence["writes"]
                else "未见直接写操作；不能据此认定没有下游副作用，POST 默认按真实写操作审慎处理"
            )
        )
        lines.append("测试生成原则：只以本卡列出的源码事实建立断言；未列出的字段、状态码和成功语义必须标为待确认。")
        cards.append(
            {"mode": mode, "page": f"{group} / {kind} {label} [{name}]", "route": f"/{route}", "content": "\n".join(lines)}
        )
    return tuple(cards)
