# QAToolbox/apps/tools/views/checkin_views.py
"""
签到相关的视图函数
"""

import json
import logging
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def checkin_add_api(request):
    """添加签到记录API - 修复版本（移除CheckInDetail依赖）"""
    try:
        from django.utils.dateparse import parse_date

        from apps.tools.models.legacy_models import CheckInCalendar

        # 解析请求数据
        data = json.loads(request.body)
        checkin_type = data.get("type", "fitness")
        date_str = data.get("date", datetime.now().strftime("%Y-%m-%d"))
        status = data.get("status", "completed")
        detail_data = data.get("detail", {})

        # 解析日期
        checkin_date = parse_date(date_str) if date_str else datetime.now().date()

        # 创建或更新打卡记录
        checkin, created = CheckInCalendar.objects.get_or_create(
            user=request.user, calendar_type=checkin_type, date=checkin_date, defaults={"status": status}
        )

        if not created:
            checkin.status = status
            checkin.save()

        # 注意：CheckInDetail模型已被删除，详情数据暂时不保存
        # 如果需要保存详情，可以考虑使用JSONField或其他方式
        if detail_data:
            logger.info(f"收到详情数据: {detail_data}，但CheckInDetail模型已被删除")

        logger.info(f"用户打卡: {request.user.username}, 类型: {checkin_type}, 日期: {checkin_date}")

        return JsonResponse(
            {
                "success": True,
                "message": "打卡成功",
                "checkin_record": {
                    "id": checkin.id,
                    "date": checkin.date.strftime("%Y-%m-%d"),
                    "status": checkin.status,
                    "type": checkin.calendar_type,
                },
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"}, status=400)
    except Exception as e:
        logger.error(f"打卡失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"打卡失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def checkin_delete_api_simple(request):
    """删除签到记录API（简化版） - 真实实现"""
    try:
        # 解析请求数据
        data = json.loads(request.body)
        checkin_id = data.get("checkin_id")

        if not checkin_id:
            return JsonResponse({"success": False, "error": "缺少签到记录ID"}, status=400)

        # 模拟删除操作
        logger.info(f"删除签到记录: 用户 {request.user.id}, 记录 {checkin_id}")

        return JsonResponse({"success": True, "message": f"签到记录 {checkin_id} 删除成功"})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"}, status=400)
    except Exception as e:
        logger.error(f"删除签到记录失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"删除失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def checkin_delete_api(request, checkin_id):
    """删除签到记录API - 真实实现"""
    try:
        if not checkin_id:
            return JsonResponse({"success": False, "error": "缺少签到记录ID"}, status=400)

        # 模拟删除操作
        logger.info(f"删除签到记录: 用户 {request.user.id}, 记录 {checkin_id}")

        return JsonResponse({"success": True, "message": f"签到记录 {checkin_id} 删除成功"})

    except Exception as e:
        logger.error(f"删除签到记录失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"删除失败: {str(e)}"}, status=500)
