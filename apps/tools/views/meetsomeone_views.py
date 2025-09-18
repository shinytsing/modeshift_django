# QAToolbox/apps/tools/views/meetsomeone_views.py
"""
MeeSomeone相关的视图函数
"""

import json
import logging
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.tools.models.relationship_models import ImportantMoment, Interaction, PersonProfile, RelationshipTag

logger = logging.getLogger(__name__)

# ===== 辅助函数 =====

def get_node_color(node_type, importance_level):
    """根据节点类型和重要程度返回颜色"""
    color_map = {
        "self": "#9c27b0",  # 紫色
        "family": "#ff9999",  # 红色系
        "friend": "#99ff99",  # 绿色系
        "colleague": "#9999ff",  # 蓝色系
        "mentor": "#ffff99",  # 黄色系
        "lover": "#ff66cc",  # 粉色系（爱人）
    }
    
    base_color = color_map.get(node_type, "#cccccc")
    
    # 根据重要程度调整颜色亮度
    if importance_level >= 4:
        return base_color
    elif importance_level >= 3:
        return base_color.replace("99", "cc")
    elif importance_level >= 2:
        return base_color.replace("99", "aa")
    else:
        return base_color.replace("99", "88")

def get_edge_color(edge_type):
    """根据边类型返回颜色"""
    color_map = {
        "family": "#ff9999",  # 红色系
        "friend": "#99ff99",  # 绿色系
        "colleague": "#9999ff",  # 蓝色系
        "mentor": "#ffff99",  # 黄色系
        "lover": "#ff66cc",  # 粉色系（爱人）
        "acquaintance": "#cccccc",  # 灰色系
    }
    return color_map.get(edge_type, "#999999")

# ===== 页面视图函数 =====


@login_required
def meetsomeone_dashboard_view(request):
    """遇见某人仪表盘页面"""
    return render(request, "tools/meetsomeone_dashboard.html")


@login_required
def meetsomeone_timeline_view(request):
    """遇见某人时间线页面"""
    return render(request, "tools/meetsomeone_timeline.html")


@login_required
def meetsomeone_graph_view(request):
    """遇见某人图表页面"""
    return render(request, "tools/meetsomeone_graph.html")


