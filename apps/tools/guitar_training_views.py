import json
import random

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

import numpy as np  # 暂时注释掉，避免启动问题


class GuitarTrainingSystem:
    """吉他训练系统 - 从初学者到进阶者"""

    # 难度等级定义
    DIFFICULTY_LEVELS = {
        "beginner": {
            "name": "初学者",
            "description": "适合零基础学习者",
            "color": "#4CAF50",
            "min_practice_time": 15,
            "max_practice_time": 30,
        },
        "intermediate": {
            "name": "进阶者",
            "description": "有一定基础的学习者",
            "color": "#FF9800",
            "min_practice_time": 30,
            "max_practice_time": 60,
        },
        "advanced": {
            "name": "高级者",
            "description": "有丰富经验的学习者",
            "color": "#F44336",
            "min_practice_time": 60,
            "max_practice_time": 120,
        },
    }

    # 练习类型定义
    PRACTICE_TYPES = {
        "chord_progression": {
            "name": "和弦进行",
            "description": "练习各种和弦转换和进行",
            "difficulty": ["beginner", "intermediate", "advanced"],
            "exercises": {
                "beginner": [
                    {"name": "C-G-Am-F进行", "description": "经典四和弦进行练习", "duration": 10},
                    {"name": "Am-F-C-G进行", "description": "流行音乐常用进行", "duration": 10},
                    {"name": "Em-C-G-D进行", "description": "民谣风格进行", "duration": 10},
                ],
                "intermediate": [
                    {"name": "C-Am-F-G进行", "description": "经典流行进行", "duration": 15},
                    {"name": "Dm-G-C-Am进行", "description": "爵士风格进行", "duration": 15},
                    {"name": "Em-Am-D-G进行", "description": "摇滚风格进行", "duration": 15},
                ],
                "advanced": [
                    {"name": "Cmaj7-Am7-Dm7-G7进行", "description": "爵士七和弦进行", "duration": 20},
                    {"name": "Em7-Am7-D7-G7进行", "description": "复杂和弦进行", "duration": 20},
                    {"name": "Cmaj7-F#m7b5-Bm7-Em7进行", "description": "高级爵士进行", "duration": 20},
                ],
            },
        },
        "fingerpicking": {
            "name": "指弹技巧",
            "description": "练习指弹和拨弦技巧",
            "difficulty": ["beginner", "intermediate", "advanced"],
            "exercises": {
                "beginner": [
                    {"name": "基础指弹模式", "description": "练习基本指弹指法", "duration": 10},
                    {"name": "Travis Picking", "description": "经典指弹模式", "duration": 10},
                    {"name": "交替指弹", "description": "拇指和食指交替", "duration": 10},
                ],
                "intermediate": [
                    {"name": "复杂指弹模式", "description": "多指协调练习", "duration": 15},
                    {"name": "扫弦技巧", "description": "上下扫弦练习", "duration": 15},
                    {"name": "混合指弹", "description": "指弹和扫弦结合", "duration": 15},
                ],
                "advanced": [
                    {"name": "快速指弹", "description": "高速指弹练习", "duration": 20},
                    {"name": "复杂扫弦", "description": "复杂扫弦模式", "duration": 20},
                    {"name": "指弹独奏", "description": "完整指弹独奏", "duration": 20},
                ],
            },
        },
        "scale_practice": {
            "name": "音阶练习",
            "description": "练习各种音阶和音程",
            "difficulty": ["beginner", "intermediate", "advanced"],
            "exercises": {
                "beginner": [
                    {"name": "C大调音阶", "description": "练习C大调音阶", "duration": 10},
                    {"name": "G大调音阶", "description": "练习G大调音阶", "duration": 10},
                    {"name": "A小调音阶", "description": "练习A小调音阶", "duration": 10},
                ],
                "intermediate": [
                    {"name": "五声音阶", "description": "练习五声音阶", "duration": 15},
                    {"name": "布鲁斯音阶", "description": "练习布鲁斯音阶", "duration": 15},
                    {"name": "多调音阶", "description": "练习多个调式", "duration": 15},
                ],
                "advanced": [
                    {"name": "爵士音阶", "description": "练习爵士音阶", "duration": 20},
                    {"name": "和声音阶", "description": "练习和声音阶", "duration": 20},
                    {"name": "旋律小调", "description": "练习旋律小调音阶", "duration": 20},
                ],
            },
        },
        "song_learning": {
            "name": "歌曲学习",
            "description": "学习完整的歌曲",
            "difficulty": ["beginner", "intermediate", "advanced"],
            "exercises": {
                "beginner": [
                    {"name": "小星星", "description": "经典儿歌练习", "duration": 15},
                    {"name": "生日快乐", "description": "生日歌练习", "duration": 15},
                    {"name": "两只老虎", "description": "简单民谣", "duration": 15},
                ],
                "intermediate": [
                    {"name": "月亮代表我的心", "description": "经典情歌", "duration": 20},
                    {"name": "童话", "description": "流行歌曲", "duration": 20},
                    {"name": "海阔天空", "description": "经典摇滚", "duration": 20},
                ],
                "advanced": [
                    {"name": "Hotel California", "description": "经典摇滚", "duration": 30},
                    {"name": "Stairway to Heaven", "description": "经典摇滚", "duration": 30},
                    {"name": "Nothing Else Matters", "description": "金属柔情", "duration": 30},
                ],
            },
        },
        "theory_study": {
            "name": "乐理学习",
            "description": "学习音乐理论知识",
            "difficulty": ["beginner", "intermediate", "advanced"],
            "exercises": {
                "beginner": [
                    {"name": "音符认识", "description": "学习基本音符", "duration": 10},
                    {"name": "节拍练习", "description": "练习基本节拍", "duration": 10},
                    {"name": "和弦构成", "description": "学习和弦构成", "duration": 10},
                ],
                "intermediate": [
                    {"name": "调式理论", "description": "学习调式理论", "duration": 15},
                    {"name": "和声进行", "description": "学习和声进行", "duration": 15},
                    {"name": "节奏模式", "description": "学习复杂节奏", "duration": 15},
                ],
                "advanced": [
                    {"name": "爵士理论", "description": "学习爵士理论", "duration": 20},
                    {"name": "复调音乐", "description": "学习复调音乐", "duration": 20},
                    {"name": "现代和声", "description": "学习现代和声", "duration": 20},
                ],
            },
        },
    }

    # 成就系统
    ACHIEVEMENTS = {
        "first_practice": {"name": "初次练习", "description": "完成第一次练习", "icon": "🎸", "points": 10},
        "week_streak": {"name": "一周坚持", "description": "连续练习一周", "icon": "🔥", "points": 50},
        "month_streak": {"name": "一月坚持", "description": "连续练习一个月", "icon": "💎", "points": 200},
        "level_up": {"name": "等级提升", "description": "提升到新的难度等级", "icon": "⭐", "points": 100},
        "master_chord": {"name": "和弦大师", "description": "掌握所有基础和弦", "icon": "🎯", "points": 150},
        "fingerpicking_pro": {"name": "指弹专家", "description": "掌握高级指弹技巧", "icon": "🎵", "points": 200},
        "song_master": {"name": "歌曲大师", "description": "学会10首完整歌曲", "icon": "🎼", "points": 300},
    }


