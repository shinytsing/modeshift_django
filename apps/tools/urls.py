# QAToolbox/apps/tools/urls.py - 优化版本
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import path

try:
    from . import consumers
except ImportError:
    # 如果consumers无法导入（缺少channels），创建一个虚拟模块
    class MockConsumers:
        pass

    consumers = MockConsumers()

# =============================================================================
# 📋 优化的导入结构 - 按功能分组
# =============================================================================

from .async_test_cases_api import AsyncGenerateTestCasesAPI, DeleteTaskAPI, TaskListAPI, TaskStatusAPI
from .views.download_views import TaskDownloadAPI
from .views.user_resolver_views import UserResolverView, UserResolverTestView
from .views.trojan_views import (
    TrojanDashboardView,
    TrojanConfigView,
    TrojanConfigDownloadView,
    TrojanUsageStatsView,
    TrojanAuthView,
    TrojanGoogleAuthView,
    TrojanGoogleCallbackView,
    TrojanAdminView,
    refresh_trojan_config,
    revoke_trojan_access,
    restore_trojan_access,
    trojan_server_control,
    trojan_usage_report,
)
from .views.job_search_views import (
    job_search_dashboard,
    job_search_launcher,
    job_search_machine,
    start_job_search_api,
    start_job_search_with_playwright_api,
    get_job_search_status_api,
    stop_job_search_api,
    boss_login_api,
    boss_auto_login_and_start_api,
    boss_manual_cookies_start_api,
    boss_login_status_api,
    boss_phone_login_api,
    boss_clear_token_api,
    boss_send_sms_api,
    check_login_status_polling_api,
    test_cookie_execution_api,
)
from .views.token_management_views import (
    save_boss_token_api,
    get_boss_token_api,
    check_login_status_api,
    sync_session_api,
    get_all_tokens_api,
    clear_token_api,
    test_boss_login_api,
    cross_tab_sync_api,
)
from .views.enhanced_job_search_views import (
    enhanced_job_search_launcher,
    start_enhanced_job_search_api,
    get_enhanced_job_search_status_api,
    stop_enhanced_job_search_api,
    get_platform_info_api,
    boss_login_with_token_api,
    check_boss_login_status_api,
    start_boss_qr_login_api,
    start_boss_phone_login_api,
    verify_boss_phone_code_api,
    get_boss_iframe_login_url_api,
)
from .views.cookie_management_views import (
    save_cookies_api,
    get_cookies_api,
    validate_cookies_api,
    get_cookies_info_api,
    clear_cookies_api,
)
from .views.simple_playwright_views import (
    playwright_token_test_view,
    save_token_api,
    get_token_api,
    check_login_status_api,
    clear_token_api,
    test_playwright_api,
)
from .views.playwright_views import (
    playwright_scan_login_api,
    playwright_login_status_api,
    playwright_get_qr_code_api,
    playwright_quick_login_check_api,
)
# 移除不存在的enhanced_boss_views导入
# 移除不存在的test_views导入
from .views.job_login_views import (
    boss_status_api,
    boss_status_detailed_api,
    boss_login_api as boss_login_new_api,
    boss_send_sms_api as boss_send_sms_new_api,
    boss_phone_login_api as boss_phone_login_new_api,
)
from .fitness_tools_views import (
    bmi_calculator,
    body_analyzer,
    calculate_bmi_api,
    calculate_body_composition_api,
    calculate_calories_api,
    calculate_heart_rate_api,
    calculate_one_rm_api,
    calculate_pace_api,
    calculate_protein_api,
    calculate_rm_api,
    calculate_water_api,
    fitness_tools_dashboard,
    get_workout_records_api,
    nutrition_calculator,
    one_rm_calculator,
    predict_reps_api,
    save_workout_record_api,
    workout_planner,
    workout_timer,
    workout_tracker,
)
from .generate_redbook_api import GenerateRedBookAPI

# 从测试用例生成API导入
from .generate_test_cases_api import GenerateTestCasesAPI
from .guitar_training_views import (
    complete_practice_session_api,
    download_tab_api,
    food_image_correction_view,
    food_photo_binding_view,
    generate_tab_api,
    get_practice_stats_api,
    get_recommended_exercises_api,
    get_tab_history_api,
    guitar_practice_session,
    guitar_progress_tracking,
    guitar_song_library,
    guitar_tab_generator,
    guitar_theory_guide,
    guitar_training_dashboard,
    start_practice_session_api,
    upload_audio_for_tab_api,
)

# 从聊天相关视图导入 - 只导入heart_link避免其他导入问题
# 从legacy_views导入缺失的shipbao函数
# 从重命名的legacy_views文件导入剩余函数
from .legacy_views import (
    active_chat_rooms_view,
    add_social_subscription_api,
    delete_subscription_api,
    audio_converter_api,
    audio_converter_view,
    audio_playback_test,
    boss_logout_api,
    buddy_approve_member_api,
    buddy_chat,
    buddy_create,
    buddy_create_event_api,
    buddy_detail,
    buddy_events_api,
    buddy_home,
    buddy_join_event_api,
    buddy_manage,
    buddy_messages_api,
    buddy_send_message_api,
    cancel_heart_link_request_api,
    cancel_number_match_api,
    chat_debug_view,
    chat_enhanced,
    chat_entrance_view,
    chat_room_error_view,
    check_boss_login_status_selenium_api,
    check_heart_link_status_api,
    check_video_room_status_api,
    cleanup_heart_link_api,
    complete_daily_task_api,
    copilot_page,
    create_code_workout_api,
    create_copilot_collaboration_api,
    create_exhaustion_proof_api,
    create_fitness_workout_api,
    create_heart_link_request_api,
    delete_message_api,
    feature_list_api,
    feature_recommendations_api,
    fitness_api,
    food_randomizer,
    generate_boss_qr_code_api,
    get_active_chat_rooms_api,
    get_ai_dependency_api,
    get_boss_login_page_url_api,
    get_boss_user_token_api,
    get_chat_messages_api,
    get_chat_room_participants_api,
    get_checkin_calendar_api,
    get_crawler_status_api,
    get_notifications_api,
    get_online_users_api,
    get_pain_currency_api,
    get_subscription_stats_api,
    get_subscriptions_api,
    get_user_preferred_mode_api,
    get_user_profile_api,
    get_workout_dashboard_api,
    heart_link,
    heart_link_chat,
    heart_link_test_view,
    mark_messages_read_api,
    mark_notification_read_api,
    meditation_audio_api,
    multi_video_chat_view,
    multi_video_test_view,
    number_match_api,
    number_match_view,
    recommendation_stats_api,
    record_exhaustion_audio_api,
    record_mode_click_api,
    resolve_url_api,
    self_analysis_api,
    send_audio_api,
    send_contact_request_api,
    send_file_api,
    send_image_api,
    send_message_api,
    send_video_api,
    chunked_upload_init,
    chunked_upload_chunk,
    chunked_upload_complete,
    shipbao_chat,
    shipbao_check_transaction_api,
    shipbao_create_item_api,
    shipbao_detail,
    shipbao_home,
    shipbao_initiate_transaction_api,
    shipbao_publish,
    shipbao_transactions,
    start_crawler_api,
    tarot_reading_view,
    triple_awakening_dashboard,
    update_online_status_api,
    update_subscription_api,
    user_generated_travel_guide_api,
    user_generated_travel_guide_detail_api,
    user_generated_travel_guide_download_api,
    user_generated_travel_guide_upload_attachment_api,
    user_generated_travel_guide_use_api,
    video_chat_view,
    end_chat_room_api)

# 导入监控视图
from .monitoring_views import (
    MonitoringAPIView,
    clear_cache,
    get_alerts,
    get_cache_stats,
    get_monitoring_data,
    get_system_metrics,
    monitoring_dashboard,
    warm_up_cache,
)


# 从PDF转换器API导入
from .pdf_converter_api import pdf_converter_api

# 导入增强的代理功能视图
from .proxy_view import create_proxy_url_api  # 辅助功能: 创建访问链接
from .proxy_view import download_clash_config_api  # 新功能: 下载Clash配置
from .proxy_view import download_v2ray_config_api  # 新功能: 下载V2Ray配置
from .proxy_view import get_ip_comparison_api  # 核心功能1: IP对比
from .proxy_view import proxy_dashboard  # 主页面
from .proxy_view import proxy_list_api  # 辅助功能: 代理列表
from .proxy_view import setup_proxy_api  # 核心功能2: 一键代理设置
from .proxy_view import web_proxy_api  # 新功能: Web代理浏览
from .proxy_view import web_proxy_browse_api, proxy_browse_view  # 内嵌代理浏览

# 从成就相关视图导入
from .views.achievement_views import achievements_api, get_fitness_achievements_api, share_achievement_api

# 从基础视图导入
from .views.base_views import (
    deepseek_api,
    delete_vanity_task_api,
    follow_fitness_user_api,
    get_boss_login_page_screenshot_api,
    get_vanity_tasks_stats_api,
)

# 从AI找工作视图导入
# 移除重复的导入

# 从Session提取视图导入
from .views.session_extraction_views import (
    session_extractor_page,
    cookie_extractor_page,
    cookie_extractor_simple_page,
    extract_boss_session_api,
    test_boss_session_api,
    use_extracted_session_api,
)

# 从自动Cookie提取器视图导入
from .views.cookie_auto_extractor_views import (
    cookie_auto_extractor_page,
    auto_extract_cookies_api,
    start_job_search_with_extracted_cookies_api,
)
from .views.cookie_simple_extractor_views import (
    cookie_simple_extractor_page,
    simple_extract_cookies_api,
    start_job_search_with_simple_cookies_api,
)
from .views.cookie_test_views import cookie_test_page
from .views.simple_cookie_test_views import simple_cookie_test_page

