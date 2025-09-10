"""
基础工具视图
包含测试用例生成器、小红书生成器、PDF转换器等基础工具
"""

import json
import logging
import os

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import requests

from ..services.ip_location_service import IPLocationService

logger = logging.getLogger(__name__)


@login_required
def test_case_generator(request):
    """测试用例生成器页面"""
    return render(request, "tools/test_case_generator.html")


@login_required
def task_manager(request):
    """后台任务管理器页面"""
    return render(request, "tools/task_manager.html")


@login_required
def redbook_generator(request):
    """小红书文案生成器页面"""
    return render(request, "tools/redbook_generator.html")


@login_required
def pdf_converter(request):
    """PDF转换器页面"""
    return render(request, "tools/pdf_converter_modern.html")


def pdf_converter_test(request):
    """PDF转换器测试页面（无需登录）"""
    return render(request, "tools/pdf_converter_modern.html")


@login_required
def yuanqi_marriage_analyzer(request):
    """缘契 - 传统八字姻缘分析平台"""
    return render(request, "tools/yuanqi_marriage_analyzer.html")


@login_required
def fortune_analyzer(request):
    """重定向到缘契姻缘分析平台（保持向后兼容）"""
    from django.shortcuts import redirect
    from django.urls import reverse

    return redirect(reverse("tools:yuanqi_marriage_analyzer"))


@login_required
def web_crawler(request):
    """社交媒体订阅页面"""
    return render(request, "tools/web_crawler.html")


def social_subscription_demo(request):
    """社交媒体订阅功能演示页面"""
    return render(request, "tools/social_subscription_demo.html")


@login_required
def self_analysis(request):
    """人生百态镜页面"""
    return render(request, "tools/self_analysis.html")


@login_required
def storyboard(request):
    """故事板页面"""
    return render(request, "tools/storyboard.html")


@login_required
def fitness_center(request):
    """FitMatrix健身矩阵页面"""
    return render(request, "tools/fitness_center.html")


@login_required
def training_plan_editor(request):
    """训练计划编辑器页面"""
    return render(request, "tools/training_plan_editor.html")


# deepseek_api函数已移除 - 使用base_views.py中的实现


@login_required
def self_analysis_api(request):
    """人生百态镜API"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            question = data.get("question", "")

            if not question:
                return JsonResponse({"success": False, "error": "问题不能为空"})

            # 构建分析提示词
            prompt = """
            作为一个专业的心理咨询师和人生导师，请基于以下信息进行分析：

            用户问题：{question}
            
            请从以下角度进行分析：
            1. 心理层面：情绪状态、思维模式、行为动机
            2. 社会层面：人际关系、环境因素、社会支持
            3. 发展层面：个人成长、目标设定、潜力挖掘
            4. 建议层面：具体行动建议、改善方向、资源推荐
            
            请用温暖、专业、实用的语言回答，帮助用户更好地认识自己和改善现状。
            """

            # 调用DeepSeek API进行分析
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                return JsonResponse({"success": False, "error": "分析服务暂时不可用"})

            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

            payload = {
                "messages": [{"role": "user", "content": prompt}],
                "model": "deepseek-chat",
                "max_tokens": 1000,
                "temperature": 0.7,
            }

            response = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                analysis = result["choices"][0]["message"]["content"]

                return JsonResponse({"success": True, "analysis": analysis, "timestamp": timezone.now().isoformat()})
            else:
                return JsonResponse({"success": False, "error": "分析服务暂时不可用，请稍后重试"})

        except Exception as e:
            return JsonResponse({"success": False, "error": f"分析失败: {str(e)}"})

    return JsonResponse({"success": False, "error": "只支持POST请求"})


@csrf_exempt
@require_http_methods(["POST"])
def storyboard_api(request):
    """故事板API"""
    try:
        data = json.loads(request.body)
        prompt = data.get("prompt", "")

        # DeepSeek API配置
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            return JsonResponse({"error": "API密钥未配置"}, status=500, content_type="application/json")

        # 构建系统提示词
        system_prompt = """你是一位富有同理心和创造力的故事作家，专门创作治愈系故事。

你的任务是：
1. 根据用户的描述创作温暖治愈的故事
2. 故事要有情感共鸣和深度
3. 语言优美，富有诗意和想象力
4. 传递积极向上的价值观
5. 结尾要有启发性和治愈感

创作要求：
- 故事长度控制在400-600字
- 情节要引人入胜
- 人物形象要生动
- 情感表达要真实
- 要有哲思和启发