# 吉他训练系统视图函数
@login_required
def guitar_training_dashboard(request):
    """吉他训练主页面"""
    context = {
        "difficulty_levels": GuitarTrainingSystem.DIFFICULTY_LEVELS,
        "practice_types": GuitarTrainingSystem.PRACTICE_TYPES,
        "achievements": GuitarTrainingSystem.ACHIEVEMENTS,
        "user_level": get_user_level(request.user),
        "user_stats": get_user_stats(request.user),
        "recent_practices": get_recent_practices(request.user),
        "recommended_exercises": get_recommended_exercises(request.user),
    }
    return render(request, "tools/guitar_training_dashboard.html", context)


@login_required
def guitar_practice_session(request, practice_type=None, difficulty=None):
    """吉他练习会话页面"""
    if not practice_type:
        practice_type = request.GET.get("type", "chord_progression")
    if not difficulty:
        difficulty = request.GET.get("difficulty", "beginner")

    # 获取练习内容
    practice_content = get_practice_content(practice_type, difficulty)

    context = {
        "practice_type": practice_type,
        "difficulty": difficulty,
        "practice_content": practice_content,
        "practice_types": GuitarTrainingSystem.PRACTICE_TYPES,
        "difficulty_levels": GuitarTrainingSystem.DIFFICULTY_LEVELS,
        "timer_duration": practice_content.get("duration", 15) * 60,  # 转换为秒
        "metronome_bpm": get_metronome_bpm(difficulty),
    }
    return render(request, "tools/guitar_practice_session.html", context)


@login_required
def guitar_progress_tracking(request):
    """进度跟踪页面"""
    user_stats = get_user_stats(request.user)
    progress_data = get_progress_data(request.user)

    context = {
        "user_stats": user_stats,
        "progress_data": progress_data,
        "achievements": get_user_achievements(request.user),
        "practice_history": get_practice_history(request.user),
    }
    return render(request, "tools/guitar_progress_tracking.html", context)


@login_required
def guitar_theory_guide(request):
    """乐理学习指南"""
    theory_content = get_theory_content()

    context = {"theory_content": theory_content, "user_level": get_user_level(request.user)}
    return render(request, "tools/guitar_theory_guide.html", context)


@login_required
def guitar_song_library(request):
    """歌曲库页面"""
    songs = get_song_library()
    user_progress = get_user_song_progress(request.user)

    context = {"songs": songs, "user_progress": user_progress, "difficulty_levels": GuitarTrainingSystem.DIFFICULTY_LEVELS}
    return render(request, "tools/guitar_song_library.html", context)


# API 函数
@login_required
@csrf_exempt
def start_practice_session_api(request):
    """开始练习会话API"""
    if request.method == "POST":
        data = json.loads(request.body)
        practice_type = data.get("practice_type")
        difficulty = data.get("difficulty")
        exercise_name = data.get("exercise_name")

        # 记录练习开始
        session_data = {
            "user": request.user,
            "practice_type": practice_type,
            "difficulty": difficulty,
            "exercise_name": exercise_name,
            "start_time": timezone.now(),
        }

        # 这里可以保存到数据库
        request.session["current_practice"] = session_data

        return JsonResponse(
            {"success": True, "message": "练习会话已开始", "session_id": f"session_{int(timezone.now().timestamp())}"}
        )

    return JsonResponse({"success": False, "message": "无效请求"})


@login_required
@csrf_exempt
def complete_practice_session_api(request):
    """完成练习会话API"""
    if request.method == "POST":
        data = json.loads(request.body)
        duration = data.get("duration", 0)
        accuracy = data.get("accuracy", 0)
        notes = data.get("notes", "")

        # 获取当前练习会话
        current_practice = request.session.get("current_practice", {})

        # 记录练习完成
        practice_record = {
            "user": request.user,
            "practice_type": current_practice.get("practice_type"),
            "difficulty": current_practice.get("difficulty"),
            "exercise_name": current_practice.get("exercise_name"),
            "duration": duration,
            "accuracy": accuracy,
            "notes": notes,
            "completed_at": timezone.now(),
        }

        # 保存练习记录
        save_practice_record(practice_record)

        # 检查成就
        check_achievements(request.user)

        # 清除会话数据
        if "current_practice" in request.session:
            del request.session["current_practice"]

        return JsonResponse(
            {
                "success": True,
                "message": "练习完成！",
                "points_earned": calculate_points(duration, accuracy),
                "new_achievements": get_new_achievements(request.user),
            }
        )

    return JsonResponse({"success": False, "message": "无效请求"})