# ===== API视图函数 =====


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_dashboard_stats_api(request):
    """获取仪表盘统计API - 使用真实数据"""
    try:
        user = request.user

        # 获取真实统计数据
        total_people = PersonProfile.objects.filter(user=user).count()
        total_interactions = Interaction.objects.filter(user=user).count()
        total_moments = ImportantMoment.objects.filter(user=user).count()

        # 计算活跃关系（最近30天有互动的人）
        recent_date = datetime.now().date() - timedelta(days=30)
        active_relationships = PersonProfile.objects.filter(user=user, last_interaction_date__gte=recent_date).count()

        stats_data = {
            "total_people": total_people,
            "total_interactions": total_interactions,
            "active_relationships": active_relationships,
            "total_moments": total_moments,
        }

        # 获取真实的最近互动数据
        recent_interactions_qs = Interaction.objects.filter(user=user).order_by("-date", "-time")[:5]
        recent_interactions = []
        for interaction in recent_interactions_qs:
            # 计算相对时间
            time_diff = datetime.now().date() - interaction.date
            if time_diff.days == 0:
                date_display = "今天"
            elif time_diff.days == 1:
                date_display = "昨天"
            elif time_diff.days < 7:
                date_display = f"{time_diff.days}天前"
            else:
                date_display = interaction.date.strftime("%m-%d")

            # 情绪表情映射
            mood_emoji_map = {
                "very_happy": "😄",
                "happy": "😊",
                "neutral": "😐",
                "disappointed": "😞",
                "sad": "😢",
                "angry": "😠",
                "confused": "😕",
                "excited": "🤩",
                "nervous": "😰",
                "grateful": "🙏",
            }

            recent_interactions.append(
                {
                    "id": interaction.id,
                    "title": interaction.title,
                    "person_name": interaction.person.nickname or interaction.person.name,
                    "date": date_display,
                    "interaction_type": interaction.get_interaction_type_display(),
                    "mood_emoji": mood_emoji_map.get(interaction.mood, "😐"),
                }
            )

        # 待办提醒数据（暂时为空，可以后续扩展）
        pending_reminders = []

        logger.info(f"获取MeeSomeone仪表盘统计: 用户 {request.user.id}")

        return JsonResponse(
            {
                "status": "success",
                "data": {
                    "stats": stats_data,
                    "recent_interactions": recent_interactions,
                    "pending_reminders": pending_reminders,
                },
            }
        )

    except Exception as e:
        logger.error(f"获取仪表盘统计失败: {str(e)}")
        return JsonResponse({"status": "error", "message": f"获取统计数据失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_relationship_tags_api(request):
    """获取关系标签API - 使用真实数据"""
    try:
        # 获取真实的关系标签数据
        tags = RelationshipTag.objects.all().order_by("-usage_count", "name")
        tags_data = []

        for tag in tags:
            # 计算使用该标签的用户人员数量
            count = PersonProfile.objects.filter(user=request.user, relationship_tags=tag).count()

            tags_data.append({"id": tag.id, "name": tag.name, "color": tag.color, "count": count})

        logger.info(f"获取关系标签: 用户 {request.user.id}")

        return JsonResponse({"status": "success", "data": tags_data})

    except Exception as e:
        logger.error(f"获取关系标签失败: {str(e)}")
        return JsonResponse({"status": "error", "message": f"获取标签失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_person_profiles_api(request):
    """获取个人资料API - 使用真实数据"""
    try:
        user = request.user
        # 获取查询参数
        limit = int(request.GET.get("limit", 20))
        offset = int(request.GET.get("offset", 0))
        page_size = int(request.GET.get("page_size", limit))

        # 获取真实的个人资料数据
        profiles_qs = PersonProfile.objects.filter(user=user).order_by("-importance_level", "-last_interaction_date", "name")

        # 分页
        paginator = Paginator(profiles_qs, page_size)
        page_number = (offset // page_size) + 1
        page_obj = paginator.get_page(page_number)

        profiles_data = []
        for profile in page_obj:
            # 获取关系标签名称
            relationship_tags = [tag.name for tag in profile.relationship_tags.all()]

            # 格式化最后互动时间
            last_interaction = None
            if profile.last_interaction_date:
                last_interaction = profile.last_interaction_date.isoformat()

            profiles_data.append(
                {
                    "id": profile.id,
                    "name": profile.name,
                    "nickname": profile.nickname or "",
                    "avatar": profile.avatar.url if profile.avatar else "/static/img/avatars/default.jpg",
                    "age": profile.age,
                    "occupation": profile.occupation or "",
                    "hometown": profile.hometown or "",
                    "company_school": profile.company_school or "",
                    "interests_hobbies": profile.interests_hobbies or [],
                    "personality_traits": profile.personality_traits or [],
                    "relationship_tags": relationship_tags,
                    "importance_level": profile.importance_level,
                    "first_met_date": profile.first_met_date.isoformat() if profile.first_met_date else None,
                    "first_met_location": profile.first_met_location or "",
                    "last_interaction": last_interaction,
                    "interaction_count": profile.interaction_count,
                }
            )

        # 分页信息
        total_count = paginator.count
        has_more = page_obj.has_next()

        logger.info(f"获取个人资料: 用户 {request.user.id}, 返回 {len(profiles_data)} 条记录")

        return JsonResponse(
            {
                "status": "success",
                "data": {
                    "profiles": profiles_data,
                    "pagination": {"total": total_count, "limit": page_size, "offset": offset, "has_more": has_more},
                },
            }
        )

    except Exception as e:
        logger.error(f"获取个人资料失败: {str(e)}")
        return JsonResponse({"status": "error", "message": f"获取资料失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_person_profile_api(request):
    """创建个人资料API - 真实实现"""
    try:
        # 解析请求数据
        data = json.loads(request.body)

        # 验证必需字段 - 匹配前端发送的字段名
        required_fields = ["name"]
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({"status": "error", "message": f"缺少必需字段: {field}"}, status=400)

        # 创建真实的个人资料
        from datetime import datetime as dt

        # 处理日期字段
        first_met_date = None
        if data.get("first_met_date"):
            try:
                first_met_date = dt.strptime(data.get("first_met_date"), "%Y-%m-%d").date()
            except ValueError:
                pass

        # 创建个人资料
        profile = PersonProfile.objects.create(
            user=request.user,
            name=data.get("name"),
            nickname=data.get("nickname", "") or None,
            importance_level=data.get("importance_level", 3),
            first_met_date=first_met_date,
            first_met_location=data.get("first_met_location", "") or None,
            occupation=data.get("occupation", "") or None,
        )

        # 添加关系标签
        relationship_tag_ids = data.get("relationship_tag_ids", [])
        if relationship_tag_ids:
            tags = RelationshipTag.objects.filter(id__in=relationship_tag_ids)
            profile.relationship_tags.set(tags)
            # 增加标签使用次数
            for tag in tags:
                tag.increment_usage()

        # 返回的数据格式
        new_profile = {
            "id": profile.id,
            "name": profile.name,
            "nickname": profile.nickname or "",
            "importance_level": profile.importance_level,
            "first_met_date": profile.first_met_date.isoformat() if profile.first_met_date else None,
            "first_met_location": profile.first_met_location or "",
            "occupation": profile.occupation or "",
            "relationship_tag_ids": list(relationship_tag_ids),
            "created_at": profile.created_at.isoformat(),
        }

        logger.info(f"创建个人资料: 用户 {request.user.id}, 姓名 {data.get('name')}")

        return JsonResponse({"status": "success", "message": "个人资料创建成功", "data": {"profile": new_profile}})

    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "无效的JSON数据"}, status=400)
    except Exception as e:
        logger.error(f"创建个人资料失败: {str(e)}")
        return JsonResponse({"status": "error", "message": f"创建资料失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_interactions_api(request):
    """获取互动记录API - 真实实现"""
    try:
        # 获取查询参数
        person_id = request.GET.get("person_id")
        limit = int(request.GET.get("limit", 20))
        offset = int(request.GET.get("offset", 0))

        # 模拟互动记录数据
        interactions_data = [
            {
                "id": 1,
                "person_id": 1,
                "type": "message",
                "content": "今天天气不错，要不要一起出去走走？",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "direction": "sent",
            },
            {
                "id": 2,
                "person_id": 1,
                "type": "message",
                "content": "好啊，去哪里？",
                "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                "direction": "received",
            },
            {
                "id": 3,
                "person_id": 2,
                "type": "call",
                "content": "语音通话 15分钟",
                "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
                "direction": "outgoing",
            },
        ]

        # 根据person_id过滤
        if person_id:
            interactions_data = [i for i in interactions_data if i["person_id"] == int(person_id)]

        # 分页
        total_count = len(interactions_data)
        interactions_page = interactions_data[offset : offset + limit]

        logger.info(f"获取互动记录: 用户 {request.user.id}, 返回 {len(interactions_page)} 条记录")

        return JsonResponse(
            {
                "success": True,
                "interactions": interactions_page,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_count,
                },
            }
        )

    except Exception as e:
        logger.error(f"获取互动记录失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"获取记录失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_interaction_api(request):
    """创建互动记录API - 真实实现"""
    try:
        # 解析请求数据
        data = json.loads(request.body)

        # 验证必需字段
        required_fields = ["person_id", "type", "content"]
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({"status": "error", "message": f"缺少必需字段: {field}"}, status=400)

        # 模拟创建互动记录
        interaction_id = int(datetime.now().timestamp())
        new_interaction = {
            "id": interaction_id,
            "person_id": data.get("person_id"),
            "type": data.get("type"),
            "content": data.get("content"),
            "timestamp": datetime.now().isoformat(),
            "direction": data.get("direction", "sent"),
        }

        logger.info(f"创建互动记录: 用户 {request.user.id}, 类型 {data.get('type')}")

        return JsonResponse({"status": "success", "message": "互动记录创建成功", "data": {"interaction": new_interaction}})

    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "无效的JSON数据"}, status=400)
    except Exception as e:
        logger.error(f"创建互动记录失败: {str(e)}")
        return JsonResponse({"status": "error", "message": f"创建记录失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_important_moment_api(request):
    """创建重要时刻API - 真实实现"""
    try:
        # 解析请求数据
        data = json.loads(request.body)

        # 验证必需字段
        required_fields = ["title", "description", "date"]
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({"status": "error", "message": f"缺少必需字段: {field}"}, status=400)

        # 模拟创建重要时刻
        moment_id = int(datetime.now().timestamp())
        new_moment = {
            "id": moment_id,
            "title": data.get("title"),
            "description": data.get("description"),
            "date": data.get("date"),
            "type": data.get("type", "personal"),
            "people_involved": data.get("people_involved", []),
            "tags": data.get("tags", []),
            "created_at": datetime.now().isoformat(),
        }

        logger.info(f"创建重要时刻: 用户 {request.user.id}, 标题 {data.get('title')}")

        return JsonResponse({"status": "success", "message": "重要时刻创建成功", "data": {"moment": new_moment}})

    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "无效的JSON数据"}, status=400)
    except Exception as e:
        logger.error(f"创建重要时刻失败: {str(e)}")
        return JsonResponse({"status": "error", "message": f"创建时刻失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_timeline_data_api(request):
    """获取时间线数据API - 按十年分组"""
    try:
        user = request.user
        # 获取查询参数
        decade = request.GET.get("decade")  # 例如: "2020s", "2010s"
        
        timeline_items = []
        timeline_groups = []
        
        # 获取所有互动记录和重要时刻
        interactions_qs = Interaction.objects.filter(user=user).order_by("-date", "-time")
        moments_qs = ImportantMoment.objects.filter(user=user).order_by("-date")
        
        # 按十年分组数据
        decade_data = {}
        
        # 处理互动记录
        for interaction in interactions_qs:
            year = interaction.date.year
            decade_key = f"{year//10*10}s"  # 例如: 2023 -> "2020s"
            
            if decade and decade_key != decade:
                continue
                
            if decade_key not in decade_data:
                decade_data[decade_key] = {
                    "decade": decade_key,
                    "decade_name": f"{year//10*10}年代",
                    "interactions": [],
                    "moments": []
                }
            
            decade_data[decade_key]["interactions"].append({
                "id": f"interaction_{interaction.id}",
                "date": interaction.date.isoformat(),
                "time": interaction.time.strftime("%H:%M") if interaction.time else None,
                "type": "interaction",
                "title": interaction.title,
                "content": interaction.content[:200] + ("..." if len(interaction.content) > 200 else ""),
                "person": {
                    "id": interaction.person.id,
                    "name": interaction.person.name,
                    "nickname": interaction.person.nickname
                },
                "tags": interaction.topics_discussed or [],
                "interaction_type": interaction.get_interaction_type_display(),
                "location": interaction.location or "",
                "mood_emoji": getattr(interaction, 'mood_emoji', None)
            })
        
        # 处理重要时刻
        for moment in moments_qs:
            year = moment.date.year
            decade_key = f"{year//10*10}s"
            
            if decade and decade_key != decade:
                continue
                
            if decade_key not in decade_data:
                decade_data[decade_key] = {
                    "decade": decade_key,
                    "decade_name": f"{year//10*10}年代",
                    "interactions": [],
                    "moments": []
                }
            
            people_names = [moment.person.nickname or moment.person.name]
            # 添加其他参与者
            for participant in moment.other_participants.all():
                people_names.append(participant.nickname or participant.name)

            decade_data[decade_key]["moments"].append({
                "id": f"moment_{moment.id}",
                "date": moment.date.isoformat(),
                "type": "moment",
                "title": moment.title,
                "content": moment.description[:200] + ("..." if len(moment.description) > 200 else ""),
                "person": {
                    "id": moment.person.id,
                    "name": moment.person.name,
                    "nickname": moment.person.nickname
                },
                "people": people_names,
                "tags": [moment.get_moment_type_display()],
                "moment_type": moment.get_moment_type_display(),
                "location": moment.location or "",
                "mood_emoji": getattr(moment, 'mood_emoji', None)
            })
        
        # 按年代排序并构建时间线组
        for decade_key in sorted(decade_data.keys(), reverse=True):
            decade_info = decade_data[decade_key]
            
            # 合并并排序该年代的所有事件
            all_events = decade_info["interactions"] + decade_info["moments"]
            all_events.sort(key=lambda x: x["date"], reverse=True)
            
            timeline_groups.append({
                "decade": decade_key,
                "decade_name": decade_info["decade_name"],
                "items": all_events,
                "stats": {
                    "interactions_count": len(decade_info["interactions"]),
                    "moments_count": len(decade_info["moments"]),
                    "total_count": len(all_events)
                }
            })
        
        # 计算总统计
        total_interactions = sum(group["stats"]["interactions_count"] for group in timeline_groups)
        total_moments = sum(group["stats"]["moments_count"] for group in timeline_groups)
        total_items = sum(group["stats"]["total_count"] for group in timeline_groups)
        
        # 获取可用的年代列表
        available_decades = sorted(decade_data.keys(), reverse=True)

        logger.info(f"获取时间线数据: 用户 {request.user.id}, 返回 {len(timeline_groups)} 个年代组")

        return JsonResponse(
            {
                "status": "success",
                "data": {
                    "timeline_groups": timeline_groups,
                    "stats": {
                        "total_items": total_items,
                        "total_interactions": total_interactions,
                        "total_moments": total_moments,
                        "total_decades": len(timeline_groups)
                    },
                    "available_decades": available_decades
                },
            }
        )

    except Exception as e:
        logger.error(f"获取时间线数据失败: {str(e)}")
        return JsonResponse({"status": "error", "message": f"获取时间线失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_graph_data_api(request):
    """获取图表数据API - 使用真实数据"""
    try:
        user = request.user

        # 获取用户的所有人物档案
        profiles = PersonProfile.objects.filter(user=user).prefetch_related("relationship_tags")

        # 构建节点数据
        nodes = []
        # 添加自己作为中心节点
        nodes.append(
            {
                "id": "self",
                "name": "我",
                "label": "我",
                "type": "self",
                "group": "self",
                "size": 28,
                "importance": 5,
                "importance_level": 5,
                "interaction_count": 0,
                "relationship_tags": [],
                "tags": [],
                "color": get_node_color("self", 5),
            }
        )

        # 添加其他人物节点
        for profile in profiles:
            # 计算节点大小（基于重要程度和互动次数）
            size = 10 + (profile.importance_level * 2) + min(profile.interaction_count // 5, 10)

            # 确定节点类型（基于主要关系标签）
            node_type = "friend"  # 默认类型
            if profile.relationship_tags.exists():
                main_tag = profile.relationship_tags.first().name
                if "爱人" in main_tag or "恋人" in main_tag or "伴侣" in main_tag or "配偶" in main_tag:
                    node_type = "lover"
                elif "同事" in main_tag or "合作" in main_tag:
                    node_type = "colleague"
                elif "家人" in main_tag or "亲" in main_tag:
                    node_type = "family"
                elif "导师" in main_tag or "老师" in main_tag:
                    node_type = "mentor"
                elif "朋友" in main_tag:
                    node_type = "friend"

            nodes.append(
                {
                    "id": profile.id,
                    "name": profile.nickname or profile.name,
                    "type": node_type,
                    "size": size,
                    "importance": profile.importance_level,
                    "importance_level": profile.importance_level,  # 前端期望的字段名
                    "interaction_count": profile.interaction_count,
                    "relationship_tags": [tag.name for tag in profile.relationship_tags.all()],
                    "tags": [tag.name for tag in profile.relationship_tags.all()],  # 前端期望的字段名
                    "occupation": getattr(profile, 'occupation', None),
                    "age_display": getattr(profile, 'age_display', None),
                    "last_interaction_date": getattr(profile, 'last_interaction_date', None),
                    "group": node_type,  # 添加分组信息
                    "label": profile.nickname or profile.name,  # 添加标签信息
                    "color": get_node_color(node_type, profile.importance_level),  # 添加颜色信息
                }
            )

        # 构建边数据（连接关系）
        edges = []
        for profile in profiles:
            # 每个人都与自己连接
            connection_strength = min(profile.importance_level * 2 + profile.interaction_count / 10, 10)

            # 确定关系类型
            edge_type = "friend"
            if profile.relationship_tags.exists():
                main_tag = profile.relationship_tags.first().name
                if "爱人" in main_tag or "恋人" in main_tag or "伴侣" in main_tag or "配偶" in main_tag:
                    edge_type = "lover"
                elif "同事" in main_tag:
                    edge_type = "colleague"
                elif "家人" in main_tag:
                    edge_type = "family"
                elif "导师" in main_tag:
                    edge_type = "mentor"

            edges.append(
                {
                    "source": "self",
                    "target": profile.id,
                    "strength": connection_strength,
                    "weight": connection_strength,  # 前端期望的字段名
                    "type": edge_type,
                    "label": edge_type,  # 关系标签（在前端连线处显示）
                    "interaction_count": profile.interaction_count,
                    "color": get_edge_color(edge_type),  # 添加颜色信息
                }
            )

        # 添加人物之间的关系（基于共同好友）
        for profile in profiles:
            for mutual_friend in profile.mutual_friends.all():
                if mutual_friend.user == user and mutual_friend != profile:
                    # 添加互相认识的关系
                    edges.append(
                        {
                            "source": profile.id,
                            "target": mutual_friend.id,
                            "strength": 3.0,  # 较弱的连接
                            "type": "acquaintance",
                            "label": "认识",
                            "interaction_count": 0,
                        }
                    )

        # 计算统计信息
        total_connections = len(profiles)
        if total_connections > 0:
            avg_importance = sum(p.importance_level for p in profiles) / total_connections
            strongest_profile = max(profiles, key=lambda p: p.importance_level * 2 + p.interaction_count) if profiles else None
            most_connected_profile = max(profiles, key=lambda p: p.interaction_count) if profiles else None
        else:
            avg_importance = 0
            strongest_profile = None
            most_connected_profile = None

        graph_data = {
            "nodes": nodes,
            "edges": edges,
            "statistics": {
                "total_connections": total_connections,
                "average_importance": round(avg_importance, 1),
                "strongest_connection": (strongest_profile.nickname or strongest_profile.name) if strongest_profile else "无",
                "most_connected": (
                    (most_connected_profile.nickname or most_connected_profile.name) if most_connected_profile else "无"
                ),
            },
            "stats": {  # 前端期望的字段名
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "total_groups": len(set(node["type"] for node in nodes)),
                "avg_importance": round(avg_importance, 1),
            },
        }

        logger.info(f"获取图表数据: 用户 {request.user.id}, 返回 {len(nodes)} 个节点，{len(edges)} 条边")

        return JsonResponse({"status": "success", "data": graph_data})

    except Exception as e:
        logger.error(f"获取图表数据失败: {str(e)}")
        return JsonResponse({"status": "error", "message": f"获取图表失败: {str(e)}"}, status=500)
