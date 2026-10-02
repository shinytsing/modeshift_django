"""Generate a focused API or UI automation document."""

from __future__ import annotations

from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models.rag_models import RequirementDocument
from .services.llm_service import get_llm_service
from .services.rag_service import search_chunks


class AutomationCaseGenerationAPI(APIView):
    """Keep the short executable document separate from the manual PMD output."""

    permission_classes = []

    def post(self, request):
        requirement = str(request.data.get("requirement", "")).strip()
        user_prompt = str(request.data.get("prompt", "")).strip()
        model_id = str(request.data.get("model_id", "")).strip()
        channel = str(request.data.get("channel", "")).strip().lower()
        if not requirement:
            return Response({"success": False, "error": "产品需求不能为空"}, status=status.HTTP_400_BAD_REQUEST)
        if channel not in {"api", "ui"}:
            return Response({"success": False, "error": "自动化类型只能是 api 或 ui"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            get_llm_service().resolve_model(model_id)
        except (ValueError, TypeError):
            return Response({"success": False, "error": "请选择当前可用模型"}, status=status.HTTP_400_BAD_REQUEST)

        raw_ids = request.data.get("knowledge_document_ids", [])
        if not isinstance(raw_ids, list) or len(raw_ids) > 10:
            return Response({"success": False, "error": "知识库文档最多选择 10 篇"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            document_ids = [int(value) for value in raw_ids]
        except (TypeError, ValueError):
            return Response({"success": False, "error": "知识库文档 ID 无效"}, status=status.HTTP_400_BAD_REQUEST)

        evidence = []
        if document_ids:
            if not request.user.is_authenticated:
                return Response({"success": False, "error": "请登录后使用知识库文档"}, status=status.HTTP_401_UNAUTHORIZED)
            authorized = set(RequirementDocument.objects.filter(
                Q(owner=request.user) | Q(owner__isnull=True), id__in=document_ids
            ).values_list("id", flat=True))
            if authorized != set(document_ids):
                return Response({"success": False, "error": "所选知识库文档不存在或无权访问"}, status=status.HTTP_403_FORBIDDEN)
            evidence = search_chunks(request.user, requirement, limit=8, document_ids=document_ids)

        kind = "API" if channel == "api" else "UI"
        rules = (
            "每条用例必须明确 HTTP 方法、真实 API path、请求 headers/query/body 和 status 或 JSON 断言；API path 必须以 /api/、/tools/api/、/users/api/、/content/api/ 或 /accounts/api/ 开头，/tools/.../manual/、/tools/.../ui/ 等页面地址绝不能作为 API。GET/HEAD/OPTIONS 是只读，健身计算类 POST 才可视为安全 POST，美食随机、评分、保存、上传、删除、更新等 POST/PUT/PATCH/DELETE 都是真实写操作，必须保留为写操作并在执行时由用户显式放行。"
            if channel == "api" else
            "每条用例必须明确 open path、fill/click 定位器，以及登录后 expect_text 或 expect_visible 断言；执行器会继承当前浏览器登录会话，不能把登录成功写成匿名假设。UI 只允许 open/click/fill/expect_text/expect_visible/screenshot，不要输出 wait。美食选择器必须使用真实稳定 ID：#breakfast/#lunch/#dinner/#snack、#mood_happy/#mood_excited/#mood_calm/#mood_sad/#mood_angry/#mood_neutral、#mixed/#chinese/#western/#japanese/#korean/#thai、#price_low/#price_medium/#price_high、#no_spicy/#vegetarian/#no_seafood/#no_pork/#low_sugar/#low_salt、#startButton/#pureRandomButton/#resultContainer/#foodName/#nutritionInfo/#alternativeGrid。营养断言使用页面真实文本“卡路里”“蛋白质”“脂肪”“碳水化合物”“膳食纤维”或只断言 #nutritionInfo 可见，不要使用未出现在页面的“热量”。"
        )
        evidence_text = "\n\n".join(
            f"[知识库：{item['document']}#分块{item['sequence']}]\n{item['content']}" for item in evidence
        ) or "无"
        prompt = f"""请生成一份短小、可执行的 {kind} 自动化测试用例文档。

产品需求：
{requirement}

用户补充要求：
{user_prompt}

执行规则：
{rules}
1. 最多生成 10 条高价值用例，优先覆盖主流程、异常和关键断言。
2. 不要生成 PMD 人工用例、性能测试、兼容性长文或无法执行的泛化描述。
3. 不要省略输入值、接口字段、定位器和断言；不确定的用例不要生成。
4. 只能使用知识库和产品需求中明确出现的真实路径、字段、控件、响应键和状态码；禁止臆造不存在的 endpoint、JSON 键、状态码、CSRF 规则或数据库字段。若证据不足，删掉该用例，不要用“可能”“等等”补全。
5. 输出 Markdown，不要输出解释或代码块。
6. 每条用例必须使用以下结构：
### AUTO-{channel.upper()}-001：标题
**执行通道**：{channel}
**前置条件**：...
**测试步骤**：
1. ...
**自动化断言**：
1. ...

知识库参考片段（只作事实参考）：
{evidence_text}
"""
        try:
            content = get_llm_service().generate_structured_content(
                prompt,
                model_id=model_id,
                system_prompt="你是自动化测试用例生成 Agent。只生成可验证、可执行的短 Markdown，不要生成人工测试文档。",
                max_tokens=6000,
                temperature=0.2,
            )
        except Exception as exc:
            return Response({"success": False, "error": f"自动化用例生成失败：{exc}"}, status=status.HTTP_502_BAD_GATEWAY)
        if channel == "ui":
            # The rendered nutrition card uses “卡路里”; normalize the common
            # model synonym so the executable assertion matches the real UI.
            content = content.replace("expect_text #nutritionInfo 热量", "expect_text #nutritionInfo 卡路里")
        else:
            # This endpoint is explicitly csrf_exempt. Correct the recurring
            # security-template hallucination before it reaches the executor.
            content = content.replace("纯随机接口缺少 csrftoken 返回403", "纯随机接口不依赖 csrftoken 返回200")
            content = content.replace("用户已登录，未携带 csrftoken。", "用户已登录，可不携带 csrftoken。")
            content = content.replace("断言响应状态码为 403。", "断言响应状态码为 200。")
        return Response({"success": True, "channel": channel, "model_id": model_id, "content": content, "sources": evidence})