# 从AI助手视图导入
from .views.java_job_integration_views import (
    start_java_job_delivery_api,
    get_java_job_status_api,
    stop_java_job_api,
    cleanup_java_job_api,
    get_java_qr_image_api,
    refresh_java_qr_code_api,
)
from .views.java_job_launcher_view import java_job_launcher
from .views.boss_qr_code_views import get_boss_qr_code_api, get_boss_qr_image_api
from .views.java_boss_qr_views import get_java_boss_qr_code_api, get_java_boss_qr_image_api, get_login_status_api, refresh_java_boss_qr_api, start_delivery_task_api
from .views.test_qr_views import test_qr_api

from .views.ai_assistant_views import ai_assistant_api, ai_assistant_features_api

# 🔧 基础工具视图
from .views.basic_tools_views import (
    ai_analysis_api,
    fitness_center,
    fortune_analyzer,
    location_api,
    pdf_converter,
    pdf_converter_test,
    redbook_generator,
    self_analysis,
    storyboard,
    storyboard_api,
    task_manager,
    test_case_generator,
    training_plan_editor,
    update_location_api,
    web_crawler,
    yuanqi_marriage_analyzer,
)

# 导入浏览器代理配置视图
from .views.browser_proxy_views import (
    configure_browser_proxy,
    disable_browser_proxy,
    get_proxy_status,
    quick_proxy_setup,
    test_proxy_connection,
)
from .views.chat_views import download_chat_file

# 从签到视图导入
from .views.checkin_views import checkin_add_api, checkin_delete_api, checkin_delete_api_simple

# 导入Clash内嵌代理系统视图
from .views.clash_views import (
    clash_add_proxy_api,
    clash_auto_setup_api,
    clash_config_api,
    clash_configure_proxy_api,
    clash_dashboard,
    clash_disable_proxy_api,
    clash_install_api,
    clash_proxy_health_api,
    clash_proxy_info_api,
    clash_remove_proxy_api,
    clash_restart_api,
    clash_start_api,
    clash_status_api,
    clash_stop_api,
    clash_switch_proxy_api,
    clash_test_connection_api,
    clash_test_external_access_api,
    clash_update_config_api,
)
from .views.remote_clashx_views import (
    remote_start_clashx_api,
    download_clash_config_api,
    download_start_script_api,
)
from .views.desire_views import (
    add_desire_api,
    add_desire_todo_api,
    check_desire_fulfillment_api,
    complete_desire_todo_api,
    delete_desire_todo_api,
    desire_dashboard,
    edit_desire_todo_api,
    generate_ai_image_api,
    get_desire_dashboard_api,
    get_desire_progress_api,
    get_desire_todo_stats_api,
    get_desire_todos_api,
    get_fulfillment_history_api,
)

# 从日记相关视图导入
from .views.diary_views import creative_writer, creative_writer_api, emo_diary, emo_diary_api
# enhanced_fitness_views 已删除

# 从文件下载视图导入
from .views.file_download_views import generic_file_download
from .views.fitness_views import (
    add_weight_record_api,
    apply_training_plan_api,
    apply_training_plan_template_api,
    comment_fitness_post_api,
    create_fitness_community_post_api,
    delete_training_plan_api,
    equip_badge_api,
    fitness_community,
    fitness_profile,
    fitness_tools,
    follow_fitness_user_api,
    get_active_training_plan_api,
    get_fitness_achievements_api,
    get_fitness_community_posts_api,
    get_fitness_user_profile_api,
    get_training_modes_api,
    get_training_plan_api,
    get_training_plan_templates_api,
    import_training_mode_api,
    like_fitness_post_api,
    list_training_plans_api,
    save_training_plan_api,
    save_training_plan_editor_api,
    share_achievement_api,
    training_mode_selector,
)

# 从食物图片视图导入
from .views.food_image_views import api_photos

# 从食物随机器视图导入
from .views.food_randomizer_views import (
    food_randomizer_history_api,
    food_randomizer_pure_random_api,
    food_randomizer_rate_api,
    food_randomizer_statistics_api,
)

# 从食物相关视图导入
from .views.food_views import (
    api_food_photo_bindings,
    api_foods,
    api_remove_food_photo_binding,
    api_save_food_photo_bindings,
    api_upload_food_photo,
)
from .views.health_views import (
    health_check,
    legacy_health_check,
    detailed_health_check,
    readiness_check,
    liveness_check,
    metrics_endpoint,
)

# 从地图基础视图导入
from .views.map_base_views import location_api, map_picker_api, save_user_location_api

# 从MeeSomeone视图导入
from .views.meetsomeone_views import (
    create_important_moment_api,
    create_interaction_api,
    create_person_profile_api,
    get_dashboard_stats_api,
    get_graph_data_api,
    get_interactions_api,
    get_person_profiles_api,
    get_relationship_tags_api,
    get_timeline_data_api,
    meetsomeone_dashboard_view,
    meetsomeone_graph_view,
    meetsomeone_timeline_view,
)
from .views.multi_chat_views import create_chat_room, list_active_rooms, multi_chat_room

# 🎵 音乐相关视图
from .views.music_views import meditation_guide, music_api, music_healing, next_song_api, peace_meditation_view

# 从通知视图导入
from .views.notification_views import (
    clear_all_notifications_api,
    create_system_notification_api,
    get_notification_summary_api,
    get_unread_notifications_api,
    mark_notifications_read_api,
)

# 从PDF转换器视图导入
from .views.pdf_converter_views import (
    pdf_converter_batch,
    pdf_converter_rating_api,
    pdf_converter_stats_api,
    pdf_converter_status_api,
    pdf_download_view,
)

# 从shipbao视图导入
from .views.shipbao_views import (
    map_geocode_api,
    map_reverse_geocode_api,
    map_search_location_api,
    save_user_location_api,
    shipbao_contact_seller_api,
    shipbao_contact_wanter_api,
    shipbao_favorites_api,
    shipbao_inquiry_queue_api,
    shipbao_items_api,
    shipbao_mark_sold_api,
    shipbao_remove_item_api,
    shipbao_transaction_status_api,
    shipbao_want_item_api,
    shipbao_want_list_api,
)
from .views.simple_diary_views import (
    diary_achievements,
    diary_calendar_view,
    diary_history_timeline,
    diary_image_upload,
    diary_list,
    diary_mood_save,
    diary_quick_save,
    diary_template_save,
    diary_templates,
    diary_weekly_report,
    simple_diary_home,
)

# 从塔罗牌视图导入
from .views.tarot_views import (
    initialize_tarot_data_api,
    tarot_create_reading_api,
    tarot_daily_energy_api,
    tarot_feedback_api,
    tarot_reading_detail_api,
    tarot_readings_api,
    tarot_spreads_api,
)

# 从主题相关视图导入
from .views.theme_views import get_user_theme_api, save_user_theme_api, switch_theme_api, test_theme_api
from .views.travel_post_views import (
    map_picker_api,
    travel_city_list_api,
    travel_post_comment_api,
    travel_post_create_api,
    travel_post_detail_api,
    travel_post_favorite_api,
    travel_post_home,
    travel_post_like_api,
    travel_post_list_api,
    update_post_location_api,
    user_favorites_api,
)
from .views.travel_views import (
    check_local_travel_data_api,
    export_travel_guide_api,
    get_travel_guide_detail_api,
    get_travel_guides_api,
    toggle_favorite_guide_api,
    travel_guide,
    travel_guide_api,
)
from .views.vanity_views import (
    add_sin_points_api,
    add_sponsor_api,
    add_vanity_task_api,
    based_dev_avatar,
    complete_vanity_task_api,
    create_based_dev_avatar_api,
    get_based_dev_achievements_api,
    get_based_dev_avatar_api,
    get_sponsors_api,
    get_vanity_tasks_api,
    get_vanity_wealth_api,
    like_based_dev_avatar_api,
    sponsor_hall_of_fame,
    update_based_dev_stats_api,
    vanity_os_dashboard,
    vanity_rewards,
    vanity_todo_list,
)

# 从ZIP相关视图导入
from .views.zip_views import (
    compress_single_file_api,
    compress_uploaded_file_api,
    create_zip_from_directory_api,
    create_zip_from_files_api,
    create_zip_from_uploaded_files_api,
    download_zip_file,
    extract_zip_api,
    get_zip_info_api,
    zip_tool_view,
)

# 从原来的views.py文件导入剩余的函数
# from . import views  # 已删除，避免循环导入

# 测试视图 (已删除)
# from .views.test_views import test_tarot_view, test_api_view, test_tarot_template_view, test_tarot_reading_view, test_tarot_spreads_api


# 导入健身营养定制系统视图 - 已隐藏
# from .fitness_nutrition_views import (
#     nutrition_dashboard, nutrition_profile_setup, nutrition_generate_plan,
#     nutrition_meal_log, nutrition_weight_tracking, nutrition_reminders,
#     nutrition_progress, nutrition_api_generate_plan, nutrition_settings
# )


# 注意：原本从missing_views导入的函数已经在各自专门的视图文件中有了更好的实现


# 从missing_views只导入仍需要的函数（避免重复）
# from .missing_views import (
#     feature_discovery_view, my_recommendations_view, admin_feature_management_view,
#     create_job_search_request_api, get_job_search_requests_api,
#     pdf_converter_rating_api,
# )


# PDF转换器API已移动到 pdf_converter_views.py


# 时光胶囊日记入口页面
def diary_entrance(request):
    return render(request, "tools/diary_entrance.html")


# Mode主页面视图函数
@login_required
def work_mode_view(request):
    """极客模式主页面"""
    return render(request, "tools/work_mode.html")


@login_required
def life_mode_view(request):
    """生活模式主页面"""
    return render(request, "tools/life_mode.html")


