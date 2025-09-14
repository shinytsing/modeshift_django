"""
AI助手视图 - 提供智能对话功能
"""

import json
import logging
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def ai_assistant_api(request):
    """AI助手API - 处理用户消息并返回AI回复"""
    try:
        # 解析请求数据
        data = json.loads(request.body)
        user_message = data.get("message", "")
        conversation_history = data.get("history", [])
        
        if not user_message:
            return JsonResponse({"success": False, "error": "消息内容不能为空"}, status=400)
        
        # 构建系统提示词
        system_prompt = """你是一位专业的AI智能助手，专门为用户提供各种帮助和服务。

你的主要功能包括：
1. 生成测试用例 - 根据需求生成详细的测试用例文档
2. 创建旅游攻略 - 为用户制定详细的旅游计划和建议
3. 生成小红书内容 - 创作吸引人的社交媒体内容
4. 创意写作 - 帮助用户进行各种创意写作
5. 数据分析 - 分析和解读各种数据
6. 系统使用指导 - 帮助用户了解如何使用系统功能

系统功能清单：
- 测试用例生成器：可以根据需求自动生成功能测试、界面测试、性能测试等用例
- 旅游攻略工具：提供详细的旅游规划、景点推荐、行程安排
- 小红书内容生成：创作符合平台特色的内容，包括标题、正文、标签
- 塔罗牌占卜：提供塔罗牌解读和占卜服务
- 冥想音频：提供各种冥想音频和放松音乐
- 地图服务：集成高德地图，提供位置服务和导航
- 聊天系统：支持实时聊天和视频通话
- 任务管理：帮助用户管理日常任务和计划

回答指导原则：
- 保持友好、专业、有帮助的态度
- 根据用户需求提供具体的指导和建议
- 如果用户询问系统功能，详细说明如何使用
- 提供实用的操作步骤和建议
- 鼓励用户尝试不同的功能
- 用简洁明了的语言回答

请根据用户的询问提供相应的帮助和建议。"""

        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史对话（限制最近10轮）
        for msg in conversation_history[-10:]:
            messages.append(msg)
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        # 获取LLM服务并生成回复
        llm_service = get_llm_service()
        
        # 根据用户消息类型选择不同的生成策略
        if any(keyword in user_message.lower() for keyword in ['测试用例', '测试', '用例']):
            # 测试用例相关
            response = llm_service.generate_content(
                user_message,
                system_prompt="你是一位资深的测试工程师，擅长生成完整、详细的测试用例。请根据用户需求提供具体的测试用例生成指导。",
                max_tokens=2000
            )
        elif any(keyword in user_message.lower() for keyword in ['旅游', '攻略', '旅行', '景点']):
            # 旅游攻略相关
            response = llm_service.generate_content(
                user_message,
                system_prompt="你是一位专业的旅游规划师，擅长制定详细的旅游攻略和行程安排。请根据用户需求提供具体的旅游建议。",
                max_tokens=2000
            )
        elif any(keyword in user_message.lower() for keyword in ['小红书', '内容', '文案', '分享']):
            # 小红书内容相关
            response = llm_service.generate_content(
                user_message,
                system_prompt="你是一位专业的小红书内容创作者，擅长创作吸引人的旅游、美食、生活分享内容。请根据用户需求提供具体的内容创作建议。",
                max_tokens=2000
            )
        elif any(keyword in user_message.lower() for keyword in ['写作', '创意', '文案', '内容创作']):
            # 创意写作相关
            response = llm_service.generate_content(
                user_message,
                system_prompt="你是一位创意写作专家，擅长创作各种类型的创意内容。请根据用户需求提供具体的写作建议和指导。",
                max_tokens=2000
            )
        elif any(keyword in user_message.lower() for keyword in ['分析', '数据', '统计', '解读']):
            # 数据分析相关
            response = llm_service.generate_content(
                user_message,
                system_prompt="你是一位专业的数据分析师，擅长进行深度分析和解读。请根据用户需求提供具体的分析建议。",
                max_tokens=2000
            )
        elif any(keyword in user_message.lower() for keyword in ['如何使用', '怎么用', '功能', '系统']):
            # 系统使用指导
            response = llm_service.generate_content(
                user_message,
                system_prompt="你是一位系统使用指导专家，专门帮助用户了解如何使用各种系统功能。请根据用户询问提供详细的使用步骤和指导。",
                max_tokens=1500
            )
        else:
            # 通用对话
            response = llm_service.generate_content(
                user_message,
                system_prompt="你是一位友好的AI助手，请根据用户的问题提供有用的回答和建议。",
                max_tokens=1500
            )
        
        logger.info(f"AI助手回复用户 {request.user.id}: {user_message[:50]}...")
        
        return JsonResponse({
            "success": True,
            "response": response,
            "timestamp": json.dumps({"timestamp": "now"})
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"}, status=400)
    except Exception as e:
        logger.error(f"AI助手API处理异常: {str(e)}")
        return JsonResponse({"success": False, "error": f"服务暂时不可用: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def ai_assistant_features_api(request):
    """获取AI助手功能清单API"""
    try:
        features = {
            "success": True,
            "features": [
                {
                    "id": "test_cases",
                    "name": "测试用例生成",
                    "description": "根据需求自动生成详细的测试用例",
                    "icon": "fas fa-vial",
                    "keywords": ["测试用例", "测试", "用例", "功能测试"]
                },
                {
                    "id": "travel_guide",
                    "name": "旅游攻略生成",
                    "description": "制定详细的旅游计划和行程安排",
                    "icon": "fas fa-map-marked-alt",
                    "keywords": ["旅游", "攻略", "旅行", "景点"]
                },
                {
                    "id": "redbook_content",
                    "name": "小红书内容生成",
                    "description": "创作吸引人的社交媒体内容",
                    "icon": "fas fa-heart",
                    "keywords": ["小红书", "内容", "文案", "分享"]
                },
                {
                    "id": "creative_writing",
                    "name": "创意写作",
                    "description": "帮助进行各种创意写作",
                    "icon": "fas fa-pen-fancy",
                    "keywords": ["写作", "创意", "文案", "内容创作"]
                },
                {
                    "id": "data_analysis",
                    "name": "数据分析",
                    "description": "分析和解读各种数据",
                    "icon": "fas fa-chart-bar",
                    "keywords": ["分析", "数据", "统计", "解读"]
                },
                {
                    "id": "system_guide",
                    "name": "系统使用指导",
                    "description": "帮助了解如何使用系统功能",
                    "icon": "fas fa-question-circle",
                    "keywords": ["如何使用", "怎么用", "功能", "系统"]
                }
            ]
        }
        
        return JsonResponse(features)
        
    except Exception as e:
        logger.error(f"获取AI助手功能清单失败: {str(e)}")
        return JsonResponse({"success": False, "error": "获取功能清单失败"}, status=500)