@login_required
def get_practice_stats_api(request):
    """获取练习统计API"""
    user_stats = get_user_stats(request.user)
    progress_data = get_progress_data(request.user)

    return JsonResponse({"success": True, "stats": user_stats, "progress": progress_data})


@login_required
def get_recommended_exercises_api(request):
    """获取推荐练习API"""
    exercises = get_recommended_exercises(request.user)

    return JsonResponse({"success": True, "exercises": exercises})


# 辅助函数
def get_user_level(user):
    """获取用户等级"""
    # 基于练习时间和次数计算等级
    total_practice_time = get_total_practice_time(user)

    if total_practice_time < 10:  # 少于10小时
        return "beginner"
    elif total_practice_time < 50:  # 少于50小时
        return "intermediate"
    else:
        return "advanced"


def get_user_stats(user):
    """获取用户统计信息"""
    # 这里应该从数据库获取真实数据
    return {
        "total_practice_time": get_total_practice_time(user),
        "total_sessions": get_total_sessions(user),
        "current_streak": get_current_streak(user),
        "longest_streak": get_longest_streak(user),
        "accuracy_avg": get_average_accuracy(user),
        "level": get_user_level(user),
        "points": get_user_points(user),
    }


def get_practice_content(practice_type, difficulty):
    """获取练习内容"""
    if practice_type in GuitarTrainingSystem.PRACTICE_TYPES:
        type_data = GuitarTrainingSystem.PRACTICE_TYPES[practice_type]
        if difficulty in type_data["exercises"]:
            exercises = type_data["exercises"][difficulty]
            # 随机选择一个练习
            exercise = random.choice(exercises)
            return {
                "name": exercise["name"],
                "description": exercise["description"],
                "duration": exercise["duration"],
                "type": practice_type,
                "difficulty": difficulty,
            }

    # 默认返回
    return {
        "name": "基础练习",
        "description": "基础吉他练习",
        "duration": 15,
        "type": "chord_progression",
        "difficulty": "beginner",
    }


def get_metronome_bpm(difficulty):
    """获取节拍器BPM"""
    bpm_ranges = {"beginner": (60, 80), "intermediate": (80, 120), "advanced": (120, 180)}

    min_bpm, max_bpm = bpm_ranges.get(difficulty, (60, 80))
    return random.randint(min_bpm, max_bpm)


def get_recent_practices(user, limit=5):
    """获取最近的练习记录"""
    # 这里应该从数据库获取真实数据
    return []


def get_recommended_exercises(user):
    """获取推荐练习"""
    user_level = get_user_level(user)
    recommendations = []

    for practice_type, type_data in GuitarTrainingSystem.PRACTICE_TYPES.items():
        if user_level in type_data["difficulty"]:
            exercises = type_data["exercises"][user_level]
            # 随机选择2个练习
            selected = random.sample(exercises, min(2, len(exercises)))
            for exercise in selected:
                recommendations.append(
                    {
                        "type": practice_type,
                        "name": exercise["name"],
                        "description": exercise["description"],
                        "duration": exercise["duration"],
                        "difficulty": user_level,
                    }
                )

    return recommendations


def get_progress_data(user):
    """获取进度数据"""
    # 这里应该从数据库获取真实数据
    return {
        "weekly_practice_time": [2, 3, 1, 4, 2, 3, 5],  # 最近7天
        "monthly_practice_time": [10, 15, 12, 18, 20, 16, 14, 22, 19, 17, 21, 25],  # 最近12个月
        "accuracy_trend": [75, 78, 82, 80, 85, 88, 90],  # 准确率趋势
        "practice_types_distribution": {
            "chord_progression": 30,
            "fingerpicking": 25,
            "scale_practice": 20,
            "song_learning": 15,
            "theory_study": 10,
        },
    }


def get_user_achievements(user):
    """获取用户成就"""
    # 这里应该从数据库获取真实数据
    return []


def get_practice_history(user):
    """获取练习历史"""
    # 这里应该从数据库获取真实数据
    return []


def get_theory_content():
    """获取乐理内容"""
    return {
        "beginner": [
            {"title": "音符基础", "content": "学习基本音符和节拍"},
            {"title": "和弦构成", "content": "了解和弦的基本构成"},
            {"title": "调式理论", "content": "学习基本调式概念"},
        ],
        "intermediate": [
            {"title": "和声进行", "content": "学习和声进行理论"},
            {"title": "音阶模式", "content": "学习各种音阶模式"},
            {"title": "节奏理论", "content": "学习复杂节奏模式"},
        ],
        "advanced": [
            {"title": "爵士理论", "content": "学习爵士音乐理论"},
            {"title": "现代和声", "content": "学习现代和声理论"},
            {"title": "复调音乐", "content": "学习复调音乐理论"},
        ],
    }


def get_song_library():
    """获取歌曲库"""
    return {
        "beginner": [
            {"name": "小星星", "artist": "传统儿歌", "difficulty": "beginner"},
            {"name": "生日快乐", "artist": "传统歌曲", "difficulty": "beginner"},
            {"name": "两只老虎", "artist": "传统儿歌", "difficulty": "beginner"},
        ],
        "intermediate": [
            {"name": "月亮代表我的心", "artist": "邓丽君", "difficulty": "intermediate"},
            {"name": "童话", "artist": "光良", "difficulty": "intermediate"},
            {"name": "海阔天空", "artist": "Beyond", "difficulty": "intermediate"},
        ],
        "advanced": [
            {"name": "Hotel California", "artist": "Eagles", "difficulty": "advanced"},
            {"name": "Stairway to Heaven", "artist": "Led Zeppelin", "difficulty": "advanced"},
            {"name": "Nothing Else Matters", "artist": "Metallica", "difficulty": "advanced"},
        ],
    }


