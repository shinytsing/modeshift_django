"""BOSS 直聘单平台投递服务。

增强版页面只提供 BOSS 直聘能力。浏览器会话由用户扫码建立，确认后保存为
Playwright storage state；任务本身写入既有求职模型，避免依赖 Django 进程内存。
"""

from dataclasses import dataclass
from datetime import timedelta
import hashlib
import json
import logging
import os
import threading
import time
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.contrib.auth.models import User
from django.db import close_old_connections, transaction
from django.utils import timezone

from apps.tools.models import CookieSession, JobApplication, JobSearchRequest
from .boss_zhipin_playwright import BossZhipinPlaywrightService, storage_state_has_boss_auth_cookie

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PlatformConfig:
    name: str
    icon: str
    description: str
    login_methods: List[str]
    max_applications: int
    wait_time: int
    enabled: bool = True


@dataclass(frozen=True)
class JobSearchConfig:
    keywords: List[str]
    cities: List[str]
    salary_range: List[int]
    experience: str
    max_applications: int
    interval: int
    blacklist: List[str]
    greeting: str
    use_ai: bool = True


def _boss_session_dir(user_id: int) -> str:
    directory = os.path.join(settings.MEDIA_ROOT, "boss_sessions", f"user_{user_id}")
    os.makedirs(directory, mode=0o700, exist_ok=True)
    os.chmod(directory, 0o700)
    return directory


def _boss_storage_state_file(user_id: int) -> str:
    return os.path.join(_boss_session_dir(user_id), "storage_state.json")


def persist_boss_storage_state(user_id: int, storage_state: Dict[str, Any], qr_id: str = "") -> str:
    """保存每个用户最新的一份 BOSS 登录态快照。"""
    if not isinstance(storage_state, dict) or not storage_state.get("cookies") and not storage_state.get("origins"):
        raise ValueError("BOSS storage state 为空，不能保存登录态")

    state_file = _boss_storage_state_file(user_id)
    with open(state_file, "w", encoding="utf-8") as handle:
        json.dump(storage_state, handle, ensure_ascii=False)
    os.chmod(state_file, 0o600)

    session_id = f"boss-{user_id}"
    with transaction.atomic():
        sessions = list(
            CookieSession.objects.select_for_update()
            .filter(user_id=user_id, platform="boss")
            .order_by("-last_used", "-id")
        )
        session = sessions[0] if sessions else None
        # 清理早期版本可能留下的重复会话，只保留最新的一条。
        for stale_session in sessions[1:]:
            stale_session.delete()
        if session is None:
            session = CookieSession(user_id=user_id, platform="boss", session_id=session_id)
        session.session_id = session_id
        session.storage_state = storage_state
        session.is_active = True
        session.save()

    meta_file = os.path.join(_boss_session_dir(user_id), "session.json")
    with open(meta_file, "w", encoding="utf-8") as handle:
        json.dump({"qr_id": qr_id, "state_file": state_file, "updated_at": time.time(), "mode": "playwright"}, handle)
    os.chmod(meta_file, 0o600)
    return state_file


def deactivate_boss_storage_state(user_id: int) -> None:
    """标记失效的 BOSS 会话，后续登录检查不会继续加载旧 state 文件。"""
    CookieSession.objects.filter(user_id=user_id, platform="boss").update(is_active=False)


def load_boss_storage_state(user_id: int) -> Optional[Dict[str, Any]]:
    """优先从数据库加载，兼容早期版本留下的 state 文件。"""
    session = CookieSession.objects.filter(user_id=user_id, platform="boss").first()
    if session and session.is_active:
        state = session.get_storage_state()
        if state:
            return state
    # 已知会话被标记为失效时，不要继续使用磁盘上的旧 state，避免失效登录态反复被尝试。
    if session:
        return None

    state_file = _boss_storage_state_file(user_id)
    try:
        os.chmod(state_file, 0o600)
        with open(state_file, encoding="utf-8") as handle:
            state = json.load(handle)
        return state if isinstance(state, dict) else None
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


