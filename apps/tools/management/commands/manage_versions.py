"""
Django管理命令：版本管理
用于添加、更新和查看项目版本信息
"""

import os
import sys

from django.core.management.base import BaseCommand, CommandError

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from apps.tools.utils.version_tracker import VersionTracker


class Command(BaseCommand):
    help = "管理项目版本信息"

    def add_arguments(self, parser):
        parser.add_argument(
            "action",
            choices=["list", "add", "update", "current", "stats"],
            help="操作类型：list(列表), add(添加), update(更新), current(当前版本), stats(统计)",
        )

        # 添加版本参数
        parser.add_argument("--ver", type=str, help="版本号 (例如: 1.1.0)")

        # 添加标题参数
        parser.add_argument("--title", type=str, help="版本标题")

        # 添加功能参数
        parser.add_argument("--features", type=str, help='功能列表，用逗号分隔 (例如: "功能1,功能2,功能3")')

        # 添加描述参数
        parser.add_argument("--description", type=str, help="版本描述")

        # 添加日期参数
        parser.add_argument("--date", type=str, help="发布日期 (格式: YYYY-MM-DD)")

    def handle(self, *args, **options):
        tracker = VersionTracker()
        action = options["action"]

        if action == "list":
            self.list_versions(tracker)
        elif action == "add":
            self.add_version(tracker, options)
        elif action == "update":
            self.update_version(tracker, options)
        elif action == "current":
            self.show_current_version(tracker)
        elif action == "stats":
            self.show_stats(tracker)

    def list_versions(self, tracker):
        """列出所有版本"""
        self.stdout.write(self.style.SUCCESS("📋 版本列表"))
        self.stdout.write("=" * 60)

        versions = tracker.get_all_versions()
        for version in versions:
            formatted_date = tracker.format_date_for_display(version["date"])
            self.stdout.write(f"v{version['version']} ({formatted_date})")
            self.stdout.write(f"   标题: {version['title']}")
            self.stdout.write(f"   功能: {', '.join(version['features'])}")
            self.stdout.write(f"   描述: {version['description']}")
            self.stdout.write("-" * 40)

    def add_version(self, tracker, options):
        """添加新版本"""
        version = options.get("ver")
        title = options.get("title")
        features_str = options.get("features")
        description = options.get("description")
        date = options.get("date")

        if not all([version, title, features_str, description]):
            raise CommandError("添加版本需要提供所有参数：--ver, --title, --features, --description")

        # 解析功能列表
        features = [f.strip() for f in features_str.split(",") if f.strip()]

        # 添加版本
        tracker.add_version(version, title, features, description, date)

        self.stdout.write(self.style.SUCCESS(f"✅ 成功添加版本 v{version}: {title}"))

    def update_version(self, tracker, options):
        """更新版本信息"""
        version = options.get("ver")
        if not version:
            raise CommandError("更新版本需要提供 --ver 参数")

        # 构建更新数据
        update_data = {}
        if options.get("title"):
            update_data["title"] = options["title"]
        if options.get("features"):
            features = [f.strip() for f in options["features"].split(",") if f.strip()]
            update_data["features"] = features
        if options.get("description"):
            update_data["description"] = options["description"]
        if options.get("date"):
            update_data["date"] = options["date"]

        if not update_data:
            raise CommandError("更新版本需要提供至少一个更新字段")

        # 更新版本
        success = tracker.update_version(version, **update_data)
        if success:
            self.stdout.write(self.style.SUCCESS(f"✅ 成功更新版本 v{version}"))
        else:
            raise CommandError(f"❌ 未找到版本 v{version}")

    def show_current_version(self, tracker):
        """显示当前版本"""
        current_version = tracker.get_current_version()
        version_info = tracker.get_version_by_number(current_version)

        self.stdout.write(self.style.SUCCESS("🎯 当前版本信息"))
        self.stdout.write("=" * 40)

        if version_info:
            formatted_date = tracker.format_date_for_display(version_info["date"])
            self.stdout.write(f"版本号: v{version_info['version']}")
            self.stdout.write(f"发布日期: {formatted_date}")
            self.stdout.write(f"标题: {version_info['title']}")
            self.stdout.write(f"功能: {', '.join(version_info['features'])}")
            self.stdout.write(f"描述: {version_info['description']}")
        else:
            self.stdout.write(f"当前版本: v{current_version}")

    def show_stats(self, tracker):
        """显示版本统计信息"""
        self.stdout.write(self.style.SUCCESS("📊 版本统计信息"))
        self.stdout.write("=" * 40)

        self.stdout.write(f"当前版本: v{tracker.get_current_version()}")
        self.stdout.write(f"项目启动: {tracker.get_project_start_date()}")
        self.stdout.write(f"开发周期: {tracker.get_development_duration()}")
        self.stdout.write(f"版本总数: {tracker.get_version_count()}")
        self.stdout.write(f"功能总数: {tracker.get_total_features()}")

        # 显示功能分布
        self.stdout.write("\n🎯 功能分布:")
        feature_count = {}
        for version in tracker.get_all_versions():
            for feature in version["features"]:
                feature_count[feature] = feature_count.get(feature, 0) + 1

        for feature, count in sorted(feature_count.items(), key=lambda x: x[1], reverse=True):
            self.stdout.write(f"   {feature}: {count}次")


# 使用示例
if __name__ == "__main__":
    # 测试命令
    tracker = VersionTracker()

    print("📋 版本管理命令示例:")
    print("=" * 50)
    print("1. 查看版本列表:")
    print("   python manage.py manage_versions list")
    print()
    print("2. 添加新版本:")
    print("   python manage.py manage_versions add --ver 1.1.0 --title '功能增强' --features '新功能1,新功能2' --description '新增多个功能'")
    print()
    print("3. 更新版本:")
    print("   python manage.py manage_versions update --ver 1.0.0 --title '更新标题'")
    print()
    print("4. 查看当前版本:")
    print("   python manage.py manage_versions current")
    print()
    print("5. 查看统计信息:")
    print("   python manage.py manage_versions stats")