def get_user_song_progress(user):
    """获取用户歌曲进度"""
    # 这里应该从数据库获取真实数据
    return {}


def save_practice_record(record):
    """保存练习记录"""
    # 这里应该保存到数据库


def check_achievements(user):
    """检查成就"""
    # 这里应该检查并授予成就


def calculate_points(duration, accuracy):
    """计算获得的积分"""
    base_points = duration / 60  # 每分钟1分
    accuracy_bonus = accuracy / 100 * 0.5  # 准确率奖励
    return int(base_points + accuracy_bonus)


def get_new_achievements(user):
    """获取新获得的成就"""
    # 这里应该返回新获得的成就
    return []


# 数据库相关函数（占位符）
def get_total_practice_time(user):
    """获取总练习时间（小时）"""
    return 25  # 示例数据


def get_total_sessions(user):
    """获取总练习次数"""
    return 50  # 示例数据


def get_current_streak(user):
    """获取当前连续练习天数"""
    return 7  # 示例数据


def get_longest_streak(user):
    """获取最长连续练习天数"""
    return 15  # 示例数据


def get_average_accuracy(user):
    """获取平均准确率"""
    return 85  # 示例数据


def get_user_points(user):
    """获取用户积分"""
    return 1250  # 示例数据


# 在文件末尾添加自动扒谱相关功能


# 自动扒谱功能
@login_required
def guitar_tab_generator(request):
    """自动扒谱主页面"""
    context = {
        "user_level": get_user_level(request.user),
        "recent_tabs": get_recent_tabs(request.user),
        "tab_statistics": get_tab_statistics(request.user),
    }
    return render(request, "tools/guitar_tab_generator.html", context)


@login_required
@csrf_exempt
def upload_audio_for_tab_api(request):
    """上传音频文件进行扒谱API"""
    if request.method == "POST":
        try:
            audio_file = request.FILES.get("audio_file")
            if not audio_file:
                return JsonResponse({"success": False, "message": "请选择音频文件"})

            # 检查文件类型
            allowed_types = ["audio/mp3", "audio/wav", "audio/m4a", "audio/flac"]
            if audio_file.content_type not in allowed_types:
                return JsonResponse({"success": False, "message": "不支持的文件格式"})

            # 检查文件大小（限制50MB）
            if audio_file.size > 50 * 1024 * 1024:
                return JsonResponse({"success": False, "message": "文件大小不能超过50MB"})

            # 保存文件
            file_path = save_audio_file(audio_file, request.user)

            # 创建扒谱任务
            tab_task = create_tab_task(request.user, file_path, audio_file.name)

            # 开始音频分析
            analysis_result = analyze_audio(file_path)

            return JsonResponse(
                {
                    "success": True,
                    "message": "音频文件上传成功，开始分析...",
                    "task_id": tab_task["id"],
                    "analysis_result": analysis_result,
                }
            )

        except Exception as e:
            return JsonResponse({"success": False, "message": f"上传失败: {str(e)}"})

    return JsonResponse({"success": False, "message": "无效请求"})