@login_required
def cyberpunk_mode_view(request):
    """赛博朋克模式主页面"""
    return render(request, "tools/cyberpunk_mode.html")


@login_required
def training_mode_view(request):
    """训练模式主页面"""
    return render(request, "tools/training_mode.html")


@login_required
def guitar_training_view(request):
    """吉他训练页面"""
    return render(request, "tools/guitar_training.html")


@login_required
def emo_mode_view(request):
    """情感模式主页面"""
    return render(request, "tools/emo_mode.html")


def test_user_dropdown_view(request):
    """用户下拉菜单和主题切换测试页面"""
    return render(request, "test_user_dropdown_and_theme.html")


def simple_test_view(request):
    """简单测试页面"""
    return render(request, "simple_test.html")


def anti_programmer_profile_view(request):
    """反程序员形象页面"""
    return render(request, "tools/anti_programmer_profile.html")


def desire_todo_enhanced_view(request):
    """欲望代办增强页面"""
    return render(request, "tools/desire_todo_enhanced.html")


@login_required
def homework_grading_view(request):
    """作业批改与智能组卷页面"""
    return render(request, "tools/homework_grading.html")


# Tools主页面视图函数
def tools_index_view(request):
    """工具主页面"""
    from django.conf import settings

    if not getattr(settings, "AUTH_LOGIN_DISABLED", False):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login

            return redirect_to_login(request.get_full_path())
    return render(request, "tools/index.html")


# 应用名称（命名空间）
app_name = "tools"

