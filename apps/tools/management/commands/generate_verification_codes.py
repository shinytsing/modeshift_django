"""
生成验证码管理命令
"""
from django.core.management.base import BaseCommand
from apps.tools.services.verification_code_manager import verification_manager


class Command(BaseCommand):
    help = '生成验证码'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100000,
            help='要生成的验证码数量 (默认: 100000)'
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='显示验证码统计信息'
        )

    def handle(self, *args, **options):
        if options['stats']:
            # 显示统计信息
            stats = verification_manager.get_stats()
            self.stdout.write(
                self.style.SUCCESS(
                    f"验证码统计信息:\n"
                    f"  总数: {stats['total']}\n"
                    f"  可用: {stats['available']}\n"
                    f"  已用: {stats['used']}\n"
                    f"  使用率: {stats['usage_rate']}%"
                )
            )
        else:
            # 生成验证码
            count = options['count']
            self.stdout.write(f"开始生成 {count} 个验证码...")
            
            generated_count = verification_manager.generate_codes(count)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"成功生成 {generated_count} 个验证码"
                )
            )