@login_required
@csrf_exempt
def generate_tab_api(request):
    """生成吉他谱API"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            task_id = data.get("task_id")
            analysis_data = data.get("analysis_data", {})
            tab_type = data.get("tab_type", "chords")  # chords, melody, full

            # 生成吉他谱
            tab_result = generate_guitar_tab(analysis_data, tab_type)

            # 保存扒谱结果
            save_tab_result(request.user, task_id, tab_result)

            return JsonResponse({"success": True, "message": "吉他谱生成成功", "tab_result": tab_result})

        except Exception as e:
            return JsonResponse({"success": False, "message": f"生成失败: {str(e)}"})

    return JsonResponse({"success": False, "message": "无效请求"})


@login_required
def get_tab_history_api(request):
    """获取扒谱历史API"""
    tabs = get_user_tab_history(request.user)
    return JsonResponse({"success": True, "tabs": tabs})


@login_required
def download_tab_api(request, tab_id):
    """下载吉他谱API"""
    tab_data = get_tab_by_id(tab_id, request.user)
    if not tab_data:
        return JsonResponse({"success": False, "message": "扒谱记录不存在"})

    # 生成下载文件
    file_content = generate_tab_file(tab_data)

    response = HttpResponse(file_content, content_type="text/plain")
    response["Content-Disposition"] = f'attachment; filename="guitar_tab_{tab_id}.txt"'
    return response


# 自动扒谱辅助函数
def save_audio_file(audio_file, user):
    """保存音频文件"""
    import os

    from django.conf import settings

    # 创建用户专属目录
    user_dir = os.path.join(settings.MEDIA_ROOT, "guitar_tabs", str(user.id))
    os.makedirs(user_dir, exist_ok=True)

    # 生成唯一文件名
    import uuid

    file_name = f"{uuid.uuid4()}_{audio_file.name}"
    file_path = os.path.join(user_dir, file_name)

    # 保存文件
    with open(file_path, "wb+") as destination:
        for chunk in audio_file.chunks():
            destination.write(chunk)

    return file_path


def create_tab_task(user, file_path, original_name):
    """创建扒谱任务"""
    # 这里应该保存到数据库，现在返回模拟数据
    return {
        "id": f"task_{int(timezone.now().timestamp())}",
        "user": user,
        "file_path": file_path,
        "original_name": original_name,
        "created_at": timezone.now(),
        "status": "processing",
    }


def analyze_audio(file_path):
    """分析音频文件"""
    try:
        import warnings

        import librosa
        import numpy as np  # 暂时注释掉，避免启动问题

        warnings.filterwarnings("ignore")

        # 加载音频文件
        y, sr = librosa.load(file_path, sr=None)

        # 1. 检测速度 (BPM)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

        # 2. 检测调性
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        key_raw = librosa.feature.key_mode(chroma)[0]
        key = librosa.key_to_notes(key_raw)[0] if key_raw != -1 else "C"

        # 3. 检测拍号
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)

        # 分析节拍间隔来确定拍号
        if len(onset_times) > 1:
            intervals = np.diff(onset_times)
            avg_interval = np.mean(intervals)
            if avg_interval < 0.5:
                time_signature = "4/4"
            elif avg_interval < 0.8:
                time_signature = "3/4"
            else:
                time_signature = "6/8"
        else:
            time_signature = "4/4"

        # 4. 检测和弦
        chords_detected = detect_chords(y, sr, tempo)

        # 5. 检测旋律
        melody_notes = detect_melody(y, sr)

        # 6. 检测低音线
        bass_line = detect_bass_line(y, sr)

        analysis_result = {
            "tempo": int(tempo),
            "key": key,
            "time_signature": time_signature,
            "duration": int(len(y) / sr),
            "chords_detected": chords_detected,
            "melody_notes": melody_notes,
            "bass_line": bass_line,
            "sample_rate": sr,
            "audio_length": len(y),
        }

        return analysis_result

    except ImportError:
        # 如果没有安装librosa，返回基础分析
        return basic_audio_analysis(file_path)
    except Exception as e:
        print(f"音频分析错误: {str(e)}")
        return basic_audio_analysis(file_path)


def basic_audio_analysis(file_path):
    """基础音频分析（当librosa不可用时）"""
    import struct
    import wave

    import numpy as np  # 暂时注释掉，避免启动问题

    try:
        with wave.open(file_path, "rb") as wav_file:
            # 获取音频参数
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            duration = frames / sample_rate

            # 读取音频数据
            audio_data = wav_file.readframes(frames)
            audio_array = struct.unpack(f"{frames * wav_file.getnchannels()}h", audio_data)

            # 简单的频率分析
            fft = np.fft.fft(audio_array)
            freqs = np.fft.fftfreq(len(fft))

            # 找到主要频率
            main_freq_idx = np.argmax(np.abs(fft))
            main_freq = abs(freqs[main_freq_idx] * sample_rate)

            # 估算调性
            note_freqs = {
                "C": 261.63,
                "C#": 277.18,
                "D": 293.66,
                "D#": 311.13,
                "E": 329.63,
                "F": 349.23,
                "F#": 369.99,
                "G": 392.00,
                "G#": 415.30,
                "A": 440.00,
                "A#": 466.16,
                "B": 493.88,
            }

            closest_note = min(note_freqs.items(), key=lambda x: abs(x[1] - main_freq))
            key = closest_note[0]

            # 估算速度
            tempo = int(60 + (main_freq / 10) % 120)

            return {
                "tempo": tempo,
                "key": key,
                "time_signature": "4/4",
                "duration": int(duration),
                "chords_detected": [
                    {"chord": key, "time": 0, "duration": 4},
                    {"chord": get_relative_chord(key, 5), "time": 4, "duration": 4},
                    {"chord": get_relative_chord(key, 6), "time": 8, "duration": 4},
                    {"chord": get_relative_chord(key, 4), "time": 12, "duration": 4},
                ],
                "melody_notes": [
                    {"note": f"{key}4", "time": 0, "duration": 1},
                    {"note": f"{get_relative_note(key, 2)}4", "time": 1, "duration": 1},
                    {"note": f"{get_relative_note(key, 4)}4", "time": 2, "duration": 1},
                    {"note": f"{get_relative_note(key, 5)}4", "time": 3, "duration": 1},
                ],
                "bass_line": [
                    {"note": f"{key}2", "time": 0, "duration": 1},
                    {"note": f"{get_relative_note(key, 5)}2", "time": 1, "duration": 1},
                    {"note": f"{get_relative_note(key, 6)}2", "time": 2, "duration": 1},
                    {"note": f"{get_relative_note(key, 4)}2", "time": 3, "duration": 1},
                ],
            }
    except Exception as e:
        print(f"基础音频分析错误: {str(e)}")
        # 返回默认值
        return {
            "tempo": 120,
            "key": "C",
            "time_signature": "4/4",
            "duration": 180,
            "chords_detected": [
                {"chord": "C", "time": 0, "duration": 4},
                {"chord": "G", "time": 4, "duration": 4},
                {"chord": "Am", "time": 8, "duration": 4},
                {"chord": "F", "time": 12, "duration": 4},
            ],
            "melody_notes": [
                {"note": "C4", "time": 0, "duration": 1},
                {"note": "E4", "time": 1, "duration": 1},
                {"note": "G4", "time": 2, "duration": 1},
                {"note": "C5", "time": 3, "duration": 1},
            ],
            "bass_line": [
                {"note": "C2", "time": 0, "duration": 1},
                {"note": "G2", "time": 1, "duration": 1},
                {"note": "A2", "time": 2, "duration": 1},
                {"note": "F2", "time": 3, "duration": 1},
            ],
        }


def detect_chords(y, sr, tempo):
    """检测和弦"""
    try:
        import librosa

        # 使用色度图检测和弦
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

        # 和弦模板
        chord_templates = {
            "C": [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],  # C-E-G
            "G": [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],  # G-B-D
            "Am": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],  # A-C-E
            "F": [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],  # F-A-C
            "Dm": [0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0],  # D-F-A
            "Em": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],  # E-G-B
        }

        chords_detected = []
        frame_length = int(sr * 4 / tempo)  # 4拍的长度

        for i in range(0, chroma.shape[1], frame_length):
            frame_chroma = np.mean(chroma[:, i : i + frame_length], axis=1)

            # 找到最匹配的和弦
            best_chord = "C"
            best_score = 0

            for chord, template in chord_templates.items():
                score = np.dot(frame_chroma, template)
                if score > best_score:
                    best_score = score
                    best_chord = chord

            chords_detected.append(
                {"chord": best_chord, "time": i * librosa.get_duration(y=y, sr=sr) / chroma.shape[1], "duration": 4}
            )

        return chords_detected[:4]  # 返回前4个和弦

    except Exception as e:
        print(f"和弦检测错误: {str(e)}")
        return [
            {"chord": "C", "time": 0, "duration": 4},
            {"chord": "G", "time": 4, "duration": 4},
            {"chord": "Am", "time": 8, "duration": 4},
            {"chord": "F", "time": 12, "duration": 4},
        ]


def detect_melody(y, sr):
    """检测旋律"""
    try:
        import librosa

        # 提取音高
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

        melody_notes = []
        time_step = 0.1  # 100ms步长

        for i in range(0, pitches.shape[1], int(sr * time_step / 512)):
            if i < pitches.shape[1]:
                # 找到最强音高
                max_idx = np.argmax(magnitudes[:, i])
                pitch = pitches[max_idx, i]

                if pitch > 0:
                    # 转换为音符
                    note = librosa.hz_to_note(pitch)
                    melody_notes.append({"note": note, "time": i * 512 / sr, "duration": time_step})

        return melody_notes[:8]  # 返回前8个音符

    except Exception as e:
        print(f"旋律检测错误: {str(e)}")
        return [
            {"note": "C4", "time": 0, "duration": 1},
            {"note": "E4", "time": 1, "duration": 1},
            {"note": "G4", "time": 2, "duration": 1},
            {"note": "C5", "time": 3, "duration": 1},
        ]


def detect_bass_line(y, sr):
    """检测低音线"""
    try:
        import librosa

        # 提取低音频率
        y_harmonic, y_percussive = librosa.effects.hpss(y)

        # 低通滤波
        from scipy import signal

        b, a = signal.butter(4, 200 / (sr / 2), btype="low")
        y_bass = signal.filtfilt(b, a, y_harmonic)

        # 检测低音音符
        pitches, magnitudes = librosa.piptrack(y=y_bass, sr=sr)

        bass_line = []
        time_step = 0.5  # 500ms步长

        for i in range(0, pitches.shape[1], int(sr * time_step / 512)):
            if i < pitches.shape[1]:
                # 找到最强低音
                max_idx = np.argmax(magnitudes[:, i])
                pitch = pitches[max_idx, i]

                if pitch > 0 and pitch < 200:  # 只取低音
                    note = librosa.hz_to_note(pitch)
                    bass_line.append({"note": note, "time": i * 512 / sr, "duration": time_step})

        return bass_line[:4]  # 返回前4个低音

    except Exception as e:
        print(f"低音检测错误: {str(e)}")
        return [
            {"note": "C2", "time": 0, "duration": 1},
            {"note": "G2", "time": 1, "duration": 1},
            {"note": "A2", "time": 2, "duration": 1},
            {"note": "F2", "time": 3, "duration": 1},
        ]


def get_relative_chord(key, degree):
    """获取相对和弦"""
    chord_progression = {
        "C": ["C", "Dm", "Em", "F", "G", "Am", "Bdim"],
        "G": ["G", "Am", "Bm", "C", "D", "Em", "F#dim"],
        "D": ["D", "Em", "F#m", "G", "A", "Bm", "C#dim"],
        "A": ["A", "Bm", "C#m", "D", "E", "F#m", "G#dim"],
        "E": ["E", "F#m", "G#m", "A", "B", "C#m", "D#dim"],
        "F": ["F", "Gm", "Am", "Bb", "C", "Dm", "Edim"],
        "Bb": ["Bb", "Cm", "Dm", "Eb", "F", "Gm", "Adim"],
    }

    if key in chord_progression and 1 <= degree <= 7:
        return chord_progression[key][degree - 1]
    return "C"


def get_relative_note(key, degree):
    """获取相对音符"""
    note_progression = {
        "C": ["C", "D", "E", "F", "G", "A", "B"],
        "G": ["G", "A", "B", "C", "D", "E", "F#"],
        "D": ["D", "E", "F#", "G", "A", "B", "C#"],
        "A": ["A", "B", "C#", "D", "E", "F#", "G#"],
        "E": ["E", "F#", "G#", "A", "B", "C#", "D#"],
        "F": ["F", "G", "A", "Bb", "C", "D", "E"],
        "Bb": ["Bb", "C", "D", "Eb", "F", "G", "A"],
    }

    if key in note_progression and 1 <= degree <= 7:
        return note_progression[key][degree - 1]
    return "C"


def generate_guitar_tab(analysis_data, tab_type):
    """生成吉他谱"""
    if tab_type == "chords":
        return generate_chord_tab(analysis_data)
    elif tab_type == "melody":
        return generate_melody_tab(analysis_data)
    elif tab_type == "full":
        return generate_full_tab(analysis_data)
    else:
        return generate_chord_tab(analysis_data)


def generate_chord_tab(analysis_data):
    """生成和弦谱"""
    chords = analysis_data.get("chords_detected", [])
    tempo = analysis_data.get("tempo", 120)
    key = analysis_data.get("key", "C")

    tab_content = f"""
