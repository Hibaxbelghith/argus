"""
Django management command to generate analytics for all users
Usage: python manage.py generate_analytics [--period daily|weekly|monthly]
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from analytics.services import AnalyticsEngine, SecurityAlertService
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate analytics for all active users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--period',
            type=str,
            default='daily',
            choices=['daily', 'weekly', 'monthly'],
            help='Period type for analytics generation'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Username to generate analytics for (optional)'
        )

    def handle(self, *args, **options):
        period = options['period']
        username = options.get('user')
        
        self.stdout.write(f"🔄 Generating {period} analytics...")
        
        # Filter users
        if username:
            users = User.objects.filter(username=username, is_active=True)
            if not users.exists():
                self.stdout.write(self.style.ERROR(f'❌ User "{username}" not found'))
                return
        else:
            users = User.objects.filter(is_active=True)
        
        success_count = 0
        error_count = 0
        
        for user in users:
            try:
                # Generate analytics
                analytics = AnalyticsEngine.generate_period_analytics(user, period)
                
                # Update trends
                AnalyticsEngine.update_object_trends(user)
                
                # Generate insights
                AnalyticsEngine.generate_insights(user)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ {user.username}: {analytics.total_detections} détections, '
                        f'{analytics.total_objects_detected} objets'
                    )
                )
                success_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ {user.username}: {str(e)}')
                )
                error_count += 1
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ Success: {success_count} users'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'❌ Errors: {error_count} users'))
