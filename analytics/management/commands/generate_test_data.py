"""
Django management command to generate test analytics data
Usage: python manage.py generate_test_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from detection.models import Detection
from analytics.models import Alert, Insight
from datetime import datetime, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate test data for analytics and detection modules'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detections',
            type=int,
            default=100,
            help='Number of detections to create (default: 100)'
        )
        parser.add_argument(
            '--anomalies',
            type=int,
            default=10,
            help='Number of anomalies to create (default: 10)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to spread data across (default: 30)'
        )

    def handle(self, *args, **options):
        num_detections = options['detections']
        num_anomalies = options['anomalies']
        days = options['days']

        self.stdout.write(self.style.SUCCESS(f'\n🚀 Generating test data...'))

        # Get or create a test user
        user = self._get_or_create_user()

        # Generate normal detections
        self.stdout.write(f'📊 Creating {num_detections} normal detections...')
        normal_objects = [
            ['person', 'chair'],
            ['person', 'laptop', 'desk'],
            ['person', 'phone'],
            ['car', 'person'],
            ['person', 'bottle'],
            ['dog', 'person'],
            ['cat', 'person'],
            ['person', 'book'],
            ['person', 'tv'],
            ['bicycle', 'person'],
        ]

        created_detections = []
        for i in range(num_detections):
            detection = Detection.objects.create(
                user=user,
                image_url=f"test_detection_{i}.jpg",
                detected_objects=random.choice(normal_objects),
                confidence=random.uniform(0.75, 0.95),
                detected_at=datetime.now() - timedelta(
                    days=random.randint(0, days),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
            )
            created_detections.append(detection)

        self.stdout.write(self.style.SUCCESS(f'✅ Created {num_detections} normal detections'))

        # Generate anomalous detections
        self.stdout.write(f'⚠️  Creating {num_anomalies} anomalous detections...')
        suspicious_objects = [
            ['gun', 'weapon'],
            ['knife', 'weapon'],
            ['fire'],
            ['crowbar', 'person'],
            ['scissors', 'weapon'],
            ['gun'],
            ['weapon', 'person'],
        ]

        anomaly_detections = []
        for i in range(num_anomalies):
            detection = Detection.objects.create(
                user=user,
                image_url=f"anomaly_detection_{i}.jpg",
                detected_objects=random.choice(suspicious_objects),
                confidence=random.uniform(0.85, 0.99),
                detected_at=datetime.now() - timedelta(
                    days=random.randint(0, min(7, days)),  # Recent anomalies
                    hours=random.randint(0, 23)
                )
            )
            anomaly_detections.append(detection)

            # Create corresponding alerts
            Alert.objects.create(
                detection=detection,
                alert_type='anomaly_detected',
                severity='high' if 'gun' in detection.detected_objects or 'fire' in detection.detected_objects else 'medium',
                message=f"Suspicious object detected: {', '.join(detection.detected_objects)}",
                details={
                    'confidence': detection.confidence,
                    'objects': detection.detected_objects,
                    'timestamp': detection.detected_at.isoformat()
                }
            )

        self.stdout.write(self.style.SUCCESS(f'✅ Created {num_anomalies} anomalies with alerts'))

        # Generate some insights
        self.stdout.write('💡 Creating insights...')
        
        insights_data = [
            {
                'insight_type': 'pattern_detected',
                'title': 'Morning Activity Pattern',
                'description': 'High activity detected between 8 AM and 10 AM',
                'importance': 'medium',
                'actionable': True,
                'data': {
                    'peak_hours': [8, 9, 10],
                    'avg_detections': 15,
                    'pattern': 'daily_routine'
                }
            },
            {
                'insight_type': 'anomaly_trend',
                'title': 'Increased Security Events',
                'description': f'{num_anomalies} suspicious detections in the last {min(7, days)} days',
                'importance': 'high',
                'actionable': True,
                'data': {
                    'count': num_anomalies,
                    'period_days': min(7, days),
                    'objects': list(set(sum(suspicious_objects, [])))
                }
            },
            {
                'insight_type': 'recommendation',
                'title': 'Review Camera Coverage',
                'description': 'Consider adding cameras in low-coverage areas',
                'importance': 'medium',
                'actionable': True,
                'data': {
                    'confidence': 0.75,
                    'based_on': 'detection_patterns'
                }
            }
        ]

        for insight_data in insights_data:
            Insight.objects.create(**insight_data)

        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(insights_data)} insights'))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('📈 TEST DATA GENERATION SUMMARY'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'👤 User: {user.username} (ID: {user.id})')
        self.stdout.write(f'📊 Normal Detections: {num_detections}')
        self.stdout.write(f'⚠️  Anomalous Detections: {num_anomalies}')
        self.stdout.write(f'🚨 Alerts Created: {num_anomalies}')
        self.stdout.write(f'💡 Insights Created: {len(insights_data)}')
        self.stdout.write(f'📅 Date Range: Last {days} days')
        self.stdout.write(self.style.SUCCESS('='*60))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Test data generation complete!'))
        self.stdout.write('\n🧪 Next steps:')
        self.stdout.write('   1. Start Django server: python manage.py runserver')
        self.stdout.write('   2. Visit: http://localhost:8000/analytics/api/anomalies/detect/')
        self.stdout.write('   3. Visit: http://localhost:8000/analytics/api/patterns/recognize/')
        self.stdout.write('   4. Visit: http://localhost:8000/analytics/dashboard/')

    def _get_or_create_user(self):
        """Get the first user or create a test user"""
        user = User.objects.first()
        
        if not user:
            self.stdout.write('👤 Creating test user...')
            user = User.objects.create_user(
                username='testuser',
                email='test@argus-security.com',
                password='testpassword123'
            )
            self.stdout.write(self.style.SUCCESS('✅ Test user created'))
            self.stdout.write(f'   Username: testuser')
            self.stdout.write(f'   Password: testpassword123')
        else:
            self.stdout.write(f'👤 Using existing user: {user.username}')
        
        return user
