from django.apps import AppConfig


class ToolsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.tools"
    verbose_name = "工具管理"

    def ready(self):
        """应用启动时的初始化"""
        if self._should_initialize_services():
            self._initialize_services()

    def _should_initialize_services(self) -> bool:
        """仅在 Web 进程启动时初始化后台服务。

        Django 会在大量管理命令（如 `check`、`migrate`、`shell`）中触发 app registry 的
        populate；此时启动后台线程/定时任务会导致初始化阶段卡住或产生副作用。
        """
        import sys
        import os

        if os.environ.get("DISABLE_STARTUP_TASKS") == "1":
            return False

        # 只在实际启动开发服务器时启用（可按需扩展到 gunicorn/daphne 等）
        return len(sys.argv) > 1 and sys.argv[1] in ["runserver", "runserver_plus"]

    def _initialize_services(self):
        """初始化各种服务"""
        try:
            # 导入服务 (已移除测试模块)
            # from .services.auto_test_runner import initialize_auto_testing
            pass

            # 初始化服务 (跳过测试模块)
            # initialize_auto_testing()
            # 启动定时任务
            self._start_scheduled_tasks()

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"服务初始化失败: {e}")

    def _start_scheduled_tasks(self):
        """启动定时任务"""
        # 在测试环境中禁用后台任务
        import os

        if os.environ.get("DJANGO_SETTINGS_MODULE") == "config.settings.testing":
            return

        try:
            import threading
            import time

            def run_scheduled_tasks():
                """运行定时任务"""
                while True:
                    try:
                        # 每5分钟运行一次健康检查
                        from .services.monitoring_service import periodic_health_check

                        periodic_health_check()

                        # 每10分钟运行一次性能优化
                        from .services.performance_optimizer import run_performance_optimization

                        run_performance_optimization()

                        # 每15分钟运行一次分片健康检查
                        from .services.database_sharding import check_shards_health

                        check_shards_health()

                        # 每30分钟运行一次自动化测试 (已禁用)
                        # from .services.auto_test_runner import run_scheduled_tests
                        # run_scheduled_tests()

                        # 每60分钟运行一次垃圾回收
                        from .services.performance_optimizer import run_garbage_collection

                        run_garbage_collection()

                        # 等待5分钟
                        time.sleep(300)

                    except Exception as e:
                        import logging

                        logger = logging.getLogger(__name__)
                        logger.error(f"定时任务执行失败: {e}")
                        time.sleep(60)  # 出错后等待1分钟再重试

            # 启动定时任务线程
            task_thread = threading.Thread(target=run_scheduled_tasks)
            task_thread.daemon = True
            task_thread.start()

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"定时任务启动失败: {e}")