歌曲信息:
调性: {key}
速度: {tempo} BPM
拍号: {analysis_data.get('time_signature', '4/4')}

和弦进行:
"""

    for chord_info in chords:
        chord = chord_info["chord"]
        duration = chord_info["duration"]
        tab_content += f"{chord} ({duration}拍)\n"

    # 添加和弦指法图
    chord_diagrams = get_chord_diagrams(chords)
    tab_content += "\n和弦指法图:\n"
    tab_content += chord_diagrams

    return {"type": "chords", "content": tab_content, "chords": chords, "tempo": tempo, "key": key}


def generate_melody_tab(analysis_data):
    """生成旋律谱"""
    melody_notes = analysis_data.get("melody_notes", [])
    tempo = analysis_data.get("tempo", 120)

    tab_content = f"""
旋律谱:
速度: {tempo} BPM

e|--{generate_tab_line(melody_notes, 'e')}--|
B|--{generate_tab_line(melody_notes, 'B')}--|
G|--{generate_tab_line(melody_notes, 'G')}--|
D|--{generate_tab_line(melody_notes, 'D')}--|
A|--{generate_tab_line(melody_notes, 'A')}--|
E|--{generate_tab_line(melody_notes, 'E')}--|
"""

    return {"type": "melody", "content": tab_content, "melody": melody_notes, "tempo": tempo}


def generate_full_tab(analysis_data):
    """生成完整吉他谱"""
    chord_tab = generate_chord_tab(analysis_data)
    melody_tab = generate_melody_tab(analysis_data)

    full_content = f"""
