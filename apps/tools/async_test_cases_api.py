import logging

from django.db.models import Q
from rest_framework.permissions import IsAuthenticated

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .async_task_manager import get_task_manager
from .models.rag_models import RequirementDocument
from .services.llm_service import get_llm_service
from .services.rag_service import search_chunks

logger = logging.getLogger(__name__)


def _requester_id(request, create_session=False):
    if request.user.is_authenticated:
        return f"user:{request.user.pk}"
    if create_session and not request.session.session_key:
        request.session.create()
    return f"anonymous:{request.session.session_key or ''}"


class AsyncGenerateTestCasesAPI(APIView):
    """异步测试用例生成 API"""

    permission_classes = []  # 允许匿名访问

    def post(self, request):
        """创建异步任务"""
        try:
            # 获取请求参数
            requirement = request.data.get("requirement", "").strip()
            user_prompt = request.data.get("prompt", "").strip()
            is_batch = request.data.get("is_batch", False)
            batch_id = int(request.data.get("batch_id", 0))
            total_batches = int(request.data.get("total_batches", 1))

            # 参数验证
            if not requirement:
                return Response({"success": False, "error": "需求内容不能为空"}, status=status.HTTP_400_BAD_REQUEST)

            model_id = str(request.data.get("model_id", "")).strip()
            try:
                get_llm_service().resolve_model(model_id)
            except (ValueError, TypeError):
                return Response(
                    {"success": False, "error": "请选择模型目录中已配置的模型"}, status=status.HTTP_400_BAD_REQUEST
                )

            raw_document_ids = request.data.get("knowledge_document_ids", [])
            if not isinstance(raw_document_ids, list) or len(raw_document_ids) > 10:
                return Response(
                    {"success": False, "error": "知识库文档选择无效（最多选择 10 篇）"}, status=status.HTTP_400_BAD_REQUEST
                )
            try:
                document_ids = [int(value) for value in raw_document_ids]
            except (TypeError, ValueError):
                return Response({"success": False, "error": "知识库文档 ID 无效"}, status=status.HTTP_400_BAD_REQUEST)
            if len(set(document_ids)) != len(document_ids):
                return Response({"success": False, "error": "知识库文档不能重复选择"}, status=status.HTTP_400_BAD_REQUEST)
            evidence = []
            if document_ids:
                if not request.user.is_authenticated:
                    return Response({"success": False, "error": "请登录后使用知识库文档"}, status=status.HTTP_401_UNAUTHORIZED)
                authorized = set(
                    RequirementDocument.objects.filter(
                        Q(owner=request.user) | Q(owner__isnull=True), id__in=document_ids
                    ).values_list("id", flat=True)
                )
                if authorized != set(document_ids):
                    return Response(
                        {"success": False, "error": "所选知识库文档不存在或无权访问"}, status=status.HTTP_403_FORBIDDEN
                    )
                evidence = search_chunks(request.user, requirement, limit=10, document_ids=document_ids)

            # 创建异步任务 - 智能选择模式
            user_id = _requester_id(request, create_session=True)

            # 使用真实AI服务
            task_manager = get_task_manager()
            task_id = task_manager.create_task(
                requirement=requirement,
                user_prompt=user_prompt,
                is_batch=is_batch,
                batch_id=batch_id,
                total_batches=total_batches,
                user_id=user_id,
                evidence=evidence,
                model_id=model_id,
            )

            logger.info(f"创建异步任务: {task_id}, 用户: {request.user.username if request.user.is_authenticated else '匿名'}")

            return Response({"success": True, "task_id": task_id, "message": "任务已创建，正在后台处理中..."})

        except Exception as e:
            logger.error(f"创建异步任务失败: {e}")
            return Response(
                {"success": False, "error": f"创建任务失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TaskStatusAPI(APIView):
    """任务状态查询 API"""

    permission_classes = []  # 允许匿名访问

    def get(self, request, task_id):
        """获取任务状态"""
        try:
            # 直接从文件系统读取任务状态
            import json
            import os
            from .async_task_manager import AsyncTaskManager

            task_manager = AsyncTaskManager()
            tasks_file = os.path.join(task_manager.storage_dir, "tasks.json")

            if os.path.exists(tasks_file):
                with open(tasks_file, "r", encoding="utf-8") as f:
                    tasks_data = json.load(f)
                    task = tasks_data.get(task_id)
            else:
                task = None

            if not task:
                return Response({"success": False, "error": "任务不存在"}, status=status.HTTP_404_NOT_FOUND)

            requester_id = _requester_id(request)
            if requester_id.endswith(":") or task.get("user_id") != requester_id:
                return Response({"success": False, "error": "无权访问此任务"}, status=status.HTTP_403_FORBIDDEN)

            # 构建响应数据
            response_data = {
                "success": True,
                "task_id": task["id"],
                "status": task["status"],
                "progress": task["progress"],
                "created_at": task.get("created_at"),
                "started_at": task.get("started_at"),
                "completed_at": task.get("completed_at"),
            }

            # 如果任务完成，返回结果
            if task["status"] == "completed":
                response_data["result"] = task["result"]
                response_data["sources"] = task.get("evidence", [])
            elif task["status"] == "failed":
                response_data["error"] = task["error"]

            # 添加当前步骤信息
            if "current_step" in task:
                response_data["current_step"] = task["current_step"]
            response_data["selected_model"] = task.get("model_id")

            return Response(response_data)

        except Exception as e:
            logger.error(f"获取任务状态失败: {e}")
            return Response(
                {"success": False, "error": f"获取任务状态失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TaskListAPI(APIView):
    """任务列表 API"""

    permission_classes = []  # 允许匿名访问

    def get(self, request):
        """获取任务列表"""
        try:
            # 直接从文件系统读取任务列表
            import json
            import os
            from .async_task_manager import AsyncTaskManager

            task_manager = AsyncTaskManager()
            tasks_file = os.path.join(task_manager.storage_dir, "tasks.json")

            if os.path.exists(tasks_file):
                with open(tasks_file, "r", encoding="utf-8") as f:
                    tasks_data = json.load(f)
                    tasks = list(tasks_data.values())
            else:
                tasks = []

            # 按创建时间倒序排列
            requester_id = _requester_id(request)
            tasks = [task for task in tasks if not requester_id.endswith(":") and task.get("user_id") == requester_id]
            tasks.sort(key=lambda x: x["created_at"], reverse=True)

            # 只返回基本信息，不包含结果内容
            task_list = []
            for task in tasks:
                task_list.append(
                    {
                        "id": task["id"],
                        "requirement": task["requirement"],
                        "status": task["status"],
                        "progress": task["progress"],
                        "created_at": task.get("created_at"),
                        "started_at": task.get("started_at"),
                        "completed_at": task.get("completed_at"),
                    }
                )

            return Response({"success": True, "tasks": task_list, "total": len(task_list)})

        except Exception as e:
            logger.error(f"获取任务列表失败: {e}")
            return Response(
                {"success": False, "error": f"获取任务列表失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeleteTaskAPI(APIView):
    """删除任务 API"""

    permission_classes = []  # 允许匿名访问

    def dispatch(self, request, *args, **kwargs):
        # 手动设置CSRF豁免
        setattr(request, "_dont_enforce_csrf_checks", True)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        """删除任务"""
        try:
            task_id = request.data.get("task_id")

            if not task_id:
                return Response({"success": False, "error": "任务ID不能为空"}, status=status.HTTP_400_BAD_REQUEST)

            # 删除任务
            task_manager = get_task_manager()
            task = task_manager.get_task_status(task_id)
            requester_id = _requester_id(request)
            if not task or requester_id.endswith(":") or task.get("user_id") != requester_id:
                return Response({"success": False, "error": "任务不存在或无权访问"}, status=status.HTTP_404_NOT_FOUND)
            success = task_manager.delete_task(task_id)

            if success:
                logger.info(f"任务 {task_id} 删除成功")
                return Response({"success": True, "message": "任务删除成功"})
            else:
                return Response({"success": False, "error": "任务不存在"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"删除任务失败: {e}")
            return Response(
                {"success": False, "error": f"删除任务失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ModelCatalogAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"models": get_llm_service().get_model_catalog()})