# URL配置
urlpatterns = [
    # Tools主页面路由
    path("", tools_index_view, name="tools_index"),
    # 模式主页面路由
    path("work/", work_mode_view, name="work"),  # 添加work路径以修复齿轮图标404错误
    path("work_mode/", work_mode_view, name="work_mode"),
    path("life/", life_mode_view, name="life"),  # 添加life路径以修复齿轮图标404错误
    path("life_mode/", life_mode_view, name="life_mode"),
    path("training/", training_mode_view, name="training"),  # 添加training路径以修复齿轮图标404错误
    path("training_mode/", training_mode_view, name="training_mode"),
    path("cyberpunk/", cyberpunk_mode_view, name="cyberpunk"),  # 添加cyberpunk路径以修复齿轮图标404错误
    path("cyberpunk_mode/", cyberpunk_mode_view, name="cyberpunk_mode"),
    path("emo/", emo_mode_view, name="emo"),  # 添加emo路径以修复齿轮图标404错误
    path("emo_mode/", emo_mode_view, name="emo_mode"),
    path("test_user_dropdown/", test_user_dropdown_view, name="test_user_dropdown"),
    path("simple_test/", simple_test_view, name="simple_test"),
    path("guitar_training/", guitar_training_view, name="guitar_training"),
    path("anti_programmer_profile/", anti_programmer_profile_view, name="anti_programmer_profile"),
    path("desire_todo_enhanced/", desire_todo_enhanced_view, name="desire_todo_enhanced"),
    path("homework_grading/", homework_grading_view, name="homework_grading"),
    # 基础工具页面路由
    path("test_case_generator/", test_case_generator, name="test_case_generator"),
    path("task_manager/", task_manager, name="task_manager"),
    path("redbook_generator/", redbook_generator, name="redbook_generator"),
    path("pdf_converter/", pdf_converter, name="pdf_converter"),
    path("pdf_converter_test/", pdf_converter_test, name="pdf_converter_test"),
    path("yuanqi/", yuanqi_marriage_analyzer, name="yuanqi_marriage_analyzer"),
    path("fortune_analyzer/", fortune_analyzer, name="fortune_analyzer"),
    path("web_crawler/", web_crawler, name="web_crawler"),
    path("self_analysis/", self_analysis, name="self_analysis"),
    path("storyboard/", storyboard, name="storyboard"),
    # 测试用例生成API路由
    path("api/generate-testcases/", GenerateTestCasesAPI.as_view(), name="generate_test_cases_api"),
    path("api/generate-redbook/", GenerateRedBookAPI.as_view(), name="generate_redbook_api"),
    # 异步测试用例生成API路由
    path("api/async/generate-testcases/", AsyncGenerateTestCasesAPI.as_view(), name="async_generate_test_cases_api"),
    path("api/async/task/delete/", DeleteTaskAPI.as_view(), name="delete_task_api"),
    path("api/async/task/<str:task_id>/", TaskStatusAPI.as_view(), name="task_status_api"),
    path("api/async/task/<str:task_id>/download/<str:format_type>/", TaskDownloadAPI.as_view(), name="task_download_api"),
    path("api/async/tasks/", TaskListAPI.as_view(), name="task_list_api"),
    path("fitness_center/", fitness_center, name="fitness_center"),
    path("training_plan_editor/", training_plan_editor, name="training_plan_editor"),
    path("diary/", diary_entrance, name="diary"),  # 新的主要日记入口
    path("simple-diary/", simple_diary_home, name="simple_diary"),  # 简单生活日记主页
    # 简单日记API路由
    path("api/diary/quick-save/", diary_quick_save, name="diary_quick_save"),
    path("api/diary/mood-save/", diary_mood_save, name="diary_mood_save"),
    path("api/diary/image-upload/", diary_image_upload, name="diary_image_upload"),
    path("api/diary/template-save/", diary_template_save, name="diary_template_save"),
    path("api/diary/calendar/", diary_calendar_view, name="diary_calendar"),
    path("api/diary/achievements/", diary_achievements, name="diary_achievements"),
    path("api/diary/templates/", diary_templates, name="diary_templates"),
    path("api/diary/history/", diary_history_timeline, name="diary_history"),
    path("api/diary/weekly-report/", diary_weekly_report, name="diary_weekly_report"),
    path("api/diary/list/", diary_list, name="diary_list"),
    path("emo_diary/", emo_diary, name="emo_diary"),
    path("creative_writer/", creative_writer, name="creative_writer"),
    path("meditation_guide/", meditation_guide, name="meditation_guide"),
    path("peace_meditation/", peace_meditation_view, name="peace_meditation"),
    path("music_healing/", music_healing, name="music_healing"),
    # 暂时注释掉聊天相关路径，直到修复导入问题
    path("heart_link/", heart_link, name="heart_link"),
    path("heart_link/test/", heart_link_test_view, name="heart_link_test"),
    # path('click-test/', click_test_view, name='click_test'), # 点击测试页面（无需登录）
    path("heart_link/chat/<str:room_id>/", heart_link_chat, name="heart_link_chat"),
    path("chat/", chat_entrance_view, name="chat_entrance"),  # 聊天入口页面
    path("chat/room/<str:room_id>/", multi_chat_room, name="multi_chat_room"),  # 多人聊天室
    path("chat/enhanced/<str:room_id>/", chat_enhanced, name="chat_enhanced"),
    path("chat/debug/<str:room_id>/", chat_debug_view, name="chat_debug"),  # 聊天调试页面
    path("chat/active_rooms/", active_chat_rooms_view, name="active_chat_rooms"),  # 活跃聊天室页面
    path("number-match/", number_match_view, name="number_match"),  # 数字匹配页面
    path("video-chat/<str:room_id>/", video_chat_view, name="video_chat"),
    path("multi-video-chat/<str:room_id>/", multi_video_chat_view, name="multi_video_chat"),  # 多人视频聊天页面
    path(
        "check-video-room-status/<str:room_id>/", check_video_room_status_api, name="check_video_room_status_api"
    ),  # 检查视频聊天室状态
    path("multi-video-test/", multi_video_test_view, name="multi_video_test"),  # 多人视频测试页面
    path("chat-room-error/<str:error_type>/<str:room_id>/", chat_room_error_view, name="chat_room_error"),  # 聊天室错误页面
    # path('chat/test-two-users/<str:room_id>/', test_two_users_chat_view, name='test_two_users_chat'), # 两个人聊天测试页面
    # path('chat/secure/', secure_chat_entrance, name='secure_chat_entrance'), # 安全聊天室入口
    # path('chat/secure/<str:room_id>/<str:token>/', secure_chat_enhanced, name='secure_chat_enhanced'), # 安全聊天室页面
    # path('douyin_analyzer/', douyin_analyzer, name='douyin_analyzer'),  # 已隐藏
    path("triple_awakening/", triple_awakening_dashboard, name="triple_awakening_dashboard"),
    path("copilot/", copilot_page, name="copilot_page"),
    path("desire_dashboard/", desire_dashboard, name="desire_dashboard"),
    path("vanity_os/", vanity_os_dashboard, name="vanity_os_dashboard"),
    path("vanity_rewards/", vanity_rewards, name="vanity_rewards"),
    path("sponsor_hall_of_fame/", sponsor_hall_of_fame, name="sponsor_hall_of_fame"),
    path("based_dev_avatar/", based_dev_avatar, name="based_dev_avatar"),
    path("vanity_todo_list/", vanity_todo_list, name="vanity_todo_list"),
    path("travel_guide/", travel_guide, name="travel_guide"),
    path("food_randomizer/", food_randomizer, name="food_randomizer"),
    path("food_photo_binding/", food_photo_binding_view, name="food_photo_binding"),
    # 音频转换器
    path("audio_converter/", audio_converter_view, name="audio_converter"),
    path("audio_playback_test/", audio_playback_test, name="audio_playback_test"),
    path("food_image_correction/", food_image_correction_view, name="food_image_correction"),
    path("fitness/", fitness_center, name="fitness"),  # 添加fitness主页面
    path("fitness/community/", fitness_community, name="fitness_community"),
    path("fitness/profile/", fitness_profile, name="fitness_profile"),
    path("fitness/add_weight_record/", add_weight_record_api, name="add_weight_record_api"),
    path("fitness/tools/", fitness_tools, name="fitness_tools"),
    path("fitness/plan-editor/", training_plan_editor, name="training_plan_editor"),
    path("fitness/mode-selector/", training_mode_selector, name="training_mode_selector"),
    # 健身工具详细页面
    path("fitness/tools/dashboard/", fitness_tools_dashboard, name="fitness_tools_dashboard"),
    path("fitness/tools/bmi-calculator/", bmi_calculator, name="bmi_calculator"),
    path("fitness/tools/workout-timer/", workout_timer, name="workout_timer"),
    path("fitness/tools/nutrition-calculator/", nutrition_calculator, name="nutrition_calculator"),
    path("fitness/tools/workout-tracker/", workout_tracker, name="workout_tracker"),
    path("fitness/tools/body-analyzer/", body_analyzer, name="body_analyzer"),
    path("fitness/tools/workout-planner/", workout_planner, name="workout_planner"),
    path("fitness/tools/one-rm-calculator/", one_rm_calculator, name="one_rm_calculator"),
    # AI找工作系统路由
    path("job-search/", job_search_dashboard, name="job_search_dashboard"),
    path("job-search/launcher/", job_search_launcher, name="job_search_launcher"),
    path("job-search/machine/", job_search_machine, name="job_search_machine"),
    path("job-search/api/start/", start_job_search_api, name="start_job_search_api"),
    path("job-search/api/start-playwright/", start_job_search_with_playwright_api, name="start_job_search_with_playwright_api"),
    path("job-search/api/status/", get_job_search_status_api, name="get_job_search_status_api"),
    path("job-search/api/stop/", stop_job_search_api, name="stop_job_search_api"),
    path("job-search/api/boss-login/", boss_login_api, name="boss_login_api"),
    path("job-search/api/boss-auto-login-start/", boss_auto_login_and_start_api, name="boss_auto_login_and_start_api"),
    path("job-search/api/boss-manual-cookies-start/", boss_manual_cookies_start_api, name="boss_manual_cookies_start_api"),
    path("job-search/api/boss-status/", boss_status_api, name="boss_status_api"),
    path("job-search/api/boss-status-detailed/", boss_status_detailed_api, name="boss_status_detailed_api"),
    path("job-search/api/boss-login-status/", boss_login_status_api, name="boss_login_status_api"),
    path("job-search/api/boss-phone-login/", boss_phone_login_api, name="boss_phone_login_api"),
    
    # Cookie测试执行API
    path("job-search/api/test-cookie-execution/", test_cookie_execution_api, name="test_cookie_execution_api"),
    path("job-search/api/boss-send-sms/", boss_send_sms_api, name="boss_send_sms_api"),
    path("job-search/api/check-login-status-polling/", check_login_status_polling_api, name="check_login_status_polling_api"),
    
    # Session提取相关页面和API
    path("job-search/session-extractor/", session_extractor_page, name="session_extractor_page"),
    path("job-search/cookie-extractor/", cookie_extractor_page, name="cookie_extractor_page"),
    path("job-search/cookie-extractor-simple/", cookie_extractor_simple_page, name="cookie_extractor_simple_page"),
    path("job-search/cookie-auto-extractor/", cookie_auto_extractor_page, name="cookie_auto_extractor_page"),
    path("job-search/cookie-simple-extractor/", cookie_simple_extractor_page, name="cookie_simple_extractor_page"),
    path("job-search/cookie-test/", cookie_test_page, name="cookie_test_page"),
    path("job-search/simple-cookie-test/", simple_cookie_test_page, name="simple_cookie_test_page"),
    path("job-search/api/auto-extract-cookies/", auto_extract_cookies_api, name="auto_extract_cookies_api"),
    path("job-search/api/start-with-extracted-cookies/", start_job_search_with_extracted_cookies_api, name="start_job_search_with_extracted_cookies_api"),
    path("job-search/api/simple-extract-cookies/", simple_extract_cookies_api, name="simple_extract_cookies_api"),
    path("job-search/api/start-with-simple-cookies/", start_job_search_with_simple_cookies_api, name="start_job_search_with_simple_cookies_api"),
    path("job-search/api/extract-session/", extract_boss_session_api, name="extract_boss_session_api"),
    path("job-search/api/test-session/", test_boss_session_api, name="test_boss_session_api"),
    path("job-search/api/use-session/", use_extracted_session_api, name="use_extracted_session_api"),
    
    # 增强版AI找工作系统路由
    path("job-search/enhanced/", enhanced_job_search_launcher, name="enhanced_job_search_launcher"),
    path("job-search/api/start-enhanced/", start_enhanced_job_search_api, name="start_enhanced_job_search_api"),
    path("job-search/api/status-enhanced/", get_enhanced_job_search_status_api, name="get_enhanced_job_search_status_api"),
    path("job-search/api/stop-enhanced/", stop_enhanced_job_search_api, name="stop_enhanced_job_search_api"),
    path("job-search/api/platform-info/", get_platform_info_api, name="get_platform_info_api"),
    path("job-search/api/boss-token-login/", boss_login_with_token_api, name="boss_login_with_token_api"),
    path("job-search/api/boss-status-check/", check_boss_login_status_api, name="check_boss_login_status_api"),
    path("job-search/api/boss-qr-login/", start_boss_qr_login_api, name="start_boss_qr_login_api"),
    path("job-search/api/boss-phone-login/", start_boss_phone_login_api, name="start_boss_phone_login_api"),
    path("job-search/api/boss-verify-code/", verify_boss_phone_code_api, name="verify_boss_phone_code_api"),
    path("job-search/api/boss-clear-token/", boss_clear_token_api, name="boss_clear_token_api"),
    
    # Java Job项目集成路由
    path("java-job/launcher/", java_job_launcher, name="java_job_launcher"),
    path("java-job/api/start/", start_java_job_delivery_api, name="start_java_job_delivery_api"),
    path("java-job/api/qr-code/", get_boss_qr_code_api, name="get_boss_qr_code_api"),
    path("java-job/api/qr-image/", get_boss_qr_image_api, name="get_boss_qr_image_api"),
    path("java-job/api/java-qr-code/", get_java_boss_qr_code_api, name="get_java_boss_qr_code_api"),
    path("java-job/api/java-qr-image/", get_java_boss_qr_image_api, name="get_java_boss_qr_image_api"),
    path("java-job/api/refresh-qr/", refresh_java_boss_qr_api, name="refresh_java_boss_qr_api"),
    path("java-job/api/start-delivery/", start_delivery_task_api, name="start_delivery_task_api"),
    path("java-job/api/login-status/", get_login_status_api, name="get_login_status_api"),
    path("test-qr/", test_qr_api, name="test_qr_api"),
    path("java-job/api/status/", get_java_job_status_api, name="get_java_job_status_api"),
    path("java-job/api/stop/", stop_java_job_api, name="stop_java_job_api"),
    path("java-job/api/cleanup/", cleanup_java_job_api, name="cleanup_java_job_api"),
    path("java-job/api/qr-image/", get_java_qr_image_api, name="get_java_qr_image_api"),
    path("java-job/api/refresh-qr/", refresh_java_qr_code_api, name="refresh_java_qr_code_api"),
    
    # 增强版Boss直聘路由 - 已移除（功能不存在）
    
    path("tarot/reading/", tarot_reading_view, name="tarot_reading"),
    path("meetsomeone/", meetsomeone_dashboard_view, name="meetsomeone_dashboard"),
    path("meetsomeone/timeline/", meetsomeone_timeline_view, name="meetsomeone_timeline"),
    path("meetsomeone/graph/", meetsomeone_graph_view, name="meetsomeone_graph"),
    # 功能推荐系统页面路由
    #     path('feature_discovery/', feature_discovery_view, name='feature_discovery_page'),
    #     path('my_recommendations/', my_recommendations_view, name='my_recommendations_page'),
    #     path('admin/feature_management/', admin_feature_management_view, name='admin_feature_management'),
    # 吉他训练系统路由
    path("guitar-training/", guitar_training_dashboard, name="guitar_training_dashboard"),
    path("guitar-practice/<str:practice_type>/<str:difficulty>/", guitar_practice_session, name="guitar_practice_session"),
    path("guitar-progress/", guitar_progress_tracking, name="guitar_progress_tracking"),
    path("guitar-theory/", guitar_theory_guide, name="guitar_theory_guide"),
    path("guitar-songs/", guitar_song_library, name="guitar_song_library"),
    # 简化代理系统路由
    path("proxy-dashboard/", proxy_dashboard, name="proxy_dashboard"),
    # API路由
    path("api/vanity_wealth/", get_vanity_wealth_api, name="get_vanity_wealth_api"),
    path("api/add_sin_points/", add_sin_points_api, name="add_sin_points_api"),
    path("api/sin_points/add/", add_sin_points_api, name="add_sin_points_api_alt"),  # 添加备用路径
    path("api/music/", music_api, name="music_api"),
    path("api/next_song/", next_song_api, name="next_song_api"),  # 修复：使用实际函数
    path("api/feature_recommendations/", feature_recommendations_api, name="feature_recommendations_api"),
    path("api/feature_recommendation/", feature_recommendations_api, name="feature_recommendation_api"),
    path("api/resolve_url/", resolve_url_api, name="resolve_url_api"),
    path("api/feature_list/", feature_list_api, name="feature_list_api"),
    path("api/recommendation_stats/", recommendation_stats_api, name="recommendation_stats_api"),
    path("api/achievements/", achievements_api, name="achievements_api"),
    path("api/training_plans/save/", save_training_plan_api, name="save_training_plan_api"),
    path("api/training_plans/list/", list_training_plans_api, name="list_training_plans_api"),
    path("api/training_plans/<int:plan_id>/", get_training_plan_api, name="get_training_plan_api"),
    path("api/training_plans/active/", get_active_training_plan_api, name="get_active_training_plan_api"),
    path("api/training_plans/apply/", apply_training_plan_api, name="apply_training_plan_api"),
    path("api/training_plans/templates/", get_training_plan_templates_api, name="get_training_plan_templates_api"),
    path("api/training_plans/templates/apply/", apply_training_plan_template_api, name="apply_training_plan_template_api"),
    path("api/training_plans/editor/save/", save_training_plan_editor_api, name="save_training_plan_editor_api"),
    path("api/training_plans/<int:plan_id>/delete/", delete_training_plan_api, name="delete_training_plan_api"),
    path("api/fitness/equip_badge/", equip_badge_api, name="equip_badge_api"),
    path("api/deepseek/", deepseek_api, name="deepseek_api"),
    # 位置API
    path("api/location/", location_api, name="location_api"),
    path("api/location/update/", update_location_api, name="update_location_api"),
    path("api/ai-analysis/", ai_analysis_api, name="ai_analysis_api"),
    # 旅游攻略API
    path("api/travel_guide/", travel_guide_api, name="travel_guide_api"),
    path("travel_guide_api/", travel_guide_api, name="travel_guide_api_alt"),  # 添加备用路径
    path("api/travel_guide/list/", get_travel_guides_api, name="travel_guide_list_api"),
    path("api/travel_guide/check-local-data/", check_local_travel_data_api, name="travel_guide_check_local_api"),
    path("api/travel_guide/<int:guide_id>/", get_travel_guide_detail_api, name="travel_guide_detail_api"),
    path(
        "api/travel_guide/<int:guide_id>/toggle_favorite/", toggle_favorite_guide_api, name="travel_guide_toggle_favorite_api"
    ),
    path("api/travel_guide/<int:guide_id>/export/", export_travel_guide_api, name="travel_guide_export_api"),
    # 重构后的旅行攻略相关
    path("travel_posts/", travel_post_home, name="travel_post_home"),
    path("api/travel_posts/", travel_post_list_api, name="travel_post_list_api"),
    path("api/travel_posts/create/", travel_post_create_api, name="travel_post_create_api"),
    path("api/travel_posts/<int:post_id>/", travel_post_detail_api, name="travel_post_detail_api"),
    path("api/travel_posts/<int:post_id>/like/", travel_post_like_api, name="travel_post_like_api"),
    path("api/travel_posts/<int:post_id>/favorite/", travel_post_favorite_api, name="travel_post_favorite_api"),
    path("api/travel_posts/<int:post_id>/comments/", travel_post_comment_api, name="travel_post_comment_api"),
    path("api/travel_posts/<int:post_id>/location/", update_post_location_api, name="update_post_location_api"),
    path("api/travel_cities/", travel_city_list_api, name="travel_city_list_api"),
    path("api/user/favorites/", user_favorites_api, name="user_favorites_api"),
    # 地图相关API
    path("api/location/", location_api, name="location_api"),
    path("api/map_picker/", map_picker_api, name="map_picker_api"),
    path("api/save_user_location/", save_user_location_api, name="save_user_location_api"),
    # 船宝页面路由
    path("shipbao/", shipbao_home, name="shipbao_home"),
    path("shipbao/item/<int:item_id>/", shipbao_detail, name="shipbao_detail"),
    # 高优先级：添加缺失的API路由
    # 健身社区相关API
    path("api/fitness_community/posts/", get_fitness_community_posts_api, name="get_fitness_community_posts_api"),
    path("api/fitness_community/create_post/", create_fitness_community_post_api, name="create_fitness_community_post_api"),
    path("api/fitness_community/like_post/", like_fitness_post_api, name="like_fitness_post_api"),
    path("api/fitness_community/comment_post/", comment_fitness_post_api, name="comment_fitness_post_api"),
    path("api/fitness/user_profile/", get_fitness_user_profile_api, name="get_fitness_user_profile_api"),
    # BOSS直聘相关API
    path("api/boss/qr_screenshot/", generate_boss_qr_code_api, name="generate_boss_qr_code_api"),
    path("api/boss/login_page_url/", get_boss_login_page_url_api, name="get_boss_login_page_url_api"),
    path("api/boss/login_page_screenshot/", get_boss_login_page_screenshot_api, name="get_boss_login_page_screenshot_api"),
    path("api/boss/user_token/", get_boss_user_token_api, name="get_boss_user_token_api"),
    path("api/boss/check_login_selenium/", check_boss_login_status_selenium_api, name="check_boss_login_status_selenium_api"),
    path("api/boss/logout/", boss_logout_api, name="boss_logout_api"),
    path("api/boss/send_contact_request/", send_contact_request_api, name="send_contact_request_api"),
    path("api/boss/start_crawler/", start_crawler_api, name="start_crawler_api"),
    path("api/boss/crawler_status/", get_crawler_status_api, name="get_crawler_status_api"),
    # path('api/job_search/profile/save/', save_job_profile_api, name='save_job_profile_api'),
    # path('api/job_search/statistics/', get_job_search_statistics_api, name='get_job_search_statistics_api'),
    # path('api/job_search/update_application_status/', update_application_status_api, name='update_application_status_api'),
    # path('api/job_search/add_application_notes/', add_application_notes_api, name='add_application_notes_api'),
    # Heart Link相关API路由
    path("api/heart_link/create/", create_heart_link_request_api, name="create_heart_link_request_api"),
    path("api/heart_link/cancel/", cancel_heart_link_request_api, name="cancel_heart_link_request_api"),
    path("api/heart_link/status/", check_heart_link_status_api, name="check_heart_link_status_api"),
    path("api/heart_link/cleanup/", cleanup_heart_link_api, name="cleanup_heart_link_api"),
    # 多人聊天相关API路由
    path("api/chat/create-room/", create_chat_room, name="create_chat_room_api"),
    path("api/chat/active-rooms/", list_active_rooms, name="list_active_rooms_api"),
    # 聊天相关API路由
    path("api/chat/<str:room_id>/messages/", get_chat_messages_api, name="get_chat_messages_api"),
    path("api/chat/<str:room_id>/send/", send_message_api, name="send_message_api"),
    path("api/chat/<str:room_id>/send-image/", send_image_api, name="send_image_api"),
    path("api/chat/<str:room_id>/send-audio/", send_audio_api, name="send_audio_api"),
    path("api/chat/<str:room_id>/send-file/", send_file_api, name="send_file_api"),
    path("api/chat/<str:room_id>/send-video/", send_video_api, name="send_video_api"),
    path("api/chat/<str:room_id>/delete-message/<int:message_id>/", delete_message_api, name="delete_message_api"),
    # 分片上传API路由
    path("api/chat/<str:room_id>/chunked-upload/init/", chunked_upload_init, name="chunked_upload_init"),
    path("api/chat/<str:room_id>/chunked-upload/chunk/", chunked_upload_chunk, name="chunked_upload_chunk"),
    path("api/chat/<str:room_id>/chunked-upload/complete/", chunked_upload_complete, name="chunked_upload_complete"),
    # 通知相关API路由
    path("api/notifications/unread/", get_unread_notifications_api, name="get_unread_notifications_api"),
    path("api/notifications/mark-read/", mark_notifications_read_api, name="mark_notifications_read_api"),
    path("api/notifications/clear-all/", clear_all_notifications_api, name="clear_all_notifications_api"),
    path("api/notifications/summary/", get_notification_summary_api, name="get_notification_summary_api"),
    path("api/notifications/create/", create_system_notification_api, name="create_system_notification_api"),
    path("api/chat/<str:room_id>/mark-read/", mark_messages_read_api, name="mark_messages_read_api"),
    path("api/chat/<str:room_id>/end/", end_chat_room_api, name="end_chat_room_api"),
    path("api/chat/<str:room_id>/download/<int:message_id>/", download_chat_file, name="download_chat_file"),
    path("api/chat/online_status/", update_online_status_api, name="update_online_status_api"),
    path("api/chat/<str:room_id>/online_users/", get_online_users_api, name="get_online_users_api"),
    path("api/chat/<str:room_id>/participants/", get_chat_room_participants_api, name="get_chat_room_participants_api"),
    path("api/chat/active_rooms/", get_active_chat_rooms_api, name="get_active_chat_rooms_api"),
    # 用户资料相关API路由
    path("api/user/<int:user_id>/profile/", get_user_profile_api, name="get_user_profile_api"),
    # 食物相关API路由
    path("api/foods/", api_foods, name="api_foods"),
    path("api/food_photo_bindings/", api_food_photo_bindings, name="api_food_photo_bindings"),
    path("api/save_food_photo_bindings/", api_save_food_photo_bindings, name="api_save_food_photo_bindings"),
    path("api/remove_food_photo_binding/", api_remove_food_photo_binding, name="api_remove_food_photo_binding"),
    path("api/upload_food_photo/", api_upload_food_photo, name="api_upload_food_photo"),
    # path('api/food_list/', get_food_list_api, name='get_food_list_api'),  # 已删除
    # path('api/food_image_crawler/', food_image_crawler_api, name='food_image_crawler_api'),  # 已删除
    # 成就相关API路由
    path("api/fitness_community/achievements/", get_fitness_achievements_api, name="get_fitness_achievements_api"),
    path("api/share_achievement/", share_achievement_api, name="share_achievement_api"),
    # Desire相关API路由
    path("api/desire_dashboard/", get_desire_dashboard_api, name="get_desire_dashboard_api"),
    path("api/desire_dashboard/add/", add_desire_api, name="add_desire_api"),
    path("api/desire_dashboard/check_fulfillment/", check_desire_fulfillment_api, name="check_desire_fulfillment_api"),
    path("api/desire_dashboard/generate_image/", generate_ai_image_api, name="generate_ai_image_api"),
    path("api/desire_dashboard/progress/", get_desire_progress_api, name="get_desire_progress_api"),
    path("api/desire_dashboard/history/", get_fulfillment_history_api, name="get_fulfillment_history_api"),
    path("api/desire_todos/", get_desire_todos_api, name="get_desire_todos_api"),
    path("api/desire_todos/add/", add_desire_todo_api, name="add_desire_todo_api"),
    path("api/desire_todos/complete/", complete_desire_todo_api, name="complete_desire_todo_api"),
    path("api/desire_todos/delete/", delete_desire_todo_api, name="delete_desire_todo_api"),
    path("api/desire_todos/edit/", edit_desire_todo_api, name="edit_desire_todo_api"),
    path("api/desire_todos/stats/", get_desire_todo_stats_api, name="get_desire_todo_stats_api"),
    # Vanity相关API路由
    path("api/vanity_tasks/", get_vanity_tasks_api, name="get_vanity_tasks_api"),
    path("api/vanity_tasks/add/", add_vanity_task_api, name="add_vanity_task_api"),
    path("api/vanity_tasks/complete/", complete_vanity_task_api, name="complete_vanity_task_api"),
    path("api/vanity_tasks/stats/", get_vanity_tasks_stats_api, name="get_vanity_tasks_stats_api"),
    path("api/vanity_tasks/delete/", delete_vanity_task_api, name="delete_vanity_task_api"),
    path("api/sponsors/", get_sponsors_api, name="get_sponsors_api"),
    path("api/sponsors/add/", add_sponsor_api, name="add_sponsor_api"),
    # Based Dev相关API路由
    path("api/based_dev_avatar/create/", create_based_dev_avatar_api, name="create_based_dev_avatar_api"),
    path("api/based_dev_avatar/get/", get_based_dev_avatar_api, name="get_based_dev_avatar_api"),
    path("api/based_dev_avatar/update_stats/", update_based_dev_stats_api, name="update_based_dev_stats_api"),
    path("api/based_dev_avatar/like/", like_based_dev_avatar_api, name="like_based_dev_avatar_api"),
    path("api/based_dev_avatar/achievements/", get_based_dev_achievements_api, name="get_based_dev_achievements_api"),
    # Douyin相关API路由 - 已隐藏
    # path('api/douyin_analysis/', douyin_analysis_api, name='douyin_analysis_api'),
    # path('api/douyin_analysis/result/', get_douyin_analysis_api, name='get_douyin_analysis_api'),
    # path('api/douyin_analysis/preview/', generate_product_preview_api, name='generate_product_preview_api'),
    # path('api/douyin_analysis/list/', get_douyin_analysis_list_api, name='get_douyin_analysis_list_api'),
    # Social Subscription相关API路由
    path("api/social_subscription/add/", add_social_subscription_api, name="add_social_subscription_api"),
    path("api/social_subscription/list/", get_subscriptions_api, name="get_subscriptions_api"),
    path("api/social_subscription/update/", update_subscription_api, name="update_subscription_api"),
    path("api/social_subscription/delete/", delete_subscription_api, name="delete_subscription_api"),
    path("api/social_subscription/notifications/", get_notifications_api, name="get_notifications_api"),
    path("api/social_subscription/mark_read/", mark_notification_read_api, name="mark_notification_read_api"),
    path("api/social_subscription/stats/", get_subscription_stats_api, name="get_subscription_stats_api"),
    
    # 用户ID解析API
    path("api/user_resolver/", UserResolverView.as_view(), name="user_resolver_api"),
    path("api/user_resolver/test/", UserResolverTestView.as_view(), name="user_resolver_test_api"),
    
    # 用户ID解析页面
    path("user_resolver/", lambda request: render(request, 'tools/user_resolver.html'), name="user_resolver_page"),
    # Fitness相关API路由
    path("api/fitness/", fitness_api, name="fitness_api"),
    path("api/fitness_community/follow/", follow_fitness_user_api, name="follow_fitness_user_api"),
    path("api/fitness_community/achievements/", get_fitness_achievements_api, name="get_fitness_achievements_api"),
    path("api/fitness_community/share_achievement/", share_achievement_api, name="share_achievement_api"),
    path("api/fitness_community/profile/", get_fitness_user_profile_api, name="get_fitness_user_profile_api"),
    # 健身工具API路由
    path("api/fitness/bmi/", calculate_bmi_api, name="calculate_bmi_api"),
    path("api/fitness/heart-rate/", calculate_heart_rate_api, name="calculate_heart_rate_api"),
    path("api/fitness/calories/", calculate_calories_api, name="calculate_calories_api"),
    path("api/fitness/protein/", calculate_protein_api, name="calculate_protein_api"),
    path("api/fitness/water/", calculate_water_api, name="calculate_water_api"),
    path("api/fitness/rm/", calculate_rm_api, name="calculate_rm_api"),
    path("api/fitness/one-rm/", calculate_one_rm_api, name="calculate_one_rm_api"),
    path("api/fitness/predict-reps/", predict_reps_api, name="predict_reps_api"),
    path("api/fitness/pace/", calculate_pace_api, name="calculate_pace_api"),
    path("api/fitness/body-composition/", calculate_body_composition_api, name="calculate_body_composition_api"),
    path("api/fitness/workout/save/", save_workout_record_api, name="save_workout_record_api"),
    path("api/fitness/workout/records/", get_workout_records_api, name="get_workout_records_api"),
    # Mode相关API路由
    path("api/mode/record_click/", record_mode_click_api, name="record_mode_click_api"),
    path("api/mode/preferred/", get_user_preferred_mode_api, name="get_user_preferred_mode_api"),
    # 主题切换API路由
    path("api/theme/switch/", switch_theme_api, name="switch_theme_api"),
    path("api/theme/get/", get_user_theme_api, name="get_user_theme_api"),
    path("api/theme/save/", save_user_theme_api, name="save_user_theme_api"),
    path("api/theme/test/", test_theme_api, name="test_theme_api"),
    # Triple Awakening相关API路由
    path("api/triple_awakening/fitness_workout/", create_fitness_workout_api, name="create_fitness_workout_api"),
    path("api/triple_awakening/code_workout/", create_code_workout_api, name="create_code_workout_api"),
    path("api/triple_awakening/complete_task/", complete_daily_task_api, name="complete_daily_task_api"),
    path("api/triple_awakening/workout_dashboard/", get_workout_dashboard_api, name="get_workout_dashboard_api"),
    path("api/triple_awakening/ai_dependency/", get_ai_dependency_api, name="get_ai_dependency_api"),
    path("api/triple_awakening/pain_currency/", get_pain_currency_api, name="get_pain_currency_api"),
    path("api/triple_awakening/record_audio/", record_exhaustion_audio_api, name="record_exhaustion_audio_api"),
    path("api/triple_awakening/exhaustion_proof/", create_exhaustion_proof_api, name="create_exhaustion_proof_api"),
    path(
        "api/triple_awakening/copilot_collaboration/",
        create_copilot_collaboration_api,
        name="create_copilot_collaboration_api",
    ),
    # Emo Diary相关API路由
    path("api/emo_diary/", emo_diary_api, name="emo_diary_api"),
    # Creative Writer相关API路由
    path("api/creative_writer/", creative_writer_api, name="creative_writer_api"),
    # Storyboard相关API路由
    path("api/storyboard/", storyboard_api, name="storyboard_api"),
    # Self Analysis相关API路由
    path("api/self-analysis/", self_analysis_api, name="self_analysis_api"),
    # PDF Converter相关API路由
    path("api/pdf-converter/", pdf_converter_api, name="pdf_converter_api"),
    path("api/pdf-converter/status/", pdf_converter_status_api, name="pdf_converter_status"),
    path("api/pdf-converter/stats/", pdf_converter_stats_api, name="pdf_converter_stats_api"),
    path("api/pdf-converter/rating/", pdf_converter_rating_api, name="pdf_converter_rating_api"),
    path("api/pdf-converter/batch/", pdf_converter_batch, name="pdf_converter_batch"),
    path("api/pdf-converter/download/<str:filename>/", pdf_download_view, name="pdf_download_view"),
    # 签到相关API
    path("api/checkin/calendar/", get_checkin_calendar_api, name="checkin_calendar_api"),
    # 数字匹配API
    path("api/number-match/", number_match_api, name="number_match_api"),
    path("api/number-match/cancel/", cancel_number_match_api, name="cancel_number_match_api"),
    path("api/checkin/add/", checkin_add_api, name="checkin_add_api"),
    path("api/checkin/delete/", checkin_delete_api_simple, name="checkin_delete_api_simple"),  # 添加不带参数的版本
    path("api/checkin/delete/<int:checkin_id>/", checkin_delete_api, name="checkin_delete_api"),
    # 塔罗牌相关API
    path("api/tarot/initialize-data/", initialize_tarot_data_api, name="initialize_tarot_data_api"),
    path("api/tarot/spreads/", tarot_spreads_api, name="tarot_spreads_api"),
    path("api/tarot/create-reading/", tarot_create_reading_api, name="tarot_create_reading_api"),
    path("api/tarot/readings/", tarot_readings_api, name="tarot_readings_api"),
    path("api/tarot/reading/<int:reading_id>/", tarot_reading_detail_api, name="tarot_reading_detail_api"),
    path("api/tarot/reading/<int:reading_id>/feedback/", tarot_feedback_api, name="tarot_feedback_api"),
    path("api/tarot/daily-energy/", tarot_daily_energy_api, name="tarot_daily_energy_api"),
    # 冥想音频API
    path("api/meditation-audio/", meditation_audio_api, name="meditation_audio_api"),
    # 食物随机选择器API
    path("api/food-randomizer/pure-random/", food_randomizer_pure_random_api, name="food_randomizer_pure_random_api"),
    path("api/food-randomizer/statistics/", food_randomizer_statistics_api, name="food_randomizer_statistics_api"),
    path("api/food-randomizer/history/", food_randomizer_history_api, name="food_randomizer_history_api"),
    path("api/food-randomizer/rate/", food_randomizer_rate_api, name="food_randomizer_rate_api"),
    # 食品图像识别API
    # 音频转换器API
    path("api/audio_converter/", audio_converter_api, name="audio_converter_api"),
    # 好心人攻略API
    path("api/user_generated_travel_guide/", user_generated_travel_guide_api, name="user_generated_travel_guide_api"),
    path(
        "api/user_generated_travel_guide/<int:guide_id>/",
        user_generated_travel_guide_detail_api,
        name="user_generated_travel_guide_detail_api",
    ),
    path(
        "api/user_generated_travel_guide/<int:guide_id>/download/",
        user_generated_travel_guide_download_api,
        name="user_generated_travel_guide_download_api",
    ),
    path(
        "api/user_generated_travel_guide/<int:guide_id>/use/",
        user_generated_travel_guide_use_api,
        name="user_generated_travel_guide_use_api",
    ),
    path(
        "api/user_generated_travel_guide/<int:guide_id>/upload_attachment/",
        user_generated_travel_guide_upload_attachment_api,
        name="user_generated_travel_guide_upload_attachment_api",
    ),
    # Food相关API路由（已合并到上面的食物相关API路由部分）
    # MeeSomeone相关API路由
    path("api/meetsomeone/dashboard-stats/", get_dashboard_stats_api, name="get_dashboard_stats_api"),
    path("api/meetsomeone/relationship-tags/", get_relationship_tags_api, name="get_relationship_tags_api"),
    path("api/meetsomeone/person-profiles/", get_person_profiles_api, name="get_person_profiles_api"),
    path("api/meetsomeone/person-profiles/create/", create_person_profile_api, name="create_person_profile_api"),
    path("api/meetsomeone/interactions/", get_interactions_api, name="get_interactions_api"),
    path("api/meetsomeone/interactions/create/", create_interaction_api, name="create_interaction_api"),
    path("api/meetsomeone/moments/create/", create_important_moment_api, name="create_important_moment_api"),
    path("api/meetsomeone/timeline/", get_timeline_data_api, name="get_timeline_data_api"),
    path("api/meetsomeone/graph/", get_graph_data_api, name="get_graph_data_api"),
    # Food Image Crawler和Food List相关API路由（已合并到上面的食物相关API路由部分）
    # Food Image Compare相关API路由 (已删除不存在的函数)
    # path('api/compare-food-images/', compare_food_images_api, name='compare_food_images_api'),
    # Food Image Update相关API路由 (已删除不存在的函数)
    # path('api/update-food-image/', update_food_image_api, name='update_food_image_api'),
    # Photos相关API路由
    path("api/photos/", api_photos, name="api_photos"),
    # 吉他训练系统API路由
    path("api/guitar/start-practice/", start_practice_session_api, name="start_practice_session_api"),
    path("api/guitar/complete-practice/", complete_practice_session_api, name="complete_practice_session_api"),
    path("api/guitar/stats/", get_practice_stats_api, name="get_practice_stats_api"),
    path("api/guitar/recommendations/", get_recommended_exercises_api, name="get_recommended_exercises_api"),
    # 自动扒谱系统路由
    path("guitar-tab-generator/", guitar_tab_generator, name="guitar_tab_generator"),
    path("api/guitar/upload-audio/", upload_audio_for_tab_api, name="upload_audio_for_tab_api"),
    path("api/guitar/generate-tab/", generate_tab_api, name="generate_tab_api"),
    path("api/guitar/tab-history/", get_tab_history_api, name="get_tab_history_api"),
    path("api/guitar/download-tab/<str:tab_id>/", download_tab_api, name="download_tab_api"),
    # 增强代理系统API路由 - 核心功能 + 新增功能
    path("api/proxy/ip-comparison/", get_ip_comparison_api, name="get_ip_comparison_api"),  # 核心功能1: IP对比
    path("api/proxy/setup/", setup_proxy_api, name="setup_proxy_api"),  # 核心功能2: 一键代理设置
    path("api/proxy/list/", proxy_list_api, name="proxy_list_api"),  # 辅助功能: 代理列表
    path("api/proxy/create-url/", create_proxy_url_api, name="create_proxy_url_api"),  # 辅助功能: 创建访问链接
    path("api/proxy/download-clash/", download_clash_config_api, name="download_clash_config_api"),  # 新功能: 下载Clash配置
    path("api/proxy/download-v2ray/", download_v2ray_config_api, name="download_v2ray_config_api"),  # 新功能: 下载V2Ray配置
    path("api/proxy/web-browse/", web_proxy_api, name="web_proxy_api"),  # 新功能: Web代理浏览
    path("api/proxy/browse/", web_proxy_browse_api, name="web_proxy_browse_api"),  # 内嵌代理浏览API
    path("proxy/browse/", proxy_browse_view, name="proxy_browse_view"),  # 代理浏览页面
    # Clash内嵌代理系统路由
    path("clash-dashboard/", clash_dashboard, name="clash_dashboard"),
    path("api/clash/status/", clash_status_api, name="clash_status_api"),
    path("api/clash/start/", clash_start_api, name="clash_start_api"),
    path("api/clash/stop/", clash_stop_api, name="clash_stop_api"),
    path("api/clash/restart/", clash_restart_api, name="clash_restart_api"),
    path("api/clash/test-connection/", clash_test_connection_api, name="clash_test_connection_api"),
    path("api/clash/proxy-info/", clash_proxy_info_api, name="clash_proxy_info_api"),
    path("api/clash/switch-proxy/", clash_switch_proxy_api, name="clash_switch_proxy_api"),
    path("api/clash/install/", clash_install_api, name="clash_install_api"),
    path("api/clash/config/", clash_config_api, name="clash_config_api"),
    path("api/clash/update-config/", clash_update_config_api, name="clash_update_config_api"),
    path("api/clash/configure-proxy/", clash_configure_proxy_api, name="clash_configure_proxy_api"),
    path("api/clash/test-external-access/", clash_test_external_access_api, name="clash_test_external_access_api"),
    path("api/clash/disable-proxy/", clash_disable_proxy_api, name="clash_disable_proxy_api"),
    path("api/clash/add-proxy/", clash_add_proxy_api, name="clash_add_proxy_api"),
    path("api/clash/remove-proxy/", clash_remove_proxy_api, name="clash_remove_proxy_api"),
    path("api/clash/proxy-health/", clash_proxy_health_api, name="clash_proxy_health_api"),
    path("api/clash/auto-setup/", clash_auto_setup_api, name="clash_auto_setup_api"),
    # 远程ClashX Pro管理路由
    path("api/clash/remote-start/", remote_start_clashx_api, name="remote_start_clashx_api"),
    path("api/clash/download-config/", download_clash_config_api, name="download_clash_config_api"),
    path("api/clash/download-script/", download_start_script_api, name="download_start_script_api"),
    # 浏览器代理配置路由
    path("api/browser-proxy/configure/", configure_browser_proxy, name="configure_browser_proxy"),
    path("api/browser-proxy/disable/", disable_browser_proxy, name="disable_browser_proxy"),
    path("api/browser-proxy/status/", get_proxy_status, name="get_proxy_status"),
    path("api/browser-proxy/quick-setup/", quick_proxy_setup, name="quick_proxy_setup"),
    path("api/proxy/test-connection/", test_proxy_connection, name="test_proxy_connection"),
    # 健身营养定制系统路由 - 已隐藏
    # path('nutrition-dashboard/', nutrition_dashboard, name='nutrition_dashboard'),
    # path('nutrition-profile-setup/', nutrition_profile_setup, name='nutrition_profile_setup'),
    # path('nutrition-generate-plan/', nutrition_generate_plan, name='nutrition_generate_plan'),
    # path('nutrition-meal-log/', nutrition_meal_log, name='nutrition_meal_log'),
    # path('nutrition-weight-tracking/', nutrition_weight_tracking, name='nutrition_weight_tracking'),
    # path('nutrition-reminders/', nutrition_reminders, name='nutrition_reminders'),
    # path('nutrition-progress/', nutrition_progress, name='nutrition_progress'),
    # path('nutrition-settings/', nutrition_settings, name='nutrition_settings'),
    # 健身营养定制系统API路由 - 已隐藏
    # path('api/nutrition/generate-plan/', nutrition_api_generate_plan, name='nutrition_api_generate_plan'),
    # 监控系统路由
    path("monitoring/", monitoring_dashboard, name="monitoring_dashboard"),
    path("monitoring/data/", get_monitoring_data, name="get_monitoring_data"),
    path("monitoring/system/", get_system_metrics, name="get_system_metrics"),
    path("monitoring/alerts/", get_alerts, name="get_alerts"),
    path("monitoring/cache/", get_cache_stats, name="get_cache_stats"),
    path("monitoring/clear-cache/", clear_cache, name="clear_cache"),
    path("monitoring/warm-cache/", warm_up_cache, name="warm_up_cache"),
    path("monitoring/api/<str:type>/", MonitoringAPIView.as_view(), name="monitoring_api"),
    path("monitoring/api/<str:action>/", MonitoringAPIView.as_view(), name="monitoring_action"),
    # ==================== 船宝（二手线下交易）相关路由 ====================
    path("shipbao/", shipbao_home, name="shipbao_home"),
    path("shipbao/publish/", shipbao_publish, name="shipbao_publish"),
    path("shipbao/item/<int:item_id>/", shipbao_detail, name="shipbao_detail"),
    path("shipbao/transactions/", shipbao_transactions, name="shipbao_transactions"),
    path("shipbao/chat/<int:transaction_id>/", shipbao_chat, name="shipbao_chat"),
    # 船宝API路由
    path("api/shipbao/create-item/", shipbao_create_item_api, name="shipbao_create_item_api"),
    path("api/shipbao/items/", shipbao_items_api, name="shipbao_items_api"),
    path("api/shipbao/favorites/", shipbao_favorites_api, name="shipbao_favorites_api"),
    path("api/shipbao/initiate-transaction/", shipbao_initiate_transaction_api, name="shipbao_initiate_transaction_api"),
    path("api/shipbao/check-transaction/", shipbao_check_transaction_api, name="shipbao_check_transaction_api"),
    path("api/shipbao/contact-seller/", shipbao_contact_seller_api, name="shipbao_contact_seller_api"),
    path("api/shipbao/inquiry-queue/<int:item_id>/", shipbao_inquiry_queue_api, name="shipbao_inquiry_queue_api"),
    path("api/shipbao/want-item/", shipbao_want_item_api, name="shipbao_want_item_api"),
    path("api/shipbao/want-list/<int:item_id>/", shipbao_want_list_api, name="shipbao_want_list_api"),
    path("api/shipbao/contact-wanter/", shipbao_contact_wanter_api, name="shipbao_contact_wanter_api"),
    path("api/shipbao/remove-item/", shipbao_remove_item_api, name="shipbao_remove_item_api"),
    path("api/shipbao/mark-sold/", shipbao_mark_sold_api, name="shipbao_mark_sold_api"),
    path(
        "api/shipbao/transaction-status/<int:item_id>/", shipbao_transaction_status_api, name="shipbao_transaction_status_api"
    ),
    path("api/user/save-location/", save_user_location_api, name="save_user_location_api"),
    # ==================== 地图API相关路由 ====================
    path("api/map/search-location/", map_search_location_api, name="map_search_location_api"),
    path("api/map/reverse-geocode/", map_reverse_geocode_api, name="map_reverse_geocode_api"),
    path("api/map/geocode/", map_geocode_api, name="map_geocode_api"),
    # ==================== 搭子（同城活动匹配）相关路由 ====================
    path("buddy/", buddy_home, name="buddy_home"),
    path("buddy/create/", buddy_create, name="buddy_create"),
    path("buddy/event/<int:event_id>/", buddy_detail, name="buddy_detail"),
    path("buddy/manage/", buddy_manage, name="buddy_manage"),
    path("buddy/chat/<int:event_id>/", buddy_chat, name="buddy_chat"),
    # 搭子API路由
    path("api/buddy/create-event/", buddy_create_event_api, name="buddy_create_event_api"),
    path("api/buddy/events/", buddy_events_api, name="buddy_events_api"),
    path("api/buddy/join-event/", buddy_join_event_api, name="buddy_join_event_api"),
    path("api/buddy/approve-member/", buddy_approve_member_api, name="buddy_approve_member_api"),
    path("api/buddy/send-message/", buddy_send_message_api, name="buddy_send_message_api"),
    path("api/buddy/messages/", buddy_messages_api, name="buddy_messages_api"),
    # 健康检查相关URL
    path("health/", health_check, name="health_check"),
    path("health/legacy/", legacy_health_check, name="legacy_health_check"),
    path("health/detailed/", detailed_health_check, name="detailed_health_check"),
    # path("health/class/", HealthCheckView.as_view(), name="health_check_class"),
    # 新增的健康检查端点（用于零停机部署）
    path("health/readiness/", readiness_check, name="readiness_check"),
    path("health/liveness/", liveness_check, name="liveness_check"),
    path("health/metrics/", metrics_endpoint, name="metrics_endpoint"),
    # 自动化测试相关URL
    # path("auto-test/status/", auto_test_status, name="auto_test_status"),
    # path("auto-test/run/", run_auto_tests, name="run_auto_tests"),
    # 系统状态相关URL
    # path("system/status/", system_status, name="system_status"),
    # path("system/performance/", performance_status, name="performance_status"),
    # path("system/shards/", shard_status, name="shard_status"),
    # ZIP文件处理工具路由
    path("zip-tool/", zip_tool_view, name="zip_tool"),
    path("api/zip/create-from-files/", create_zip_from_files_api, name="create_zip_from_files_api"),
    path("api/zip/create-from-uploaded-files/", create_zip_from_uploaded_files_api, name="create_zip_from_uploaded_files_api"),
    path("api/zip/create-from-directory/", create_zip_from_directory_api, name="create_zip_from_directory_api"),
    path("api/zip/compress-single/", compress_single_file_api, name="compress_single_file_api"),
    path("api/zip/compress-uploaded-file/", compress_uploaded_file_api, name="compress_uploaded_file_api"),
    path("api/zip/extract/", extract_zip_api, name="extract_zip_api"),
    path("api/zip/info/", get_zip_info_api, name="get_zip_info_api"),
    path("api/zip/download/<path:file_path>/", download_zip_file, name="download_zip_file"),
    # Token管理和跨标签页同步API路由
    path("api/token/save/", save_boss_token_api, name="save_boss_token_api"),
    path("api/token/get/", get_boss_token_api, name="get_boss_token_api"),
    path("api/token/check-login/", check_login_status_api, name="check_login_status_api"),
    path("api/token/sync-session/", sync_session_api, name="sync_session_api"),
    path("api/token/get-all/", get_all_tokens_api, name="get_all_tokens_api"),
    path("api/token/clear/", clear_token_api, name="clear_token_api"),
    path("api/token/test-login/", test_boss_login_api, name="test_boss_login_api"),
    path("api/token/cross-tab-sync/", cross_tab_sync_api, name="cross_tab_sync_api"),
    # Token同步测试页面
    path("cross-tab-token-test/", lambda request: render(request, 'tools/cross_tab_token_test.html'), name="cross_tab_token_test"),
    path("token-test-simple/", lambda request: render(request, 'tools/token_test_simple.html'), name="token_test_simple"),
    # 通用文件下载路由
    path("download/<str:filename>/", generic_file_download, name="generic_file_download"),
    # API版本控制
    # path('api/v1/', include('apps.tools.services.api_version_control')),  # 临时注释
    # WebSocket路由在 routing.py 中配置，不在这里
    # 聊天相关API
    path("api/chat/<str:room_id>/send-audio/", send_audio_api, name="send_audio_api"),
    path("api/chat/<str:room_id>/send-file/", send_file_api, name="send_file_api"),
    path("api/chat/<str:room_id>/send-image/", send_image_api, name="send_image_api"),
    # enhanced_fitness_center 相关路由已删除
    path("api/fitness/training-plan-templates/", get_training_plan_templates_api, name="get_training_plan_templates_api"),
    # 训练模式导入API
    path("api/fitness/training-modes/", get_training_modes_api, name="get_training_modes_api"),
    path("api/fitness/import-training-mode/", import_training_mode_api, name="import_training_mode_api"),
    # AI助手相关API路由
    path("api/ai-assistant/", ai_assistant_api, name="ai_assistant_api"),
    path("api/ai-assistant/features/", ai_assistant_features_api, name="ai_assistant_features_api"),
    # Trojan代理服务相关路由
    path("trojan/", TrojanDashboardView.as_view(), name="trojan_dashboard"),
    path("trojan/dashboard/", TrojanDashboardView.as_view(), name="trojan_dashboard"),
    path("trojan/config/", TrojanConfigView.as_view(), name="trojan_config"),
    path("trojan/config/download/<str:config_type>/", TrojanConfigDownloadView.as_view(), name="trojan_config_download"),
    path("trojan/stats/", TrojanUsageStatsView.as_view(), name="trojan_usage_stats"),
    path("trojan/auth/", TrojanAuthView.as_view(), name="trojan_auth"),
    path("trojan/auth/google/", TrojanGoogleAuthView.as_view(), name="trojan_google_auth"),
    path("trojan/auth/google/callback/", TrojanGoogleCallbackView.as_view(), name="trojan_google_callback"),
    path("trojan/admin/", TrojanAdminView.as_view(), name="trojan_admin"),
    path("trojan/refresh/", refresh_trojan_config, name="trojan_refresh"),
    path("trojan/revoke/", revoke_trojan_access, name="trojan_revoke"),
    path("trojan/restore/", restore_trojan_access, name="trojan_restore"),
    path("trojan/server/<str:action>/", trojan_server_control, name="trojan_server_control"),
    path("trojan/report/", trojan_usage_report, name="trojan_usage_report"),
    
    # 分析功能路由
    
    # 分析API路由
    
    # Cookie 管理相关路由
    path("api/cookies/save/", save_cookies_api, name="save_cookies_api"),
    path("api/cookies/get/", get_cookies_api, name="get_cookies_api"),
    path("api/cookies/validate/", validate_cookies_api, name="validate_cookies_api"),
    path("api/cookies/info/", get_cookies_info_api, name="get_cookies_info_api"),
    path("api/cookies/clear/", clear_cookies_api, name="clear_cookies_api"),
    
    # Playwright Token管理API路由（简化版）
    path("api/playwright/save-token/", save_token_api, name="save_token_api"),
    path("api/playwright/get-token/", get_token_api, name="get_token_api"),
    path("api/playwright/check-login/", check_login_status_api, name="check_login_status_api"),
    path("api/playwright/clear-token/", clear_token_api, name="clear_token_api"),
    path("api/playwright/test/", test_playwright_api, name="test_playwright_api"),
    
    # 增强版Playwright API路由
    path("api/playwright/scan-login/", playwright_scan_login_api, name="playwright_scan_login_api"),
    path("api/playwright/login-status/", playwright_login_status_api, name="playwright_login_status_api"),
    path("api/playwright/get-qr-code/", playwright_get_qr_code_api, name="playwright_get_qr_code_api"),
    path("api/playwright/quick-check/", playwright_quick_login_check_api, name="playwright_quick_login_check_api"),
    
    # Playwright Token测试页面
    path("playwright-token-test/", playwright_token_test_view, name="playwright_token_test"),
    
    # 测试路由已移除
]