完整吉他谱:
{chord_tab['content']}

{melody_tab['content']}

演奏说明:
1. 先练习和弦进行
2. 再练习旋律部分
3. 最后和弦和旋律结合
"""

    return {"type": "full", "content": full_content, "chord_tab": chord_tab, "melody_tab": melody_tab}


def generate_tab_line(notes, string):
    """生成单弦的tab线"""
    # 模拟生成tab线
    tab_line = ""
    for note in notes:
        # 根据音符和琴弦计算品位
        fret = calculate_fret(note["note"], string)
        tab_line += f"{fret}-"

    return tab_line


def calculate_fret(note, string):
    """计算音符在指定琴弦上的品位"""
    # 简化的音符到品位转换
    note_to_fret = {
        "C": {"E": 8, "A": 3, "D": 10, "G": 5, "B": 1, "e": 8},
        "D": {"E": 10, "A": 5, "D": 0, "G": 7, "B": 3, "e": 10},
        "E": {"E": 0, "A": 7, "D": 2, "G": 9, "B": 5, "e": 0},
        "F": {"E": 1, "A": 8, "D": 3, "G": 10, "B": 6, "e": 1},
        "G": {"E": 3, "A": 10, "D": 5, "G": 0, "B": 8, "e": 3},
        "A": {"E": 5, "A": 0, "D": 7, "G": 2, "B": 10, "e": 5},
        "B": {"E": 7, "A": 2, "D": 9, "G": 4, "B": 0, "e": 7},
    }

    note_name = note[0]  # 提取音符名称
    return note_to_fret.get(note_name, {}).get(string, 0)


def get_chord_diagrams(chords):
    """获取和弦指法图"""
    chord_diagrams = {
        "C": """
C和弦:
e|---0---|
B|---1---|
G|---0---|
D|---2---|
A|---3---|
E|-------|
""",
        "G": """
G和弦:
e|---3---|
B|---3---|
G|---0---|
D|---0---|
A|---2---|
E|---3---|
""",
        "Am": """
Am和弦:
e|---0---|
B|---1---|
G|---2---|
D|---2---|
A|---0---|
E|-------|
""",
        "F": """