class EnhancedJobDeliveryService:
    """BOSS 直聘单平台任务服务。"""

    BOSS_PLATFORM = "boss"

    def __init__(self):
        self.platforms = {
            self.BOSS_PLATFORM: PlatformConfig(
                name="BOSS直聘",
                icon="🏢",
                description="扫码登录后按筛选条件沟通职位",
                login_methods=["qr"],
                max_applications=200,
                wait_time=3,
            )
        }

    def create_search_config(self, data: Dict[str, Any]) -> JobSearchConfig:
        keywords = data.get("keywords", ["Python开发"])
        if isinstance(keywords, str):
            keywords = [item.strip() for item in keywords.split(",") if item.strip()]
        keywords = [str(item).strip() for item in keywords if str(item).strip()]

        cities = data.get("cities", ["北京"])
        if isinstance(cities, str):
            cities = [cities]
        cities = [str(item).strip() for item in cities if str(item).strip()]

        salary = data.get("expected_salary", [0, 0])
        if isinstance(salary, (int, float, str)):
            salary = [int(salary or 0), int(salary or 0)]
        salary = [int(value or 0) for value in salary[:2]] if isinstance(salary, list) else [0, 0]
        salary = (salary + [0, 0])[:2]

        blacklist = data.get("blacklist", [])
        if isinstance(blacklist, str):
            blacklist = [item.strip() for item in blacklist.splitlines() if item.strip()]
        blacklist = [str(item).strip() for item in blacklist if str(item).strip()]

        max_applications = int(data.get("max_applications", 50))
        interval = int(data.get("interval", 3))
        if not 1 <= max_applications <= self.platforms[self.BOSS_PLATFORM].max_applications:
            raise ValueError("投递数量必须在 1 到 200 之间")
        if not 1 <= interval <= 300:
            raise ValueError("投递间隔必须在 1 到 300 秒之间")

        return JobSearchConfig(
            keywords=keywords,
            cities=cities,
            salary_range=salary,
            experience=str(data.get("experience", "1-3")),
            max_applications=max_applications,
            interval=interval,
            blacklist=blacklist,
            greeting=str(data.get("say_hi", "您好，我对这个职位很感兴趣，希望能有机会进一步沟通。"))[:500],
            use_ai=bool(data.get("use_ai", True)),
        )

    def start_boss_delivery(self, config: JobSearchConfig, user: User) -> Dict[str, Any]:
        """创建可跨请求读取的 BOSS 任务，并交给 Celery/本地 task 入口。"""
        if not config.keywords:
            return {"success": False, "error": "请填写搜索关键词"}
        if not config.cities:
            return {"success": False, "error": "请选择工作城市"}

        with transaction.atomic():
            active = JobSearchRequest.objects.select_for_update().filter(
                user=user, status__in=["pending", "processing"]
            ).first()
            if active:
                return {"success": False, "error": "已有 BOSS 投递任务在运行中", "task_id": str(active.pk)}

            request = JobSearchRequest.objects.create(
                user=user,
                job_title=", ".join(config.keywords)[:200],
                location=", ".join(config.cities)[:200],
                min_salary=max(0, config.salary_range[0]),
                max_salary=max(config.salary_range[0], config.salary_range[1]),
                experience_level=config.experience if config.experience in {"fresh", "1-3", "3-5", "5-10", "10+"} else "1-3",
                keywords=config.keywords,
                auto_apply=True,
                max_applications=config.max_applications,
                application_interval=config.interval,
                status="processing",
                search_options={
                    "greeting": config.greeting,
                    "blacklist": config.blacklist,
                    "use_ai": config.use_ai,
                    "platform": self.BOSS_PLATFORM,
                },
            )

        self._schedule_delivery(request.pk)
        return {
            "success": True,
            "message": "BOSS 直聘投递任务已启动",
            "task_id": str(request.pk),
            "platforms": [self.BOSS_PLATFORM],
            "config": {
                "keywords": config.keywords,
                "cities": config.cities,
                "max_applications": config.max_applications,
            },
        }

    def _schedule_delivery(self, request_id: int) -> None:
        """触发共享 task；开发环境 eager 时放入线程，避免阻塞 HTTP 请求。"""
        from apps.tools.tasks import run_boss_delivery_task

        def dispatch() -> None:
            close_old_connections()
            try:
                try:
                    run_boss_delivery_task.delay(request_id)
                except Exception as exc:
                    # 当前容器可能没有 Celery broker（例如 django-db transport 未安装）。
                    # 任务已经持久化，回退到同一后台线程执行，避免留下 processing 孤儿任务。
                    logger.warning("BOSS Celery 调度失败，回退到本地后台执行 request=%s: %s", request_id, exc)
                    run_boss_delivery_task.run(request_id)
            finally:
                close_old_connections()

        threading.Thread(target=dispatch, name=f"boss-delivery-{request_id}", daemon=True).start()

    def execute_boss_delivery(self, request_id: int) -> Dict[str, Any]:
        close_old_connections()
        request = JobSearchRequest.objects.get(pk=request_id)
        if request.status == "cancelled":
            return {"success": False, "status": "cancelled", "message": "任务已停止"}

        request.status = "processing"
        request.error_message = None
        request.save(update_fields=["status", "error_message", "updated_at"])
        config = self._config_from_request(request)
        try:
            result = self._deliver_to_boss(config, request.user_id, request.pk)
            request.refresh_from_db()
            if request.status != "cancelled":
                request.status = "completed" if result.get("success") else "failed"
                request.total_jobs_found = result.get("found_count", request.total_jobs_found)
                request.total_applications_sent = result.get("applied_count", request.total_applications_sent)
                request.success_rate = (
                    request.total_applications_sent / request.total_jobs_found * 100
                    if request.total_jobs_found else 0
                )
                request.error_message = result.get("error")
                request.completed_at = timezone.now()
                request.save(update_fields=[
                    "status", "total_jobs_found", "total_applications_sent", "success_rate",
                    "error_message", "completed_at", "updated_at",
                ])
            return result
        except Exception as exc:
            logger.exception("BOSS 投递任务执行失败 request=%s", request_id)
            request.status = "failed"
            request.error_message = str(exc)
            request.completed_at = timezone.now()
            request.save(update_fields=["status", "error_message", "completed_at", "updated_at"])
            return {"success": False, "error": str(exc), "applied_count": 0, "found_count": 0}
        finally:
            close_old_connections()

    def _config_from_request(self, request: JobSearchRequest) -> JobSearchConfig:
        options = request.search_options or {}
        return JobSearchConfig(
            keywords=request.keywords or [request.job_title],
            cities=[request.location],
            salary_range=[request.min_salary, request.max_salary],
            experience=request.experience_level,
            max_applications=request.max_applications,
            interval=request.application_interval,
            blacklist=options.get("blacklist", []),
            greeting=options.get("greeting", "您好，我对这个职位很感兴趣，希望能有机会进一步沟通。"),
            use_ai=options.get("use_ai", True),
        )

    def _is_cancelled(self, request_id: int) -> bool:
        return JobSearchRequest.objects.filter(pk=request_id, status="cancelled").exists()

    def _deliver_to_boss(self, config: JobSearchConfig, user_id: int, request_id: int) -> Dict[str, Any]:
        """使用已保存登录态执行一批 BOSS 职位沟通。"""
        if not load_boss_storage_state(user_id):
            return {
                "success": False,
                "error": "BOSS 登录态已失效，请重新扫码",
                "applied_count": 0,
                "found_count": 0,
            }
        browser = BossZhipinPlaywrightService(headless=True, anti_detection=False)
        browser._user_id = user_id
        if not browser._init_browser():
            return {"success": False, "error": "BOSS 浏览器初始化失败，请重新扫码登录", "applied_count": 0, "found_count": 0}

        applied_count = 0
        found_count = 0
        try:
            browser.page.goto(f"{browser.base_url}/web/geek/jobs", wait_until="domcontentloaded", timeout=30000)
            browser.page.wait_for_timeout(1000)
            page_logged_in = browser._check_page_login_status(browser.page)
            current_url = (browser.page.url or "").lower()
            security_verification = any(
                marker in current_url for marker in ("security", "verify.html", "/verify", "captcha")
            )
            if not page_logged_in and security_verification:
                return {
                    "success": False,
                    "error": "BOSS 返回安全验证，请先在 BOSS 页面完成验证后再执行任务",
                    "applied_count": 0,
                    "found_count": 0,
                }
            if not page_logged_in and not storage_state_has_boss_auth_cookie(load_boss_storage_state(user_id)):
                deactivate_boss_storage_state(user_id)
                return {"success": False, "error": "BOSS 登录态已失效，请重新扫码", "applied_count": 0, "found_count": 0}

            per_keyword_limit = max(1, config.max_applications // max(1, len(config.keywords)))
            for keyword in config.keywords[:3]:
                if self._is_cancelled(request_id) or applied_count >= config.max_applications:
                    break
                search_input = browser.page.wait_for_selector('input[placeholder*="搜索职位"]', timeout=10000)
                search_input.fill(keyword)
                browser.page.keyboard.press("Enter")
                browser.page.wait_for_selector(".job-list", timeout=15000)
                job_items = browser.page.query_selector_all(".job-card-wrapper")
                found_count += len(job_items)

                for job_item in job_items[:per_keyword_limit]:
                    if self._is_cancelled(request_id) or applied_count >= config.max_applications:
                        break
                    snapshot = self._job_snapshot(job_item, config)
                    if any(term.lower() in snapshot["company_name"].lower() for term in config.blacklist):
                        continue
                    if JobApplication.objects.filter(
                        job_search_request__user_id=user_id, platform=self.BOSS_PLATFORM, job_id=snapshot["job_id"]
                    ).exists():
                        continue

                    job_item.click()
                    browser.page.wait_for_timeout(500)
                    apply_btn = browser.page.wait_for_selector('button:has-text("立即沟通")', timeout=5000)
                    apply_btn.click()
                    greeting_input = browser.page.wait_for_selector('textarea[placeholder*="打招呼"]', timeout=5000)
                    greeting_input.fill(config.greeting)
                    browser.page.get_by_role("button", name="发送").click()
                    JobApplication.objects.create(
                        job_search_request_id=request_id,
                        job_id=snapshot["job_id"],
                        job_title=snapshot["job_title"],
                        company_name=snapshot["company_name"],
                        location=snapshot["location"],
                        salary_range=snapshot["salary_range"],
                        job_description=snapshot["description"],
                        requirements=[],
                        benefits=[],
                        platform=self.BOSS_PLATFORM,
                        job_url=snapshot["job_url"],
                        status="contacted",
                        notes="BOSS 直聘增强版任务",
                    )
                    applied_count += 1
                    JobSearchRequest.objects.filter(pk=request_id).update(
                        total_jobs_found=found_count,
                        total_applications_sent=applied_count,
                        updated_at=timezone.now(),
                    )
                    browser.page.keyboard.press("Escape")
                    browser.page.wait_for_timeout(config.interval * 1000)

            storage_state = browser.page.context.storage_state()
            persist_boss_storage_state(user_id, storage_state)
            return {
                "success": True,
                "applied_count": applied_count,
                "found_count": found_count,
                "message": f"BOSS 直聘投递完成，成功沟通 {applied_count} 份，找到 {found_count} 个职位",
            }
        except Exception as exc:
            logger.exception("BOSS 页面投递失败 user=%s", user_id)
            return {"success": False, "error": str(exc), "applied_count": applied_count, "found_count": found_count}
        finally:
            try:
                if browser.page:
                    persist_boss_storage_state(user_id, browser.page.context.storage_state())
            except Exception:
                logger.warning("保存 BOSS 投递后的登录态失败", exc_info=True)
            browser._close_browser()

    @staticmethod
    def _job_snapshot(job_item: Any, config: JobSearchConfig) -> Dict[str, str]:
        text = (job_item.inner_text() or "").splitlines()
        clean = [line.strip() for line in text if line.strip()]
        job_title = clean[0][:200] if clean else config.keywords[0][:200]
        company_name = clean[1][:200] if len(clean) > 1 else "BOSS 职位"
        page = job_item.page
        job_url = page.url if page.url.startswith("http") else "https://www.zhipin.com/web/geek/jobs"
        job_key = job_item.get_attribute("data-jobid") or job_item.get_attribute("data-id")
        job_id = job_key or hashlib.sha256(f"{job_url}|{job_title}|{company_name}".encode()).hexdigest()[:100]
        return {
            "job_id": job_id,
            "job_title": job_title,
            "company_name": company_name,
            "location": config.cities[0],
            "salary_range": "-".join(str(value) for value in config.salary_range if value) or "面议",
            "description": "",
            "job_url": job_url,
        }

    def get_delivery_status(self, user: User) -> Dict[str, Any]:
        request = JobSearchRequest.objects.filter(user=user).order_by("-created_at").first()
        if not request:
            return {"success": True, "status": "idle", "message": "当前没有 BOSS 投递任务"}

        runtime = timezone.now() - request.created_at
        latest_application = request.applications.order_by("-application_time").first()
        result = {
            "success": request.status != "failed",
            "applied_count": request.total_applications_sent,
            "found_count": request.total_jobs_found,
            "message": request.error_message or "BOSS 任务已完成",
        }
        if latest_application:
            result["last_job"] = {
                "title": latest_application.job_title,
                "company": latest_application.company_name,
                "status": latest_application.status,
            }
        return {
            "success": True,
            "status": request.status,
            "task_id": str(request.pk),
            "platforms": [self.BOSS_PLATFORM],
            "runtime": str(timedelta(seconds=int(runtime.total_seconds()))),
            "total_applied": request.total_applications_sent,
            "total_found": request.total_jobs_found,
            "results": {self.BOSS_PLATFORM: result},
            "config": {
                "keywords": request.keywords,
                "cities": [request.location],
                "max_applications": request.max_applications,
                "expected_salary": [request.min_salary, request.max_salary],
                "interval": request.application_interval,
                "greeting": (request.search_options or {}).get("greeting", ""),
                "blacklist": (request.search_options or {}).get("blacklist", []),
                "use_ai": (request.search_options or {}).get("use_ai", True),
            },
            "error": request.error_message or "",
        }

    def get_delivery_summary(self, user: User) -> Dict[str, Any]:
        """返回工作确认弹窗需要的历史统计和最近投递记录，不返回任何会话内容。"""
        requests = list(JobSearchRequest.objects.filter(user=user).order_by("-created_at"))
        total_found = sum(item.total_jobs_found or 0 for item in requests)
        total_applied = sum(item.total_applications_sent or 0 for item in requests)
        completed_tasks = sum(item.status == "completed" for item in requests)
        failed_tasks = sum(item.status == "failed" for item in requests)
        success_rate = round((total_applied / total_found) * 100, 2) if total_found else 0

        applications = JobApplication.objects.filter(
            job_search_request__user=user,
            platform=self.BOSS_PLATFORM,
        ).order_by("-application_time")
        status_counts: Dict[str, int] = {}
        for status in applications.values_list("status", flat=True):
            status_counts[status] = status_counts.get(status, 0) + 1

        recent_applications = [
            {
                "title": item.job_title,
                "company": item.company_name,
                "location": item.location,
                "status": item.status,
                "applied_at": item.application_time.isoformat() if item.application_time else "",
            }
            for item in applications[:10]
        ]

        latest_config: Dict[str, Any] = {}
        if requests:
            latest = requests[0]
            options = latest.search_options or {}
            latest_config = {
                "keywords": latest.keywords or ([latest.job_title] if latest.job_title else []),
                "cities": [latest.location] if latest.location else [],
                "expected_salary": [latest.min_salary, latest.max_salary],
                "max_applications": latest.max_applications,
                "interval": latest.application_interval,
                "greeting": options.get("greeting", ""),
                "blacklist": options.get("blacklist", []),
                "use_ai": options.get("use_ai", True),
            }

        latest_task = requests[0] if requests else None
        return {
            "tasks_count": len(requests),
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "total_found": total_found,
            "total_applied": total_applied,
            "success_rate": success_rate,
            "status_counts": status_counts,
            "recent_applications": recent_applications,
            "latest_task": {
                "id": latest_task.pk,
                "status": latest_task.status,
                "created_at": latest_task.created_at.isoformat(),
                "error": latest_task.error_message or "",
            } if latest_task else None,
            "latest_config": latest_config,
        }

    def stop_delivery(self, user: User) -> Dict[str, Any]:
        request = JobSearchRequest.objects.filter(user=user, status__in=["pending", "processing"]).order_by("-created_at").first()
        if not request:
            return {"success": False, "error": "没有运行中的 BOSS 投递任务"}
        request.status = "cancelled"
        request.completed_at = timezone.now()
        request.save(update_fields=["status", "completed_at", "updated_at"])
        return {"success": True, "message": "BOSS 投递任务已停止", "task_id": str(request.pk)}

    def get_platform_info(self) -> Dict[str, Any]:
        config = self.platforms[self.BOSS_PLATFORM]
        return {
            "success": True,
            "platforms": {
                self.BOSS_PLATFORM: {
                    "name": config.name,
                    "icon": config.icon,
                    "description": config.description,
                    "login_methods": config.login_methods,
                    "max_applications": config.max_applications,
                    "wait_time": config.wait_time,
                    "enabled": config.enabled,
                }
            },
        }
