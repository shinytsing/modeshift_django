"""
清理过期的IP-Token绑定
"""
from django.core.management.base import BaseCommand
from apps.tools.services.ip_token_binding_service import ip_token_binding_service


class Command(BaseCommand):
    help = '清理过期的IP-Token绑定'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-age-hours',
            type=int,
            default=24,
            help='最大绑定时间（小时），默认24小时'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只显示将要清理的绑定，不实际删除'
        )

    def handle(self, *args, **options):
        max_age_hours = options['max_age_hours']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(f'[DRY RUN] 检查超过 {max_age_hours} 小时的绑定...')
            bindings = ip_token_binding_service.get_all_bindings()
            expired_count = 0
            
            for task_id, binding in bindings.items():
                import time
                current_time = time.time()
                created_at = binding.get('created_at', 0)
                max_age_seconds = max_age_hours * 3600
                
                if current_time - created_at > max_age_seconds:
                    expired_count += 1
                    self.stdout.write(f'  - 任务 {task_id}: IP {binding.get("ip_address")} (创建于 {time.ctime(created_at)})')
            
            self.stdout.write(f'[DRY RUN] 找到 {expired_count} 个过期绑定')
        else:
            self.stdout.write(f'清理超过 {max_age_hours} 小时的绑定...')
            cleaned_count = ip_token_binding_service.cleanup_expired_bindings(max_age_hours)
            self.stdout.write(
                self.style.SUCCESS(f'成功清理 {cleaned_count} 个过期绑定')
            )
