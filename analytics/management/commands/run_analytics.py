"""
Django management command to run periodic tasks manually (without Celery)
Usage: 
    python manage.py run_analytics daily
    python manage.py run_analytics weekly
    python manage.py run_analytics all
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from analytics import tasks
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = 'Run analytics tasks manually (without Celery)'

    def add_arguments(self, parser):
        parser.add_argument(
            'task_type',
            type=str,
            choices=['daily', 'weekly', 'predictive', 'digest', 'cleanup', 'retrain', 'all'],
            help='Type of task to run'
        )

    def handle(self, *args, **options):
        task_type = options['task_type']

        self.stdout.write(self.style.SUCCESS(f'\n🚀 Running {task_type} analytics tasks...\n'))

        if task_type == 'daily' or task_type == 'all':
            self.run_daily_analytics()

        if task_type == 'weekly' or task_type == 'all':
            self.run_weekly_report()

        if task_type == 'predictive' or task_type == 'all':
            self.run_predictive_alerts()

        if task_type == 'digest' or task_type == 'all':
            self.run_daily_digest()

        if task_type == 'cleanup' or task_type == 'all':
            self.run_cleanup()

        if task_type == 'retrain' or task_type == 'all':
            self.run_retrain()

        self.stdout.write(self.style.SUCCESS('\n✅ All tasks completed!\n'))

    def run_daily_analytics(self):
        """Generate daily analytics"""
        self.stdout.write('📊 Generating daily analytics...')
        try:
            result = tasks.generate_daily_analytics()
            self.stdout.write(self.style.SUCCESS('   ✅ Daily analytics completed'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Error: {e}'))

    def run_weekly_report(self):
        """Generate weekly report"""
        self.stdout.write('📈 Generating weekly report...')
        try:
            result = tasks.generate_weekly_report()
            self.stdout.write(self.style.SUCCESS('   ✅ Weekly report completed'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Error: {e}'))

    def run_predictive_alerts(self):
        """Generate predictive alerts"""
        self.stdout.write('🔮 Generating predictive alerts...')
        try:
            result = tasks.generate_predictive_alerts_task()
            self.stdout.write(self.style.SUCCESS('   ✅ Predictive alerts completed'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Error: {e}'))

    def run_daily_digest(self):
        """Send daily digest"""
        self.stdout.write('📧 Sending daily digest...')
        try:
            result = tasks.send_daily_digest()
            self.stdout.write(self.style.SUCCESS('   ✅ Daily digest sent'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Error: {e}'))

    def run_cleanup(self):
        """Cleanup old notifications"""
        self.stdout.write('🧹 Cleaning up old notifications...')
        try:
            result = tasks.cleanup_old_notifications()
            self.stdout.write(self.style.SUCCESS('   ✅ Cleanup completed'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Error: {e}'))

    def run_retrain(self):
        """Retrain ML models"""
        self.stdout.write('🤖 Retraining ML models...')
        try:
            result = tasks.retrain_ml_models()
            self.stdout.write(self.style.SUCCESS('   ✅ Model retraining completed'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Error: {e}'))