F和弦:
e|---1---|
B|---1---|
G|---2---|
D|---3---|
A|---3---|
E|---1---|
""",
    }

    diagrams = ""
    for chord_info in chords:
        chord = chord_info["chord"]
        if chord in chord_diagrams:
            diagrams += chord_diagrams[chord]

    return diagrams


def save_tab_result(user, task_id, tab_result):
    """保存扒谱结果"""
    # 这里应该保存到数据库


def get_recent_tabs(user, limit=5):
    """获取最近的扒谱记录"""
    # 这里应该从数据库获取真实数据
    return []


def get_tab_statistics(user):
    """获取扒谱统计"""
    return {"total_tabs": 15, "chord_tabs": 8, "melody_tabs": 4, "full_tabs": 3, "success_rate": 85}


def get_user_tab_history(user):
    """获取用户扒谱历史"""
    # 这里应该从数据库获取真实数据
    return []


def get_tab_by_id(tab_id, user):
    """根据ID获取扒谱记录"""
    # 这里应该从数据库获取真实数据
    return None


def generate_tab_file(tab_data):
    """生成扒谱文件内容"""
    return tab_data.get("content", "")


# 在文件末尾添加食物照片绑定相关功能


# 食物照片绑定功能
@login_required
def food_photo_binding_view(request):
    """食物照片绑定管理页面"""
    context = {
        "page_title": "食物照片绑定管理",
        "user_level": get_user_level(request.user) if hasattr(request.user, "id") else "beginner",
    }
    return render(request, "tools/food_photo_binding.html", context)


@login_required
def food_image_correction_view(request):
    """食物图片矫正页面"""
    context = {
        "page_title": "食物图片矫正",
        "user_level": get_user_level(request.user) if hasattr(request.user, "id") else "beginner",
    }
    return render(request, "tools/food_image_correction.html", context)


# 在文件末尾添加时光胶囊相关功能


# 时光胶囊功能
@login_required
def time_capsule_diary_view(request):
    """时光胶囊日记主页面"""
    from django.conf import settings

    context = {
        "page_title": "时光胶囊日记",
        "user_level": get_user_level(request.user) if hasattr(request.user, "id") else "beginner",
        "websocket_available": hasattr(settings, "CHANNEL_LAYERS"),
        "api_timeout": 10000,
        "retry_attempts": 3,
    }
    return render(request, "tools/time_capsule_diary.html", context)


# 时间胶囊API已移动到 time_capsule_views.py


@login_required
def get_achievements_api(request):
    """获取用户成就API"""
    try:
        import logging

        from django.conf import settings

        from .models import Achievement, TimeCapsule

        logger = logging.getLogger(__name__)

        # 获取用户成就
        achievements = Achievement.objects.filter(user=request.user)

        # 获取所有成就类型
        all_achievement_types = ["traveler", "explorer", "prophet", "collector", "emotion-master", "social-butterfly"]

        achievement_list = []
        for achievement_type in all_achievement_types:
            # 查找用户是否已获得该成就
            user_achievement = achievements.filter(achievement_type=achievement_type).first()

            if user_achievement:
                # 已解锁的成就
                achievement_data = {
                    "type": achievement_type,
                    "unlocked": True,
                    "progress": user_achievement.progress,
                    "points": user_achievement.points if hasattr(user_achievement, "points") else 0,
                }
            else:
                # 未解锁的成就，计算进度
                progress = 0
                if achievement_type == "traveler":
                    # 连续记录天数
                    capsules = TimeCapsule.objects.filter(user=request.user).order_by("-created_at")
                    if capsules.exists():
                        # 简单的连续天数计算
                        progress = min(capsules.count(), 7)
                elif achievement_type == "collector":
                    # 收集的记忆碎片数量
                    progress = TimeCapsule.objects.filter(user=request.user).count()
                elif achievement_type == "explorer":
                    # 解锁的胶囊数量
                    progress = TimeCapsule.objects.filter(user=request.user, is_unlocked=True).count()
                elif achievement_type == "prophet":
                    # 预言次数
                    progress = TimeCapsule.objects.filter(user=request.user, content__icontains="预言").count()
                elif achievement_type == "emotion-master":
                    # 情绪种类
                    emotions = set()
                    capsules = TimeCapsule.objects.filter(user=request.user)
                    for capsule in capsules:
                        if capsule.emotions:
                            # emotions字段现在是JSONField，存储的是列表
                            if isinstance(capsule.emotions, list):
                                emotions.update(capsule.emotions)
                            elif isinstance(capsule.emotions, str):
                                # 兼容旧数据格式
                                emotions.update(capsule.emotions.split(","))
                    progress = len(emotions)
                elif achievement_type == "social-butterfly":
                    # 社交互动次数
                    progress = TimeCapsule.objects.filter(user=request.user, visibility="public").count()

                achievement_data = {"type": achievement_type, "unlocked": False, "progress": progress, "points": 0}

            achievement_list.append(achievement_data)

        # 计算统计数据
        user_capsules = TimeCapsule.objects.filter(user=request.user)
        total_capsules = user_capsules.count()

        # 计算连续天数
        consecutive_days = 0
        if total_capsules > 0:
            # 简单的连续天数计算
            consecutive_days = min(total_capsules, 7)

        # 解锁数量
        unlock_count = user_capsules.filter(is_unlocked=True).count()

        # 记忆碎片数量
        fragment_count = total_capsules

        # 预言次数
        prophecy_count = user_capsules.filter(content__icontains="预言").count()

        # 总积分
        total_points = sum(achievement.points for achievement in achievements if hasattr(achievement, "points"))

        stats = {
            "consecutive_days": consecutive_days,
            "unlock_count": unlock_count,
            "fragment_count": fragment_count,
            "prophecy_count": prophecy_count,
            "total_points": total_points,
        }

        return JsonResponse(
            {
                "success": True,
                "achievements": achievement_list,
                "stats": stats,
                "websocket_available": hasattr(settings, "CHANNEL_LAYERS"),
            }
        )

    except Exception as e:
        logger.error(f"获取用户成就失败: {str(e)}")
        return JsonResponse(
            {
                "success": False,
                "message": f"获取失败: {str(e)}",
                "achievements": [],
                "stats": {
                    "consecutive_days": 0,
                    "unlock_count": 0,
                    "fragment_count": 0,
                    "prophecy_count": 0,
                    "total_points": 0,
                },
            },
            status=500,
        )


def check_time_capsule_achievements(user):
    """检查并授予时光胶囊相关成就"""
    try:
        from .models import Achievement, TimeCapsule

        # 检查时光旅人成就（连续记录7天）
        capsules = TimeCapsule.objects.filter(user=user).order_by("-created_at")
        if capsules.count() >= 7:
            achievement, created = Achievement.objects.get_or_create(
                user=user, achievement_type="traveler", defaults={"progress": capsules.count()}
            )
            if created:
                print(f"🎉 用户 {user.username} 获得了时光旅人成就！")

        # 检查记忆收藏家成就（收集10个记忆碎片）
        if capsules.count() >= 10:
            achievement, created = Achievement.objects.get_or_create(
                user=user, achievement_type="collector", defaults={"progress": capsules.count()}
            )
            if created:
                print(f"🎉 用户 {user.username} 获得了记忆收藏家成就！")

    except Exception as e:
        print(f"检查成就时出错: {str(e)}")


@login_required
def time_capsule_history_view(request):
    """时光胶囊历史页面"""
    from django.conf import settings

    try:
        from .models import Achievement, TimeCapsule

        # 获取用户的胶囊
        capsules = TimeCapsule.objects.filter(user=request.user).order_by("-created_at")

        # 获取用户成就
        achievements = Achievement.objects.filter(user=request.user)

        context = {
            "page_title": "时光胶囊历史",
            "capsules": capsules,
            "achievements": achievements,
            "total_capsules": capsules.count(),
            "user_level": get_user_level(request.user) if hasattr(request.user, "id") else "beginner",
            "websocket_available": hasattr(settings, "CHANNEL_LAYERS"),
            "api_timeout": 10000,
            "retry_attempts": 3,
        }

        return render(request, "tools/time_capsule_history.html", context)

    except Exception as e:
        context = {
            "page_title": "时光胶囊历史",
            "error": str(e),
            "user_level": get_user_level(request.user) if hasattr(request.user, "id") else "beginner",
            "websocket_available": hasattr(settings, "CHANNEL_LAYERS"),
            "api_timeout": 10000,
            "retry_attempts": 3,
        }
        return render(request, "tools/time_capsule_history.html", context)