请根据用户的描述，创作一个独特而治愈的故事。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请根据以下描述创作一个治愈故事：{prompt}"},
        ]

        # 调用DeepSeek API
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        payload = {"model": "deepseek-chat", "messages": messages, "temperature": 0.8, "max_tokens": 1000}

        response = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            story = result["choices"][0]["message"]["content"]

            return JsonResponse({"success": True, "story": story}, content_type="application/json")
        elif response.status_code == 402:
            # API余额不足时返回示例故事
            fallback_stories = [
                f"基于您的描述「{prompt}」，让我为您创作一个治愈的故事：\n\n在一个安静的午后，小雨轻敲着窗台。李明坐在咖啡店的角落，手中捧着一杯温热的拿铁，思考着生活的意义。\n\n突然，一只小猫从雨中跑进了咖啡店，浑身湿漉漉的。店员想要赶走它，但李明轻声说道：「让它留下来吧，或许它也需要一个温暖的地方。」\n\n小猫似乎听懂了什么，安静地卧在李明脚边。此刻，李明意识到，生活中最美好的时光，往往来自于这些不期而遇的温柔瞬间。\n\n有时候，我们不需要寻找答案，只需要学会在当下找到属于自己的宁静与温暖。",
                f"关于「{prompt}」的故事：\n\n夕阳西下时，老师傅在工作室里专注地雕刻着一块木头。每一刀都小心翼翼，每一划都充满敬意。\n\n年轻的学徒好奇地问：「师傅，为什么您对待每一块木头都如此认真？」\n\n老师傅停下手中的工作，温和地说：「因为每一块木头都有它的故事，我只是帮它找到最美的表达方式。」\n\n学徒恍然大悟，原来匠心不在于技巧的高超，而在于对每一件事物的尊重与热爱。\n\n生活也是如此，当我们用心对待每一个平凡的日子，就会发现其中蕴含的无限可能。",
                f"以「{prompt}」为灵感的治愈故事：\n\n图书馆里，一位老奶奶每天都会来看书。她总是选择靠窗的位置，安静地翻阅着同一本诗集。\n\n管理员小王很好奇，终于有一天忍不住问道：「奶奶，您为什么总是看这本书呢？」\n\n老奶奶笑着说：「这是我已故老伴最喜欢的诗集。每次读它，就像是在和他对话一样。」\n\n小王的眼中泛起泪花，她明白了，有些书不只是书，有些阅读不只是阅读，而是一种特殊的陪伴方式。\n\n爱从不会因为离别而消失，它会以不同的形式继续温暖着我们。",
            ]

            import random

            story = random.choice(fallback_stories)

            return JsonResponse(
                {"success": True, "story": story, "fallback": True, "message": "AI服务暂时不可用，为您提供了精选的治愈故事"},
                content_type="application/json",
            )
        else:
            return JsonResponse({"error": f"API调用失败: {response.status_code}"}, status=500, content_type="application/json")

    except Exception as e:
        return JsonResponse({"error": f"处理请求时出错: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def location_api(request):
    """位置信息API"""
    try:
        ip_service = IPLocationService()

        # 获取用户位置信息
        location = ip_service.get_user_location(request)

        return JsonResponse({"success": True, "location": location})
    except Exception as e:
        logger.error(f"位置API错误: {str(e)}")
        return JsonResponse({"success": False, "message": "获取位置信息失败", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_location_api(request):
    """更新用户位置信息API"""
    try:
        data = json.loads(request.body)
        city_name = data.get("city", "").strip()

        if not city_name:
            return JsonResponse({"success": False, "message": "城市名称不能为空"}, status=400)

        ip_service = IPLocationService()
        location = ip_service.get_location_by_city_name(city_name)

        return JsonResponse({"success": True, "location": location})
    except Exception as e:
        logger.error(f"更新位置API错误: {str(e)}")
        return JsonResponse({"success": False, "message": "更新位置信息失败", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def ai_analysis_api(request):
    """
    AI智能分析API - 接入DeepSeek
    """
    try:
        data = json.loads(request.body)
        prompt = data.get("prompt", "")
        data.get("userData", {})

        # 调用DeepSeek API
        ai_response = call_deepseek_api(prompt)

        return JsonResponse({"success": True, "analysis": ai_response})
    except Exception as e:
        logger.error(f"AI分析API错误: {str(e)}")
        # 返回模拟分析结果作为备选
        mock_analysis = generate_mock_analysis(data.get("userData", {}))
        return JsonResponse({"success": True, "analysis": mock_analysis})


def call_deepseek_api(prompt):
    """
    调用DeepSeek API
    """
    try:
        # DeepSeek API配置
        api_key = os.getenv("DEEPSEEK_API_KEY", "")
        api_url = "https://api.deepseek.com/v1/chat/completions"

        if not api_key:
            raise Exception("DeepSeek API密钥未配置")

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位资深的中国传统命理学专家，精通八字命理和姻缘分析。请提供专业、详细且实用的分析建议。",
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 2000,
            "temperature": 0.7,
        }

        response = requests.post(api_url, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            ai_content = result["choices"][0]["message"]["content"]

            # 解析AI回复并结构化
            return parse_ai_response(ai_content)
        else:
            raise Exception(f"DeepSeek API调用失败: {response.status_code}")

    except Exception as e:
        logger.error(f"DeepSeek API调用错误: {str(e)}")
        raise e


def parse_ai_response(ai_content):
    """
    解析AI回复内容并结构化
    """
    # 尝试将AI回复分段处理
    sections = []
    current_section = {"title": "AI智能分析", "content": ""}

    lines = ai_content.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 检测标题行（包含数字、特殊符号等）
        if any(
            marker in line
            for marker in [
                "一、",
                "二、",
                "三、",
                "四、",
                "五、",
                "六、",
                "七、",
                "1.",
                "2.",
                "3.",
                "4.",
                "5.",
                "6.",
                "7.",
                "##",
                "**",
            ]
        ):
            if current_section["content"]:
                sections.append(current_section)
            current_section = {"title": line, "content": ""}
        else:
            if current_section["content"]:
                current_section["content"] += "\n"
            current_section["content"] += line

    # 添加最后一个section
    if current_section["content"]:
        sections.append(current_section)

    # 如果没有找到明确的分段，返回整体内容
    if not sections:
        sections = [{"title": "🧠 AI深度分析", "content": ai_content}]

    return {"title": "AI智能深度分析", "sections": sections}


def generate_mock_analysis(user_data):
    """
    生成模拟AI分析结果（备选方案）
    """
    mode = user_data.get("mode", "couple")

    if mode == "couple":
        male_name = user_data.get("male", {}).get("name", "男方")
        female_name = user_data.get("female", {}).get("name", "女方")

        return {
            "title": "AI智能深度分析",
            "sections": [
                {
                    "title": "🧠 AI深度洞察",
                    "content": f"基于大数据分析和传统命理学的结合，AI系统深度分析了{male_name}和{female_name}的八字信息。通过对比数万个成功案例，发现你们在五行配置上具有较好的互补性，特别是在性格匹配度方面表现出色。",
                },
                {
                    "title": "🔮 未来趋势预测",
                    "content": "根据八字运势和现代心理学分析，预测你们的感情发展将在接下来的6-12个月内迎来重要转机。建议在春季（3-5月）或秋季（9-11月）考虑重要的感情决定，这些时期的能量场最为和谐。",
                },
                {
                    "title": "💡 个性化建议",
                    "content": "AI建议你们在日常相处中要注意沟通方式的调整。建议多进行户外活动，如登山、散步等，这有助于增强你们的感情纽带。同时要避免在情绪波动较大的时期做重要决定。",
                },
                {
                    "title": "⚠️ 注意事项",
                    "content": "需要特别关注的是双方在处理压力时的不同方式。建议建立定期的深度沟通机制，每周安排固定时间进行心灵交流，这将大大提升你们的关系稳定性。",
                },
            ],
        }
    else:
        person_name = user_data.get("person", {}).get("name", "您")

        return {
            "title": "AI智能深度分析",
            "sections": [
                {
                    "title": "🧠 个人特质分析",
                    "content": f"AI系统分析了{person_name}的八字特征，发现您具有较强的感情敏感度和直觉能力。您的性格中既有温和的一面，也有坚定的原则性，这种平衡使您在感情中能够给予对方安全感。",
                },
                {
                    "title": "💕 理想伴侣画像",
                    "content": "基于您的八字分析，最适合您的伴侣类型应该具备：稳重可靠的性格、良好的沟通能力、以及与您互补的五行属性。建议寻找在事业上有一定成就，同时注重家庭生活的对象。",
                },
                {
                    "title": "🌟 姻缘时机预测",
                    "content": "AI预测您的最佳姻缘时期将在未来18个月内出现。特别是在农历的春季和夏季，桃花运势最为旺盛。建议在这段时间内多参加社交活动，扩大交友圈。",
                },
                {
                    "title": "📋 行动建议",
                    "content": "建议您在寻找另一半的过程中保持开放的心态，不要过分拘泥于外在条件。重点关注对方的品格和价值观是否与您匹配。同时，提升自己的内在修养也很重要。",
                },
            ],
        }
