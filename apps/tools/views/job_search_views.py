"""
AI找工作助手视图
集成get_jobs项目的功能到Django中
"""
import json
import logging
import os
import time
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.conf import settings
from apps.tools.services.job_search_service import JobSearchService

logger = logging.getLogger(__name__)


def job_search_machine(request):
    """投递机器页面 - 包含"我已登录"按钮"""
    return render(request, 'tools/job_search_machine.html')


@login_required
def job_search_dashboard(request):
    """AI找工作助手主页面"""
    return render(request, "tools/job_search_dashboard.html")


def job_search_launcher(request):
    """AI一键投递启动器页面"""
    return render(request, "tools/job_search_launcher.html")


@csrf_exempt
@require_http_methods(["POST"])
def start_job_search_api(request):
    """启动AI一键投递API - 自动检测Boss直聘登录状态"""
    try:
        data = json.loads(request.body)
        
        # 解析参数
        platforms = data.get('platforms', ['boss'])
        keywords = data.get('keywords', [])
        cities = data.get('cities', [])
        expected_salary = data.get('expected_salary', [])
        say_hi = data.get('say_hi', '')
        use_ai = data.get('use_ai', True)
        send_img_resume = data.get('send_img_resume', False)
        current_browser_cookies = data.get('current_browser_cookies', {})
        
        logger.info(f"接收到投递请求: 平台={platforms}, 关键词={keywords}, 城市={cities}")
        
        # 创建服务实例
        service = JobSearchService()
        
        # 如果不是Boss直聘平台，直接启动
        if 'boss' not in platforms:
            logger.info("🚀 非Boss直聘平台，直接启动投递任务...")
            result = service.start_job_search(
                platforms=platforms,
                keywords=keywords,
                cities=cities,
                expected_salary=expected_salary,
                say_hi=say_hi,
                use_ai=use_ai,
                send_img_resume=send_img_resume,
                user=request.user
            )
            
            # 确保result是字典类型
            if not isinstance(result, dict):
                logger.error(f"❌ 服务方法返回了错误的数据类型: {type(result)}")
                return JsonResponse({
                    "success": False, 
                    "error": "服务内部错误",
                    "details": f"期望字典类型，实际得到: {type(result)}"
                }, status=500)
            
            return JsonResponse(result)
        
        # 检查是否有手动输入的cookies
        if current_browser_cookies and len(current_browser_cookies) > 0:
            logger.info(f"🔧 使用手动输入的cookies: {len(current_browser_cookies)}个")
            
            # 直接使用用户输入的cookies进行投递
            result = service.start_boss_search_with_cookies(
                current_browser_cookies, keywords, cities, 
                expected_salary, say_hi, use_ai, request.user
            )
            
            # 确保result是字典类型
            if not isinstance(result, dict):
                logger.error(f"❌ 服务方法返回了错误的数据类型: {type(result)}")
                return JsonResponse({
                    "success": False, 
                    "error": "服务内部错误",
                    "details": f"期望字典类型，实际得到: {type(result)}"
                }, status=500)
            
            # 添加手动输入信息
            result['login_detected'] = True
            result['session_source'] = 'manual_cookies'
            result['cookie_count'] = len(current_browser_cookies)
            
            logger.info(f"✅ 使用手动cookies，开始执行投递任务...")
            
            # 使用手动cookies启动投递任务
            search_result = service.start_job_search(
                platforms=platforms,
                keywords=keywords,
                cities=cities,
                expected_salary=expected_salary,
                say_hi=say_hi,
                use_ai=use_ai,
                send_img_resume=send_img_resume,
                user=request.user
            )
            
            # 合并结果
            if isinstance(search_result, dict):
                result.update(search_result)
                result['manual_cookies_used'] = True
                result['search_task_started'] = True
                logger.info(f"✅ 手动cookies投递任务启动成功")
            else:
                logger.error(f"❌ start_job_search返回了错误的数据类型: {type(search_result)}")
                result['search_task_started'] = False
                result['error'] = f"投递任务启动失败: 返回了错误的数据类型 {type(search_result)}"
            
            response = JsonResponse(result)
            logger.info(f"🔍 返回响应对象类型: {type(response)}")
            return response
        
        # 自动检测Boss直聘登录状态
        logger.info("🔍 开始检测Boss直聘登录状态...")
        login_status = service.check_boss_login_status(request.user.id)
        
        # 如果有有效的登录状态，直接使用现有session
        if login_status.get('is_logged_in', False):
            # 如果检测到登录状态，直接启动投递任务
            logger.info("🚀 检测到有效登录状态，直接启动投递任务...")
            result = service.start_job_search(
                platforms=platforms,
                keywords=keywords,
                cities=cities,
                expected_salary=expected_salary,
                say_hi=say_hi,
                use_ai=use_ai,
                send_img_resume=send_img_resume,
                user=request.user
            )
            
            # 确保result是字典类型
            if not isinstance(result, dict):
                logger.error(f"❌ 服务方法返回了错误的数据类型: {type(result)}")
                return JsonResponse({
                    "success": False, 
                    "error": "服务内部错误",
                    "details": f"期望字典类型，实际得到: {type(result)}"
                }, status=500)
            
            # 在结果中添加登录状态信息
            if result.get('success'):
                result['login_detected'] = True
                result['login_message'] = '自动检测到Boss直聘登录状态，已直接启动投递任务'
                result['login_status'] = login_status
                result['token_info'] = login_status.get('token_info', {})
                result['user_info'] = login_status.get('user_info', {})
                logger.info(f"✅ Boss直聘登录状态检测成功，置信度: {login_status.get('login_confidence', 0):.2f}")
            
            return JsonResponse(result)
        
        # 如果没有登录状态，返回需要登录的响应
        logger.info("❌ 未检测到Boss直聘登录状态")
        return JsonResponse({
            "success": False,
            "need_login": True,
            "login_detected": False,
            "login_url": "https://www.zhipin.com/web/user/?ka=header-login",
            "message": "需要先登录Boss直聘",
            "instructions": [
                "1. 请先在浏览器中访问 https://www.zhipin.com 并登录",
                "2. 登录成功后，点击右上角的头像确认登录状态",
                "3. 然后重新尝试启动投递任务"
            ],
            "login_status": login_status
        })
        # 暂时移除认证检查，让检测逻辑能够执行
        # if not request.user.is_authenticated:
        #     logger.warning(f"未认证用户尝试访问投递API: {request.META.get('REMOTE_ADDR')}")
        #     return JsonResponse({"success": False, "error": "请先登录"})
        
        user_id = request.user.id if request.user.is_authenticated else 1
        username = request.user.username if request.user.is_authenticated else "anonymous"
        logger.info(f"用户 {username} 启动投递任务")
        
        data = json.loads(request.body)
        
        # 获取参数 - 适配前端发送的数据格式
        # 支持两种数据格式：新格式(数组)和旧格式(字符串)
        platforms = data.get('platforms', ['boss'])
        if not isinstance(platforms, list):
            platforms = [data.get('platform', 'boss')]
        
        keywords = data.get('keywords', ['Python开发'])
        if not isinstance(keywords, list):
            keywords_str = keywords or ''
            keywords = [k.strip() for k in keywords_str.split(',') if k.strip()] if keywords_str else ['Python开发']
        
        cities = data.get('cities', ['北京'])
        if not isinstance(cities, list):
            city = cities or '北京'
            cities = [city]
        
        expected_salary = data.get('expected_salary', [15000, 25000])
        if not isinstance(expected_salary, list):
            # 处理单个薪资值
            salary_val = expected_salary or 15000
            expected_salary = [salary_val, salary_val + 10000]
        
        say_hi = data.get('say_hi', '您好，我对这个职位很感兴趣，希望能有机会进一步沟通。')
        use_ai = data.get('use_ai', True)
        send_img_resume = data.get('send_img_resume', False)
        
        # 获取前端传递的当前浏览器cookies
        current_browser_cookies = data.get('current_browser_cookies', {})
        
        # 验证参数
        if not keywords:
            return JsonResponse({"success": False, "error": "请填写搜索关键词"})
        
        # 调用服务层
        service = JobSearchService()
        
        # 如果包含Boss直聘平台，先自动检测登录状态
        if 'boss' in platforms:
            logger.info(f"🤖 检测到Boss直聘平台，开始自动检测登录状态...")
            
        # 如果用户手动输入了cookies，使用手动cookies
        if current_browser_cookies and len(current_browser_cookies) > 0:
            logger.info(f"🍪 用户手动输入了{len(current_browser_cookies)}个cookies")
            
            # 直接使用用户输入的cookies进行投递
            result = service.start_boss_search_with_cookies(
                current_browser_cookies, keywords, cities, 
                expected_salary, say_hi, use_ai, request.user
            )
            
            # 确保result是字典类型
            if not isinstance(result, dict):
                logger.error(f"❌ 服务方法返回了错误的数据类型: {type(result)}")
                return JsonResponse({
                    "success": False, 
                    "error": "内部服务错误，请稍后重试",
                    "debug_info": f"Expected dict, got {type(result)}"
                })
            
            # 添加手动输入信息
            result['login_detected'] = True
            result['session_source'] = 'manual_cookies'
            result['cookie_count'] = len(current_browser_cookies)
            
            logger.info(f"✅ 使用手动cookies，开始执行投递任务...")
            
            # 使用手动cookies启动投递任务
            search_result = service.start_job_search(
                platforms=platforms,
                keywords=keywords,
                cities=cities,
                expected_salary=expected_salary,
                say_hi=say_hi,
                use_ai=use_ai,
                send_img_resume=send_img_resume,
                user=request.user
            )
            
            # 合并结果
            if isinstance(search_result, dict):
                result.update(search_result)
                result['manual_cookies_used'] = True
                result['search_task_started'] = True
                logger.info(f"✅ 手动cookies投递任务启动成功")
            else:
                logger.error(f"❌ start_job_search返回了错误的数据类型: {type(search_result)}")
                result['search_task_started'] = False
                result['error'] = f"投递任务启动失败: 返回了错误的数据类型 {type(search_result)}"
            
            response = JsonResponse(result)
            logger.info(f"🔍 返回响应对象类型: {type(response)}")
            return response
        
        # 如果没有前端cookies或cookies为空，自动检测Boss直聘登录状态
        logger.info("🔄 没有前端cookies，自动检测Boss直聘登录状态...")
        login_status = service.get_login_status(user_id)
        
        # 检查登录状态检测是否成功
        if not login_status.get('success'):
            logger.warning(f"❌ 登录状态检测失败: {login_status.get('message', '未知错误')}")
            return JsonResponse({
                "success": False,
                "error": "登录状态检测失败，请稍后重试",
                "need_login": True,
                "login_status": login_status,
                "suggestion": "请检查网络连接后重试，或手动登录Boss直聘"
            })
        
        # 检查是否已登录
        if login_status.get('is_logged_in'):
            logger.info(f"✅ 检测到Boss直聘已登录，token: {login_status.get('token_info', {}).get('token', '')[:20]}...")
            
            # 检查是否是安全验证页面
            if login_status.get('security_verification'):
                logger.info("⚠️ 检测到安全验证页面，需要用户手动完成验证")
                return JsonResponse({
                    "success": False,
                    "error": "检测到Boss直聘安全验证页面，请手动完成滑块验证后重试",
                    "need_login": True,
                    "security_verification": True,
                    "login_status": login_status,
                    "suggestion": "请在浏览器中完成Boss直聘的安全验证（滑块验证），然后重新启动投递任务"
                })
            
            # 如果检测到登录状态，直接启动投递任务
            logger.info("🚀 检测到有效登录状态，直接启动投递任务...")
            result = service.start_job_search(
                platforms=platforms,
                keywords=keywords,
                cities=cities,
                expected_salary=expected_salary,
                say_hi=say_hi,
                use_ai=use_ai,
                send_img_resume=send_img_resume,
                user=request.user
            )
            
            # 确保result是字典类型
            if not isinstance(result, dict):
                logger.error(f"❌ start_job_search方法返回了错误的数据类型: {type(result)}")
                return JsonResponse({
                    "success": False, 
                    "error": "内部服务错误，请稍后重试",
                    "debug_info": f"Expected dict, got {type(result)}"
                })
            
            # 在结果中添加登录状态信息
            if result.get('success'):
                result['login_detected'] = True
                result['login_message'] = '自动检测到Boss直聘登录状态，已直接启动投递任务'
                result['login_status'] = login_status
                result['token_info'] = login_status.get('token_info', {})
                result['user_info'] = login_status.get('user_info', {})
                logger.info(f"✅ Boss直聘登录状态检测成功，置信度: {login_status.get('login_confidence', 0)}%")
            
            return JsonResponse(result)
        else:
            # 未检测到登录状态，返回需要登录的提示
            logger.warning(f"❌ 未检测到Boss直聘登录状态: {login_status.get('message', '未知错误')}")
            return JsonResponse({
                "success": False,
                "error": "未检测到Boss直聘登录状态，请先登录Boss直聘",
                "need_login": True,
                "login_status": login_status,
                "suggestion": "请先在浏览器中登录Boss直聘，然后重新启动投递任务"
            })
        
        # 如果不是Boss直聘平台，直接启动
        if 'boss' not in platforms:
            logger.info("🚀 非Boss直聘平台，直接启动投递任务...")
            result = service.start_job_search(
                platforms=platforms,
                keywords=keywords,
                cities=cities,
                expected_salary=expected_salary,
                say_hi=say_hi,
                use_ai=use_ai,
                send_img_resume=send_img_resume,
                user=request.user
            )
            
            # 确保result是字典类型
            if not isinstance(result, dict):
                logger.error(f"❌ 非Boss平台start_job_search方法返回了错误的数据类型: {type(result)}")
                return JsonResponse({
                    "success": False, 
                    "error": "内部服务错误，请稍后重试",
                    "debug_info": f"Expected dict, got {type(result)}"
                })
            
            return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"})
    except Exception as e:
        logger.error(f"启动AI投递失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"启动失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
def get_job_search_status_api(request):
    """获取投递状态API - 不需要登录的版本"""
    try:
        # 获取task_id参数
        task_id = request.GET.get('task_id')
        if not task_id:
            return JsonResponse({
                "success": False, 
                "error": "缺少task_id参数",
                "status": "error"
            })
        
        # 创建服务实例
        service = JobSearchService()
        
        # 尝试获取任务状态（使用默认用户）
        from django.contrib.auth.models import User
        default_user = User.objects.first()  # 使用第一个用户作为默认用户
        
        if default_user:
            status = service.get_job_search_status(default_user)
        else:
            # 如果没有用户，返回默认状态
            status = {
                "success": True,
                "status": "no_user",
                "message": "系统未初始化",
                "progress": 0
            }
        
        return JsonResponse(status)
    except Exception as e:
        logger.error(f"获取投递状态失败: {str(e)}")
        return JsonResponse({
            "success": False, 
            "error": f"获取状态失败: {str(e)}",
            "status": "error"
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def stop_job_search_api(request):
    """停止投递API"""
    try:
        service = JobSearchService()
        result = service.stop_job_search(request.user)
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"停止投递失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"停止失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
def boss_login_api(request):
    """Boss直聘登录API - 直接打开登录页面"""
    try:
        import json
        
        # 检查请求体是否为空
        if not request.body:
            logger.warning("Boss直聘登录API收到空请求体")
            return JsonResponse({
                "success": True,
                "message": "请手动打开Boss直聘登录页面进行扫码登录",
                "login_url": "https://login.zhipin.com/",
                "manual_login": True,
                "instructions": [
                    "1. 点击下方链接打开Boss直聘登录页面",
                    "2. 使用微信扫码登录",
                    "3. 登录成功后返回此页面",
                    "4. 点击'我已登录'按钮自动获取cookies并开始投递"
                ]
            })
        
        # 尝试解析JSON
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            logger.warning(f"Boss直聘登录API收到无效JSON: {e}")
            return JsonResponse({
                "success": True,
                "message": "请手动打开Boss直聘登录页面进行扫码登录",
                "login_url": "https://login.zhipin.com/",
                "manual_login": True,
                "instructions": [
                    "1. 点击下方链接打开Boss直聘登录页面",
                    "2. 使用微信扫码登录",
                    "3. 登录成功后返回此页面",
                    "4. 点击'我已登录'按钮自动获取cookies并开始投递"
                ]
            })
        
        method = data.get('method', 'qr')
        
        if method == 'qr':
            # 直接返回Boss直聘登录页面URL，让用户手动打开
            login_url = "https://login.zhipin.com/"
            
            return JsonResponse({
                "success": True,
                "message": "请手动打开Boss直聘登录页面进行扫码登录",
                "login_url": login_url,
                "manual_login": True,
                "instructions": [
                    "1. 点击下方链接打开Boss直聘登录页面",
                    "2. 使用微信扫码登录",
                    "3. 登录成功后返回此页面",
                    "4. 点击'我已登录'按钮自动获取cookies并开始投递"
                ]
            })
        else:
            return JsonResponse({
                "success": False,
                "error": "不支持的登录方式"
            })
        
    except Exception as e:
        logger.error(f"Boss直聘登录失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"登录失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
def start_job_search_with_playwright_api(request):
    """启动投递API - 新流程：自动启动Playwright并智能处理登录"""
    try:
        data = json.loads(request.body)
        
        # 解析参数
        platforms = data.get('platforms', ['boss'])
        keywords = data.get('keywords', [])
        cities = data.get('cities', [])
        expected_salary = data.get('expected_salary', [])
        say_hi = data.get('say_hi', '')
        use_ai = data.get('use_ai', True)
        send_img_resume = data.get('send_img_resume', False)
        
        logger.info(f"🎭 启动新流程投递请求: 平台={platforms}, 关键词={keywords}, 城市={cities}")
        
        # 创建服务实例
        service = JobSearchService()
        
        # 如果不是Boss直聘平台，直接启动
        if 'boss' not in platforms:
            logger.info("🚀 非Boss直聘平台，直接启动投递任务...")
            result = service.start_job_search(
                platforms=platforms,
                keywords=keywords,
                cities=cities,
                expected_salary=expected_salary,
                say_hi=say_hi,
                use_ai=use_ai,
                send_img_resume=send_img_resume,
                user=request.user
            )
            
            # 确保result是字典类型
            if not isinstance(result, dict):
                logger.error(f"❌ 服务方法返回了错误的数据类型: {type(result)}")
                return JsonResponse({
                    "success": False, 
                    "error": "服务内部错误",
                    "details": f"期望字典类型，实际得到: {type(result)}"
                }, status=500)
            
            return JsonResponse(result)
        
        # 新流程：自动启动Playwright并智能处理登录
        logger.info("🎭 启动新流程：自动启动Playwright并智能处理登录...")
        
        # 使用Playwright服务启动浏览器
        from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
        playwright_service = BossZhipinPlaywrightService(headless=False)  # 非无头模式，让用户看到浏览器
        
        try:
            # 初始化浏览器
            if not playwright_service._init_browser():
                logger.error("❌ Playwright浏览器初始化失败")
                return JsonResponse({
                    "success": False,
                    "error": "Playwright浏览器启动失败",
                    "message": "无法启动浏览器，请检查系统环境",
                    "debug_info": "浏览器初始化返回False"
                })
            
            # 使用重试机制访问主页
            main_url = "https://www.zhipin.com/"
            logger.info(f"🌐 访问Boss直聘主页: {main_url}")
            
            if not playwright_service._navigate_with_retry(main_url):
                logger.warning("主页访问失败，尝试访问登录页面")
                # 如果主页访问失败，直接访问登录页面
                login_url = "https://login.zhipin.com/"
                if not playwright_service._navigate_with_retry(login_url):
                    logger.error("登录页面访问也失败")
                    return JsonResponse({
                        "success": False,
                        "error": "无法访问Boss直聘网站",
                        "message": "请检查网络连接后重试"
                    })
            
            # 检查登录状态
            login_status = playwright_service._check_page_login_status(playwright_service.page)
            
            if login_status:
                logger.info("✅ 检测到已登录状态，直接开始投递...")
                
                # 提取cookies
                cookies = playwright_service.page.context.cookies()
                cookie_dict = {}
                for cookie in cookies:
                    if 'zhipin.com' in cookie.get('domain', ''):
                        cookie_dict[cookie['name']] = cookie['value']
                
                # 保存cookies到服务中
                playwright_service.set_cookies(cookie_dict)
                
                # 启动投递任务
                result = service.start_boss_search_with_cookies(
                    cookie_dict, keywords, cities, 
                    expected_salary, say_hi, use_ai, request.user
                )
                
                # 确保result是字典类型
                if not isinstance(result, dict):
                    logger.error(f"❌ 服务方法返回了错误的数据类型: {type(result)}")
                    return JsonResponse({
                        "success": False, 
                        "error": "服务内部错误",
                        "details": f"期望字典类型，实际得到: {type(result)}"
                    }, status=500)
                
                # 添加登录检测信息
                result['login_detected'] = True
                result['login_message'] = '检测到已登录状态，自动开始投递任务'
                result['cookie_count'] = len(cookie_dict)
                result['login_method'] = 'auto_detected'
                
                logger.info(f"✅ 自动检测登录状态投递完成")
                return JsonResponse(result)
                
            else:
                logger.info("❌ 未检测到登录状态，提示用户扫码登录...")
                
                # 导航到登录页面
                login_url = "https://www.zhipin.com/web/user/?ka=header-login"
                if not playwright_service._navigate_with_retry(login_url):
                    logger.warning("登录页面访问失败，使用备用URL")
                    # 使用备用登录URL
                    backup_url = "https://login.zhipin.com/"
                    if not playwright_service._navigate_with_retry(backup_url):
                        logger.error("备用登录页面访问也失败")
                        return JsonResponse({
                            "success": False,
                            "error": "无法访问登录页面",
                            "message": "请检查网络连接后重试"
                        })
                
                # 返回需要登录的响应，但保持浏览器打开
                # 不自动启动后台检测线程，等用户点击"我已登录"按钮后再启动
                logger.info("📋 浏览器已打开，等待用户登录后点击'我已登录'按钮...")
                
                return JsonResponse({
                    "success": False,
                    "need_login": True,
                    "login_detected": False,
                    "message": "请在打开的浏览器中扫码登录Boss直聘",
                    "login_url": login_url,
                    "playwright_active": True,
                    "auto_detection": True,
                    "instructions": [
                        "1. 浏览器已自动打开Boss直聘登录页面",
                        "2. 使用微信扫码登录",
                        "3. 登录成功后，系统将自动检测并开始投递",
                        "4. 如果5分钟内未自动开始，请点击'我已登录'按钮"
                    ],
                    "next_action": "wait_for_login"
                })
                
        except Exception as e:
            logger.error(f"❌ Playwright流程执行失败: {str(e)}")
            return JsonResponse({
                "success": False,
                "error": f"浏览器操作失败: {str(e)}",
                "message": "请重试或使用手动cookies方式"
            })
        finally:
            # 注意：这里不关闭浏览器，让用户可以看到登录页面
            # playwright_service._close_browser()
            pass
            
    except Exception as e:
        logger.error(f"启动投递失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"启动失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
def boss_manual_cookies_start_api(request):
    """Boss直聘手动输入cookies并开始投递API"""
    try:
        data = json.loads(request.body)
        
        # 获取投递参数
        platforms = data.get('platforms', ['boss'])
        keywords = data.get('keywords', [])
        cities = data.get('cities', [])
        expected_salary = data.get('expected_salary', [])
        say_hi = data.get('say_hi', '')
        use_ai = data.get('use_ai', True)
        send_img_resume = data.get('send_img_resume', False)
        
        # 获取手动输入的cookies
        manual_cookies = data.get('manual_cookies', {})
        
        if not manual_cookies:
            return JsonResponse({
                "success": False,
                "error": "请提供手动输入的cookies",
                "instructions": [
                    "1. 在Playwright浏览器中登录Boss直聘",
                    "2. 打开开发者工具 (F12)",
                    "3. 在Console中输入: document.cookie",
                    "4. 复制输出的cookie字符串",
                    "5. 将cookie字符串粘贴到manual_cookies字段中"
                ]
            })
        
        logger.info(f"用户手动输入了{len(manual_cookies)}个cookies，开始投递")
        
        # 创建服务实例
        service = JobSearchService()
        
        # 使用手动cookies启动投递
        result = service.start_boss_search_with_cookies(
            manual_cookies, keywords, cities, 
            expected_salary, say_hi, use_ai, request.user
        )
        
        # 确保result是字典类型
        if not isinstance(result, dict):
            logger.error(f"❌ 服务方法返回了错误的数据类型: {type(result)}")
            return JsonResponse({
                "success": False, 
                "error": "服务内部错误",
                "details": f"期望字典类型，实际得到: {type(result)}"
            }, status=500)
        
        # 添加手动输入信息
        result['login_detected'] = True
        result['login_message'] = '使用手动输入的cookies开始投递任务'
        result['cookie_count'] = len(manual_cookies)
        result['login_method'] = 'manual_cookies'
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"手动cookies投递失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": f"投递失败: {str(e)}"
        })


@csrf_exempt
@require_http_methods(["POST"])
def boss_auto_login_and_start_api(request):
    """Boss直聘自动登录检测并开始投递API"""
    try:
        data = json.loads(request.body)
        
        # 获取投递参数
        platforms = data.get('platforms', ['boss'])
        keywords = data.get('keywords', [])
        cities = data.get('cities', [])
        expected_salary = data.get('expected_salary', [])
        say_hi = data.get('say_hi', '')
        use_ai = data.get('use_ai', True)
        send_img_resume = data.get('send_img_resume', False)
        
        logger.info(f"用户点击'我已登录'，开始自动检测登录状态并投递")
        
        # 创建服务实例
        service = JobSearchService()
        
        # 使用Playwright检测登录状态并获取cookies
        from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
        
        logger.info("🔍 尝试连接到现有的Playwright浏览器实例...")
        
        # 尝试连接到现有的浏览器实例（如果存在）
        try:
            # 方法1：尝试连接到现有的Chrome实例
            playwright_service = BossZhipinPlaywrightService()
            
            # 尝试连接到现有的浏览器
            if hasattr(playwright_service, '_connect_to_existing_browser'):
                connected = playwright_service._connect_to_existing_browser()
                if connected:
                    logger.info("✅ 成功连接到现有浏览器实例")
                else:
                    logger.info("❌ 无法连接到现有浏览器实例，创建新实例")
                    playwright_service = BossZhipinPlaywrightService(headless=False)
            else:
                logger.info("🔧 创建新的Playwright实例")
                playwright_service = BossZhipinPlaywrightService(headless=False)
                
        except Exception as e:
            logger.warning(f"⚠️ 连接现有浏览器失败: {str(e)}，创建新实例")
            playwright_service = BossZhipinPlaywrightService(headless=False)
        
        # 启动后台持续检测登录状态（参考Java项目的while循环持续检测模式）
        logger.info("🔄 用户点击'我已登录'，启动后台持续检测登录状态（参考Java项目模式）...")
        
        import threading
        import time
        
        def auto_detect_login():
            """后台自动检测登录状态 - 参考Java项目的while循环持续检测模式"""
            logger.info("🔄 开始后台持续检测登录状态（参考Java项目模式）...")
            logger.info(f"🔧 检测参数: 最大等待时间={10*60}秒, 检测间隔={2}秒")
            
            # 参考Java项目：使用while循环持续检测，直到登录成功或超时
            login_detected = False
            start_time = time.time()
            max_wait_time = 10 * 60  # 10分钟超时，与Java项目一致
            check_interval = 2  # 每2秒检查一次，与Java项目一致
            
            logger.info(f"🔧 检测开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
            
            while not login_detected:
                try:
                    # 检查是否超时
                    elapsed_time = time.time() - start_time
                    if elapsed_time >= max_wait_time:
                        logger.error("⏰ 超过10分钟未完成登录，自动检测结束（参考Java项目超时机制）")
                        break
                    
                    attempt_count = int(elapsed_time / check_interval) + 1
                    logger.info(f"🔄 第{attempt_count}次持续检测登录状态... (已等待 {elapsed_time:.1f}秒)")
                    
                    # 尝试使用现有的Playwright浏览器实例
                    logger.info(f"🔍 检查浏览器实例: hasattr(page)={hasattr(playwright_service, 'page')}")
                    if hasattr(playwright_service, 'page') and playwright_service.page:
                        logger.info(f"🔍 浏览器实例存在，开始检测页面状态...")
                        try:
                            # 参考Java项目：检查关键元素来判断登录状态
                            # Java项目检查: div.job-list-container
                            page = playwright_service.page
                            logger.info(f"🔍 页面对象获取成功: {type(page)}")
                            
                            # 获取页面基本信息
                            try:
                                current_url = page.url
                                page_title = page.title()
                                logger.info(f"🔍 页面信息: URL={current_url}, 标题={page_title}")
                            except Exception as e:
                                logger.warning(f"⚠️ 获取页面信息失败: {str(e)}")
                            
                            # 方法1：检查职位列表容器（与Java项目一致）
                            try:
                                logger.info("🔍 方法1: 检查职位列表容器...")
                                job_list_container = page.locator("div.job-list-container")
                                container_count = job_list_container.count()
                                logger.info(f"🔍 职位列表容器数量: {container_count}")
                                
                                if container_count > 0:
                                    is_visible = job_list_container.is_visible()
                                    logger.info(f"🔍 职位列表容器可见性: {is_visible}")
                                    if is_visible:
                                        logger.info("✅ 检测到职位列表容器，用户已登录！")
                                        login_detected = True
                                        break
                                else:
                                    logger.info("❌ 未找到职位列表容器")
                            except Exception as e:
                                logger.warning(f"⚠️ 检查职位列表容器失败: {str(e)}")
                            
                            # 方法2：检查登录按钮是否消失
                            if not login_detected:
                                try:
                                    logger.info("🔍 方法2: 检查登录按钮是否消失...")
                                    login_btn = page.locator("text=登录/注册, text=立即登录, text=扫码登录")
                                    login_btn_count = login_btn.count()
                                    logger.info(f"🔍 登录按钮数量: {login_btn_count}")
                                    
                                    if login_btn_count == 0:
                                        logger.info("✅ 登录按钮已消失，用户已登录！")
                                        login_detected = True
                                        break
                                    else:
                                        logger.info("❌ 发现登录按钮，用户未登录")
                                except Exception as e:
                                    logger.warning(f"⚠️ 检查登录按钮失败: {str(e)}")
                            
                            # 方法3：使用现有的登录状态检查方法
                            if not login_detected:
                                try:
                                    logger.info("🔍 方法3: 使用现有登录状态检查方法...")
                                    login_status = playwright_service._check_page_login_status(page)
                                    logger.info(f"🔍 现有方法检测结果: {login_status}")
                                    
                                    if login_status:
                                        logger.info("✅ 使用现有方法检测到登录状态！")
                                        login_detected = True
                                        break
                                    else:
                                        logger.info("❌ 现有方法未检测到登录状态")
                                except Exception as e:
                                    logger.warning(f"⚠️ 使用现有方法检测失败: {str(e)}")
                            
                            logger.info(f"❌ 第{int(elapsed_time/check_interval) + 1}次检测：仍未登录")
                            
                        except Exception as e:
                            logger.warning(f"⚠️ 页面检测异常: {str(e)}")
                    else:
                        logger.warning("⚠️ 没有找到浏览器实例，跳过本次检测")
                    
                    # 等待下次检测
                    logger.info(f"⏳ 等待 {check_interval} 秒后进行下次检测...")
                    time.sleep(check_interval)
                    
                except Exception as e:
                    logger.error(f"❌ 持续检测异常: {str(e)}")
                    time.sleep(check_interval)
            
            # 如果检测到登录，启动投递任务
            if login_detected:
                try:
                    logger.info("🎉 检测到登录成功，开始启动投递任务...")
                    logger.info(f"🔧 投递参数: keywords={keywords}, cities={cities}, expected_salary={expected_salary}")
                    
                    # 提取cookies
                    logger.info("🍪 开始提取cookies...")
                    cookies = playwright_service.page.context.cookies()
                    cookie_dict = {}
                    for cookie in cookies:
                        if 'zhipin.com' in cookie.get('domain', ''):
                            cookie_dict[cookie['name']] = cookie['value']
                    
                    logger.info(f"🍪 提取到 {len(cookie_dict)} 个cookies: {list(cookie_dict.keys())}")
                    
                    # 保存cookies到服务中
                    logger.info("💾 保存cookies到服务中...")
                    playwright_service.set_cookies(cookie_dict)
                    
                    # 启动投递任务
                    logger.info("🚀 启动投递任务...")
                    result = service.start_job_search(
                        platforms=platforms,
                        keywords=keywords,
                        cities=cities,
                        expected_salary=expected_salary,
                        say_hi=say_hi,
                        use_ai=use_ai,
                        send_img_resume=send_img_resume,
                        user=request.user if request.user.is_authenticated else None
                    )
                    
                    logger.info(f"✅ 自动检测登录状态投递完成: {result}")
                    
                except Exception as e:
                    logger.error(f"❌ 启动投递任务失败: {str(e)}")
                    logger.error(f"❌ 错误详情: {str(e)}", exc_info=True)
            else:
                logger.info("⏰ 自动检测登录状态超时，请手动点击'我已登录'按钮")
        
        # 启动后台检测线程
        detection_thread = threading.Thread(target=auto_detect_login, daemon=True)
        detection_thread.start()
        
        # 立即返回响应，告诉前端正在检测中
        return JsonResponse({
            "success": False,
            "need_login": True,
            "login_detected": False,
            "message": "正在持续检测登录状态，请稍候...",
            "playwright_active": True,
            "instructions": [
                "1. 系统正在持续检测您的登录状态",
                "2. 如果已登录，系统将自动开始投递任务",
                "3. 如果10分钟内未检测到登录，请重新点击'我已登录'按钮"
            ]
        })
        
    except Exception as e:
        logger.error(f"自动登录检测失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": f"检测失败: {str(e)}"
        })


@csrf_exempt
@require_http_methods(["GET"])
def boss_login_status_api(request):
    """Boss直聘登录状态API - 使用Playwright替代Selenium"""
    try:
        from apps.tools.services.job_search_service import JobSearchService
        
        job_service = JobSearchService()
        
        # 使用Playwright检查登录状态
        result = job_service.check_qr_login_status(1)  # 使用默认用户ID
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"检查Boss直聘登录状态失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"检查状态失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def boss_token_login_api(request):
    """Boss直聘Token登录API"""
    try:
        import json
        
        data = json.loads(request.body)
        token = data.get('token', '').strip()
        
        if not token:
            return JsonResponse({"success": False, "error": "Token不能为空"})
        
        from apps.tools.services.job_search_service import JobSearchService
        from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
        
        job_service = JobSearchService()
        
        # 使用Playwright验证token
        playwright_service = BossZhipinPlaywrightService(headless=True)
        result = playwright_service.check_login_status(request.user.id)
        
        if result.get('success') and result.get('is_logged_in'):
            # 保存token到文件
            token_file = os.path.join(settings.BASE_DIR, 'get_jobs_integration', f'boss_token_{request.user.id}.json')
            os.makedirs(os.path.dirname(token_file), exist_ok=True)
            
            token_data = {
                'token': token,
                'login_time': time.time(),
                'user_id': request.user.id
            }
            
            with open(token_file, 'w', encoding='utf-8') as f:
                json.dump(token_data, f, ensure_ascii=False, indent=2)
            
            return JsonResponse({
                "success": True,
                "message": "Token登录成功",
                "token": token
            })
        else:
            return JsonResponse({
                "success": False,
                "error": "Token验证失败，请检查token有效性"
            })
        
    except Exception as e:
        logger.error(f"Boss直聘Token登录失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"Token登录失败: {str(e)}"})

@csrf_exempt
@require_http_methods(["POST"])
def boss_phone_login_api(request):
    """Boss直聘手机号登录API - 已禁用"""
    return JsonResponse({
        "success": False,
        "error": "手机号登录功能已禁用，请使用cookies登录方式",
        "disabled": True,
        "alternative": "请使用浏览器登录Boss直聘后，复制cookies进行登录"
    })


@csrf_exempt
@require_http_methods(["POST"])
def test_cookie_execution_api(request):
    """测试Cookie执行API - 使用用户提供的Cookie直接测试"""
    try:
        # 用户提供的Cookie数据
        test_cookies = {
            "__a": "52114796.1759162090..1759162090.4.1.4.4",
            "__c": "1759162090", 
            "__g": "-",
            "__l": "l=%2Fwww.zhipin.com%2F&r=&g=&s=3&friend_source=0",
            "__zp_stoken__": "0138fRE%2FDr8OGwpbDhjs0HQoUFhVNNzpOK8KMTkUyQzlDRU5FO0FFTk0ZRzXCsMK6KMKWw7xZw4p9OChORU5HRThFOU0YTkHDhzhENMOAw4YpwovDt2LDlgt3HcK7CnTDhR3Ds8OGC0XDjikrEcOFQTpORxLDjcK6w483w4bDgcODVsK6wpTDjTpGPRIrRhFaFBZGRlRLbAhUYEpmYlAVU0hTNEc6T0UWw5nDujVHCAkUHxQKCxYdFhwdEB4VHx4TCBMJCBUeFTE4wqHDgcKKwo%2FEsMSow7PEpMKnwq7Ci8K0xI7Cq8KuU8K4wqrEh8KnwpdQU2DCulHDjmTCmsK8w4TDg2zCuGxeYcOAV2JJXUhpw4JSVG7DjmDChVAQEhAXH0Yew5zEhsOL",
            "ab_guid": "e4b98c29-f308-4580-95f3-bd10b4405ee1",
            "bst": "V2RNgvF-X-3F5rVtRuyR0aKSKy7DrWxi8~|RNgvF-X-3F5rVtRuyR0aKSKy7DrQwCw~",
            "Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a": "1759162121",
            "Hm_lvt_194df3105ad7148dcf2b98a91b5e727a": "1759162092",
            "HMACCOUNT": "4D95B28B84CF3F01",
            "wbg": "0",
            "wt2": "DpBNkl9yMP6krq_JR0RiMD75j0zSl0dYyBGhzfreqBWQOs08OBcGACnMuYvqNl2eOAh0pDq5hHVkCmwoxLauyDA~~",
            "zp_at": "MfIJfyhHZlJoJFSORnjJY7UtLIB6W3xlahHnN8BibaY~"
        }
        
        logger.info("🧪 开始测试Cookie执行...")
        
        # 创建服务实例
        service = JobSearchService()
        
        # 使用Playwright服务
        from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
        playwright_service = BossZhipinPlaywrightService(headless=False)
        
        test_logs = []
        
        try:
            # 步骤1: 初始化浏览器
            logger.info("🧪 步骤1: 初始化Playwright浏览器...")
            test_logs.append("🧪 步骤1: 初始化Playwright浏览器...")
            
            if not playwright_service._init_browser():
                logger.error("❌ Playwright浏览器初始化失败")
                test_logs.append("❌ Playwright浏览器初始化失败")
                return JsonResponse({
                    "success": False,
                    "error": "Playwright浏览器启动失败",
                    "test_logs": test_logs
                })
            
            test_logs.append("✅ Playwright浏览器初始化成功")
            
            # 步骤2: 设置Cookie
            logger.info("🧪 步骤2: 设置测试Cookie...")
            test_logs.append("🧪 步骤2: 设置测试Cookie...")
            test_logs.append(f"🧪 Cookie数量: {len(test_cookies)}")
            test_logs.append(f"🧪 Cookie名称: {list(test_cookies.keys())}")
            
            # 设置Cookie到浏览器
            playwright_service.set_cookies(test_cookies)
            test_logs.append("✅ Cookie设置完成")
            
            # 步骤3: 访问Boss直聘主页
            logger.info("🧪 步骤3: 访问Boss直聘主页...")
            test_logs.append("🧪 步骤3: 访问Boss直聘主页...")
            
            main_url = "https://www.zhipin.com/"
            if not playwright_service._navigate_with_retry(main_url):
                test_logs.append("❌ 主页访问失败")
                return JsonResponse({
                    "success": False,
                    "error": "无法访问Boss直聘主页",
                    "test_logs": test_logs
                })
            
            current_url = playwright_service.page.url
            page_title = playwright_service.page.title()
            
            test_logs.append(f"✅ 主页访问成功")
            test_logs.append(f"🧪 当前URL: {current_url}")
            test_logs.append(f"🧪 页面标题: {page_title}")
            
            # 步骤4: 检查登录状态
            logger.info("🧪 步骤4: 检查登录状态...")
            test_logs.append("🧪 步骤4: 检查登录状态...")
            
            # 详细检查页面元素
            login_elements = [
                'text="登录/注册"',
                'text="立即登录"', 
                'text="扫码登录"',
                '.user-name',
                '.geek-name',
                'button:has-text("立即沟通")',
                'button:has-text("投递简历")',
                'div.job-list-container'
            ]
            
            for element in login_elements:
                try:
                    found_element = playwright_service.page.query_selector(element)
                    if found_element:
                        is_visible = found_element.is_visible()
                        test_logs.append(f"🧪 找到元素 '{element}': 可见={is_visible}")
                    else:
                        test_logs.append(f"🧪 未找到元素 '{element}'")
                except Exception as e:
                    test_logs.append(f"🧪 检查元素 '{element}' 失败: {str(e)}")
            
            # 使用登录状态检查方法
            login_status = playwright_service._check_page_login_status(playwright_service.page)
            test_logs.append(f"🧪 登录状态检查结果: {login_status}")
            
            if login_status:
                logger.info("✅ Cookie测试成功：检测到已登录状态")
                test_logs.append("✅ Cookie测试成功：检测到已登录状态")
                
                # 步骤5: 尝试启动投递任务
                logger.info("🧪 步骤5: 尝试启动投递任务...")
                test_logs.append("🧪 步骤5: 尝试启动投递任务...")
                
                # 使用简单的测试参数
                keywords = ["Python"]
                cities = ["北京"]
                expected_salary = [15000]
                say_hi = "您好，我有相关经验，希望应聘这个岗位"
                use_ai = True
                
                result = service.start_boss_search_with_cookies(
                    test_cookies, keywords, cities, 
                    expected_salary, say_hi, use_ai, request.user
                )
                
                test_logs.append(f"🧪 投递任务结果: {result}")
                
                if isinstance(result, dict) and result.get('success'):
                    test_logs.append("✅ 投递任务启动成功！")
                    return JsonResponse({
                        "success": True,
                        "message": "Cookie测试完全成功！登录状态正常，投递任务已启动",
                        "test_logs": test_logs,
                        "task_id": result.get('task_id'),
                        "login_detected": True,
                        "delivery_started": True
                    })
                else:
                    test_logs.append("⚠️ 投递任务启动失败")
                    return JsonResponse({
                        "success": False,
                        "error": "Cookie有效但投递任务启动失败",
                        "test_logs": test_logs,
                        "login_detected": True,
                        "delivery_started": False,
                        "delivery_error": str(result) if not isinstance(result, dict) else result.get('error', 'Unknown error')
                    })
            else:
                logger.warning("⚠️ Cookie测试失败：未检测到登录状态")
                test_logs.append("⚠️ Cookie测试失败：未检测到登录状态")
                
                # 检查页面内容
                try:
                    page_content = playwright_service.page.content()
                    test_logs.append(f"🧪 页面内容长度: {len(page_content)} 字符")
                    
                    # 检查是否包含登录相关文本
                    if "登录" in page_content:
                        test_logs.append("🧪 页面包含'登录'文本")
                    if "注册" in page_content:
                        test_logs.append("🧪 页面包含'注册'文本")
                    if "立即沟通" in page_content:
                        test_logs.append("🧪 页面包含'立即沟通'文本")
                        
                except Exception as e:
                    test_logs.append(f"❌ 检查页面内容失败: {str(e)}")
                
                return JsonResponse({
                    "success": False,
                    "error": "Cookie无效或已过期",
                    "test_logs": test_logs,
                    "login_detected": False,
                    "possible_causes": [
                        "Cookie已过期",
                        "Cookie格式不正确", 
                        "Boss直聘更新了验证机制",
                        "需要额外的验证步骤"
                    ]
                })
                
        except Exception as e:
            logger.error(f"❌ Cookie测试执行失败: {str(e)}")
            test_logs.append(f"❌ Cookie测试执行失败: {str(e)}")
            return JsonResponse({
                "success": False,
                "error": f"Cookie测试失败: {str(e)}",
                "test_logs": test_logs
            })
        finally:
            # 注意：这里不关闭浏览器，让用户可以看到结果
            pass
            
    except Exception as e:
        logger.error(f"Cookie测试启动失败: {str(e)}")
        return JsonResponse({
            "success": False, 
            "error": f"Cookie测试启动失败: {str(e)}",
            "test_logs": [f"❌ Cookie测试启动失败: {str(e)}"]
        })
    """调试Playwright登录流程API - 详细日志输出"""
    try:
        data = json.loads(request.body)
        
        # 解析参数
        platforms = data.get('platforms', ['boss'])
        keywords = data.get('keywords', [])
        cities = data.get('cities', [])
        expected_salary = data.get('expected_salary', [])
        say_hi = data.get('say_hi', '')
        use_ai = data.get('use_ai', True)
        send_img_resume = data.get('send_img_resume', False)
        
        logger.info(f"🐛 调试模式启动: 平台={platforms}, 关键词={keywords}, 城市={cities}")
        
        # 创建服务实例
        service = JobSearchService()
        
        # 使用Playwright服务启动浏览器
        from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
        playwright_service = BossZhipinPlaywrightService(headless=False)  # 非无头模式
        
        debug_logs = []
        
        try:
            # 初始化浏览器
            logger.info("🐛 步骤1: 初始化Playwright浏览器...")
            debug_logs.append("🐛 步骤1: 初始化Playwright浏览器...")
            
            if not playwright_service._init_browser():
                logger.error("❌ Playwright浏览器初始化失败")
                debug_logs.append("❌ Playwright浏览器初始化失败")
                return JsonResponse({
                    "success": False,
                    "error": "Playwright浏览器启动失败",
                    "debug_logs": debug_logs
                })
            
            debug_logs.append("✅ Playwright浏览器初始化成功")
            
            # 尝试从文件加载cookies
            logger.info("🐛 步骤1.5: 尝试从文件加载cookies...")
            debug_logs.append("🐛 步骤1.5: 尝试从文件加载cookies...")
            
            cookie_loaded = playwright_service.load_cookies_from_file()
            if cookie_loaded:
                debug_logs.append("✅ 从文件成功加载cookies")
            else:
                debug_logs.append("ℹ️ 未找到有效的cookie文件，需要重新登录")
            
            # 访问Boss直聘职位页面（基于深度调试的发现）
            job_url = "https://www.zhipin.com/web/geek/jobs"
            logger.info(f"🐛 步骤2: 访问Boss直聘职位页面: {job_url}")
            debug_logs.append(f"🐛 步骤2: 访问Boss直聘职位页面: {job_url}")
            
            if not playwright_service._navigate_with_retry(job_url):
                logger.warning("职位页面访问失败，尝试访问主页")
                debug_logs.append("⚠️ 职位页面访问失败，尝试访问主页")
                # 如果职位页面访问失败，访问主页
                main_url = "https://www.zhipin.com/"
                if not playwright_service._navigate_with_retry(main_url):
                    debug_logs.append("❌ 主页访问也失败")
                    return JsonResponse({
                        "success": False,
                        "error": "无法访问Boss直聘网站",
                        "debug_logs": debug_logs
                    })
                debug_logs.append(f"✅ 主页访问成功: {main_url}")
            else:
                debug_logs.append("✅ 职位页面访问成功")
            
            # 检查当前页面URL
            current_url = playwright_service.page.url
            logger.info(f"🐛 当前页面URL: {current_url}")
            debug_logs.append(f"🐛 当前页面URL: {current_url}")
            
            # 检查页面标题
            page_title = playwright_service.page.title()
            logger.info(f"🐛 页面标题: {page_title}")
            debug_logs.append(f"🐛 页面标题: {page_title}")
            
            # 详细检查登录状态
            logger.info("🐛 步骤3: 详细检查登录状态...")
            debug_logs.append("🐛 步骤3: 详细检查登录状态...")
            
            # 检查页面内容
            try:
                page_content = playwright_service.page.content()
                debug_logs.append(f"🐛 页面内容长度: {len(page_content)} 字符")
                
                # 检查关键元素
                login_elements = [
                    'text="登录/注册"',
                    'text="立即登录"',
                    'text="扫码登录"',
                    '.login-btn',
                    '.user-name',
                    '.geek-name',
                    'button:has-text("立即沟通")',
                    'button:has-text("投递简历")',
                    'div.job-list-container'  # 关键指标
                ]
                
                for element in login_elements:
                    try:
                        found_element = playwright_service.page.query_selector(element)
                        if found_element:
                            is_visible = found_element.is_visible()
                            debug_logs.append(f"🐛 找到元素 '{element}': 可见={is_visible}")
                        else:
                            debug_logs.append(f"🐛 未找到元素 '{element}'")
                    except Exception as e:
                        debug_logs.append(f"🐛 检查元素 '{element}' 失败: {str(e)}")
                        
            except Exception as e:
                debug_logs.append(f"❌ 检查页面内容失败: {str(e)}")
            
            # 使用现有的登录状态检查方法
            login_status = playwright_service._check_page_login_status(playwright_service.page)
            logger.info(f"🐛 登录状态检查结果: {login_status}")
            debug_logs.append(f"🐛 登录状态检查结果: {login_status}")
            
            if login_status:
                logger.info("✅ 检测到已登录状态，开始投递流程...")
                debug_logs.append("✅ 检测到已登录状态，开始投递流程...")
                
                # 提取cookies
                cookies = playwright_service.page.context.cookies()
                cookie_dict = {}
                for cookie in cookies:
                    if 'zhipin.com' in cookie.get('domain', ''):
                        cookie_dict[cookie['name']] = cookie['value']
                
                debug_logs.append(f"🐛 提取到 {len(cookie_dict)} 个cookies")
                debug_logs.append(f"🐛 Cookie名称: {list(cookie_dict.keys())}")
                
                # 保存cookies到服务中
                playwright_service.set_cookies(cookie_dict)
                debug_logs.append("✅ Cookies保存成功")
                
                # 启动投递任务
                logger.info("🐛 步骤4: 启动投递任务...")
                debug_logs.append("🐛 步骤4: 启动投递任务...")
                
                result = service.start_boss_search_with_cookies(
                    cookie_dict, keywords, cities, 
                    expected_salary, say_hi, use_ai, request.user
                )
                
                debug_logs.append(f"🐛 投递任务结果: {result}")
                
                # 确保result是字典类型
                if not isinstance(result, dict):
                    logger.error(f"❌ 服务方法返回了错误的数据类型: {type(result)}")
                    debug_logs.append(f"❌ 服务方法返回了错误的数据类型: {type(result)}")
                    return JsonResponse({
                        "success": False, 
                        "error": "服务内部错误",
                        "debug_logs": debug_logs
                    })
                
                # 添加调试信息
                result['debug_logs'] = debug_logs
                result['login_detected'] = True
                result['login_message'] = '调试模式：检测到已登录状态，自动开始投递任务'
                result['cookie_count'] = len(cookie_dict)
                result['login_method'] = 'debug_auto_detected'
                
                logger.info(f"✅ 调试模式投递完成")
                return JsonResponse(result)
                
            else:
                logger.info("❌ 未检测到登录状态，需要手动登录")
                debug_logs.append("❌ 未检测到登录状态，需要手动登录")
                
                # 导航到登录页面
                login_url = "https://www.zhipin.com/web/user/?ka=header-login"
                if not playwright_service._navigate_with_retry(login_url):
                    logger.warning("登录页面访问失败，使用备用URL")
                    debug_logs.append("⚠️ 登录页面访问失败，使用备用URL")
                    # 使用备用登录URL
                    backup_url = "https://login.zhipin.com/"
                    if not playwright_service._navigate_with_retry(backup_url):
                        debug_logs.append("❌ 备用登录页面访问也失败")
                        return JsonResponse({
                            "success": False,
                            "error": "无法访问登录页面",
                            "debug_logs": debug_logs
                        })
                    debug_logs.append(f"✅ 使用备用登录URL: {backup_url}")
                else:
                    debug_logs.append(f"✅ 导航到登录页面: {login_url}")
                
                return JsonResponse({
                    "success": False,
                    "need_login": True,
                    "login_detected": False,
                    "message": "调试模式：请在打开的浏览器中扫码登录Boss直聘",
                    "login_url": login_url,
                    "playwright_active": True,
                    "debug_mode": True,
                    "debug_logs": debug_logs,
                    "instructions": [
                        "1. 浏览器已自动打开Boss直聘登录页面（调试模式）",
                        "2. 使用微信扫码登录",
                        "3. 登录成功后，点击'我已登录'按钮继续",
                        "4. 系统将显示详细的调试日志",
                        "5. Cookies将自动保存，下次无需重新登录",
                        "6. 如果登录后没有自动跳转，请手动刷新页面"
                    ],
                    "next_action": "wait_for_login",
                    "troubleshooting": [
                        "如果登录后没有自动执行，可能的原因：",
                        "- 登录状态检测失败，请检查页面是否真的登录成功",
                        "- 页面没有跳转到职位列表页面",
                        "- Cookie没有正确保存",
                        "- 网络延迟导致页面加载不完整",
                        "建议：登录后手动刷新页面，然后点击'我已登录'"
                    ]
                })
                
        except Exception as e:
            logger.error(f"❌ 调试模式执行失败: {str(e)}")
            debug_logs.append(f"❌ 调试模式执行失败: {str(e)}")
            return JsonResponse({
                "success": False,
                "error": f"调试模式失败: {str(e)}",
                "debug_logs": debug_logs
            })
        finally:
            # 注意：这里不关闭浏览器，让用户可以看到登录页面
            pass
            
    except Exception as e:
        logger.error(f"调试模式启动失败: {str(e)}")
        return JsonResponse({
            "success": False, 
            "error": f"调试模式启动失败: {str(e)}",
            "debug_logs": [f"❌ 调试模式启动失败: {str(e)}"]
        })


@csrf_exempt
@require_http_methods(["POST"])
def boss_send_sms_api(request):
    """Boss直聘发送短信验证码API - 已禁用"""
    return JsonResponse({
        "success": False,
        "error": "手机号登录功能已禁用，请使用cookies登录方式",
        "disabled": True,
        "alternative": "请使用浏览器登录Boss直聘后，复制cookies进行登录"
    })


@csrf_exempt
@require_http_methods(["GET"])
def check_login_status_polling_api(request):
    """检查登录状态轮询API - 用于前端轮询检查登录状态"""
    try:
        from apps.tools.services.boss_zhipin_playwright import BossZhipinPlaywrightService
        
        logger.info("🔍 前端轮询检查登录状态...")
        logger.info(f"🔧 轮询请求时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 尝试连接到现有的Playwright浏览器实例
        try:
            # 创建新的Playwright服务实例，但尝试连接到现有浏览器
            logger.info("🔧 创建Playwright服务实例...")
            playwright_service = BossZhipinPlaywrightService(headless=False)
            
            # 尝试初始化浏览器（如果还没有的话）
            logger.info(f"🔍 检查浏览器实例状态: hasattr(page)={hasattr(playwright_service, 'page')}")
            if not hasattr(playwright_service, 'page') or not playwright_service.page:
                logger.info("🔧 尝试初始化浏览器实例...")
                if playwright_service._init_browser():
                    logger.info("✅ 浏览器实例初始化成功")
                else:
                    logger.warning("⚠️ 浏览器实例初始化失败")
                    return JsonResponse({
                        "success": False,
                        "is_logged_in": False,
                        "error": "无法初始化浏览器实例",
                        "message": "请重新启动投递流程",
                        "next_action": "restart_process"
                    })
            else:
                logger.info("✅ 浏览器实例已存在")
            
            # 检查是否有活跃的浏览器实例
            if hasattr(playwright_service, 'page') and playwright_service.page:
                page = playwright_service.page
                
                # 使用多种方法检测登录状态
                login_detected = False
                detection_method = ""
                debug_info = []
                
                # 获取当前页面信息
                try:
                    current_url = page.url
                    page_title = page.title()
                    debug_info.append(f"当前URL: {current_url}")
                    debug_info.append(f"页面标题: {page_title}")
                    logger.info(f"🔍 轮询检测页面信息: URL={current_url}, 标题={page_title}")
                except Exception as e:
                    debug_info.append(f"获取页面信息失败: {str(e)}")
                
                # 方法1：检查职位列表容器（与Java项目一致）
                try:
                    job_list_container = page.locator("div.job-list-container")
                    if job_list_container.count() > 0 and job_list_container.is_visible():
                        login_detected = True
                        detection_method = "job_list_container"
                        logger.info("✅ 轮询检测：发现职位列表容器")
                        debug_info.append("✅ 发现职位列表容器")
                    else:
                        debug_info.append("❌ 未发现职位列表容器")
                except Exception as e:
                    debug_info.append(f"检查职位列表容器失败: {str(e)}")
                
                # 方法2：检查登录按钮是否消失
                if not login_detected:
                    try:
                        login_btn = page.locator("text=登录/注册, text=立即登录, text=扫码登录")
                        login_btn_count = login_btn.count()
                        if login_btn_count == 0:
                            login_detected = True
                            detection_method = "login_button_disappeared"
                            logger.info("✅ 轮询检测：登录按钮已消失")
                            debug_info.append("✅ 登录按钮已消失")
                        else:
                            debug_info.append(f"❌ 发现 {login_btn_count} 个登录按钮")
                    except Exception as e:
                        debug_info.append(f"检查登录按钮失败: {str(e)}")
                
                # 方法3：检查URL是否包含登录后特征
                if not login_detected:
                    try:
                        if any(path in current_url for path in ['/web/geek/jobs', '/web/geek/chat', '/web/geek/profile', '/web/geek/job']):
                            login_detected = True
                            detection_method = "url_pattern"
                            logger.info("✅ 轮询检测：通过URL模式检测到登录")
                            debug_info.append("✅ 通过URL模式检测到登录")
                        else:
                            debug_info.append("❌ URL不包含登录后特征")
                    except Exception as e:
                        debug_info.append(f"检查URL模式失败: {str(e)}")
                
                # 方法4：使用现有的登录状态检查方法
                if not login_detected:
                    try:
                        login_status = playwright_service._check_page_login_status(page)
                        if login_status:
                            login_detected = True
                            detection_method = "existing_method"
                            logger.info("✅ 轮询检测：使用现有方法检测到登录")
                            debug_info.append("✅ 使用现有方法检测到登录")
                        else:
                            debug_info.append("❌ 现有方法未检测到登录")
                    except Exception as e:
                        debug_info.append(f"使用现有方法检测失败: {str(e)}")
                
                # 方法5：检查页面内容关键词
                if not login_detected:
                    try:
                        page_content = page.content().lower()
                        login_keywords = ['立即沟通', '投递简历', '我的简历', '我的投递', '个人中心', '退出', 'logout']
                        keyword_count = sum(1 for keyword in login_keywords if keyword in page_content)
                        if keyword_count >= 2:
                            login_detected = True
                            detection_method = "content_keywords"
                            logger.info(f"✅ 轮询检测：通过页面内容检测到登录 (匹配{keyword_count}个关键词)")
                            debug_info.append(f"✅ 通过页面内容检测到登录 (匹配{keyword_count}个关键词)")
                        else:
                            debug_info.append(f"❌ 页面内容只匹配 {keyword_count} 个关键词")
                    except Exception as e:
                        debug_info.append(f"检查页面内容失败: {str(e)}")
                
                if login_detected:
                    # 提取cookies
                    cookies = page.context.cookies()
                    cookie_dict = {}
                    for cookie in cookies:
                        if 'zhipin.com' in cookie.get('domain', ''):
                            cookie_dict[cookie['name']] = cookie['value']
                    
                    logger.info(f"✅ 轮询检测成功：检测到登录状态，提取到 {len(cookie_dict)} 个cookies")
                    
                    return JsonResponse({
                        "success": True,
                        "is_logged_in": True,
                        "detection_method": detection_method,
                        "cookie_count": len(cookie_dict),
                        "message": "检测到登录状态，可以开始投递任务",
                        "next_action": "start_delivery",
                        "debug_info": debug_info
                    })
                else:
                    logger.info("❌ 轮询检测：仍未检测到登录状态")
                    return JsonResponse({
                        "success": True,
                        "is_logged_in": False,
                        "message": "仍未检测到登录状态，请继续等待",
                        "next_action": "continue_waiting",
                        "debug_info": debug_info
                    })
            else:
                logger.warning("⚠️ 轮询检测：没有找到活跃的浏览器实例")
                return JsonResponse({
                    "success": False,
                    "is_logged_in": False,
                    "error": "没有找到活跃的浏览器实例",
                    "message": "请重新启动投递流程",
                    "next_action": "restart_process"
                })
                
        except Exception as e:
            logger.error(f"❌ 轮询检测异常: {str(e)}")
            return JsonResponse({
                "success": False,
                "is_logged_in": False,
                "error": f"轮询检测失败: {str(e)}",
                "message": "检测过程中出现异常",
                "next_action": "retry"
            })
            
    except Exception as e:
        logger.error(f"轮询检查登录状态失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": f"轮询检查失败: {str(e)}"
        })
