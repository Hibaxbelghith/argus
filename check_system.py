"""
System Health Check Script
Verifies that all AI modules and dependencies are properly configured
Usage: python check_system.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus.settings')
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}\n")


def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")


def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.ENDC}")


def check_python_packages():
    """Check if required Python packages are installed"""
    print_header("PYTHON PACKAGES CHECK")
    
    packages = {
        'django': 'Django',
        'celery': 'Celery',
        'redis': 'Redis',
        'sklearn': 'Scikit-learn (ML)',
        'xgboost': 'XGBoost (ML)',
        'prophet': 'Prophet (Time Series)',
        'openai': 'OpenAI (GPT-4)',
        'spacy': 'spaCy (NLP)',
        'plotly': 'Plotly (Visualizations)',
        'twilio': 'Twilio (SMS/Voice)',
        'sendgrid': 'SendGrid (Email)',
        'firebase_admin': 'Firebase (Push Notifications)',
    }
    
    installed = []
    missing = []
    
    for package, name in packages.items():
        try:
            __import__(package)
            print_success(f"{name} is installed")
            installed.append(name)
        except ImportError:
            print_error(f"{name} is NOT installed")
            missing.append(name)
    
    print(f"\n📊 Summary: {len(installed)}/{len(packages)} packages installed")
    
    if missing:
        print_warning(f"Missing packages: {', '.join(missing)}")
        print_warning("Run: pip install -r requirements.txt")
    
    return len(missing) == 0


def check_spacy_model():
    """Check if spaCy model is downloaded"""
    print_header("SPACY MODEL CHECK")
    
    try:
        import spacy
        try:
            nlp = spacy.load('en_core_web_sm')
            print_success("spaCy model 'en_core_web_sm' is installed")
            return True
        except OSError:
            print_error("spaCy model 'en_core_web_sm' is NOT downloaded")
            print_warning("Run: python -m spacy download en_core_web_sm")
            return False
    except ImportError:
        print_error("spaCy is not installed")
        return False


def check_redis_connection():
    """Check Redis connection"""
    print_header("REDIS CONNECTION CHECK")
    
    try:
        import redis
        broker_url = getattr(settings, 'CELERY_BROKER_URL', 'redis://localhost:6379/0')
        
        # Parse Redis URL
        if broker_url.startswith('redis://'):
            parts = broker_url.replace('redis://', '').split('/')
            host_port = parts[0].split(':')
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else 6379
        else:
            host, port = 'localhost', 6379
        
        r = redis.Redis(host=host, port=port, db=0, socket_connect_timeout=2)
        r.ping()
        print_success(f"Redis is running on {host}:{port}")
        return True
    except Exception as e:
        print_error(f"Cannot connect to Redis: {e}")
        print_warning("Install Redis or Memurai (Windows) and start the service")
        return False


def check_environment_variables():
    """Check critical environment variables"""
    print_header("ENVIRONMENT VARIABLES CHECK")
    
    env_vars = {
        'SECRET_KEY': 'Django Secret Key',
        'CELERY_BROKER_URL': 'Celery Broker URL',
        'OPENAI_API_KEY': 'OpenAI API Key (optional)',
        'TWILIO_ACCOUNT_SID': 'Twilio Account SID (optional)',
        'SENDGRID_API_KEY': 'SendGrid API Key (optional)',
    }
    
    configured = []
    missing = []
    
    for var, description in env_vars.items():
        value = os.getenv(var) or getattr(settings, var, None)
        if value and str(value).strip():
            if 'optional' in description.lower():
                print_success(f"{description}: Configured")
            else:
                print_success(f"{description}: ✓")
            configured.append(var)
        else:
            if 'optional' in description.lower():
                print_warning(f"{description}: Not configured (features limited)")
            else:
                print_error(f"{description}: NOT SET (required)")
                missing.append(var)
    
    print(f"\n📊 Summary: {len(configured)}/{len(env_vars)} variables configured")
    
    if missing:
        print_warning("Create a .env file with required variables")
    
    return len([v for v in missing if 'optional' not in env_vars[v].lower()]) == 0


def check_database():
    """Check database connectivity and migrations"""
    print_header("DATABASE CHECK")
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print_success("Database connection successful")
        
        # Check if tables exist
        from detection.models import Detection
        from analytics.models import Alert, Insight
        from notifications.models import Notification
        
        detection_count = Detection.objects.count()
        alert_count = Alert.objects.count()
        insight_count = Insight.objects.count()
        notification_count = Notification.objects.count()
        
        print_success(f"Detections: {detection_count}")
        print_success(f"Alerts: {alert_count}")
        print_success(f"Insights: {insight_count}")
        print_success(f"Notifications: {notification_count}")
        
        if detection_count == 0:
            print_warning("No detection data. Run: python manage.py generate_test_data")
        
        return True
    except Exception as e:
        print_error(f"Database error: {e}")
        print_warning("Run: python manage.py migrate")
        return False


def check_celery():
    """Check Celery configuration"""
    print_header("CELERY CHECK")
    
    try:
        from argus.celery import app as celery_app
        print_success("Celery app configured")
        
        # Check if tasks are registered
        tasks = list(celery_app.tasks.keys())
        ai_tasks = [t for t in tasks if 'analytics' in t or 'notifications' in t]
        
        print_success(f"Total tasks registered: {len(tasks)}")
        print_success(f"AI module tasks: {len(ai_tasks)}")
        
        if ai_tasks:
            print("\n📋 AI Tasks:")
            for task in sorted(ai_tasks)[:5]:  # Show first 5
                print(f"   • {task}")
        
        print_warning("Make sure Celery worker is running:")
        print_warning("   celery -A argus worker --loglevel=info --pool=solo")
        print_warning("Make sure Celery beat is running:")
        print_warning("   celery -A argus beat --loglevel=info")
        
        return True
    except Exception as e:
        print_error(f"Celery configuration error: {e}")
        return False


def check_ml_models():
    """Check if ML models can be loaded"""
    print_header("ML MODELS CHECK")
    
    try:
        from analytics.ml_models import AnomalyDetector, TimeSeriesPredictor, TrendAnalyzer
        
        detector = AnomalyDetector()
        print_success("AnomalyDetector initialized")
        
        try:
            predictor = TimeSeriesPredictor()
            print_success("TimeSeriesPredictor initialized")
        except:
            print_warning("TimeSeriesPredictor requires Prophet (optional)")
        
        analyzer = TrendAnalyzer()
        print_success("TrendAnalyzer initialized")
        
        return True
    except Exception as e:
        print_error(f"ML models error: {e}")
        return False


def check_urls():
    """Check if URL routes are configured"""
    print_header("URL ROUTING CHECK")
    
    try:
        from django.urls import reverse
        
        urls = [
            ('analytics:dashboard', 'Analytics Dashboard'),
            ('analytics:alerts', 'Analytics Alerts'),
            ('analytics:insights', 'Analytics Insights'),
        ]
        
        for url_name, description in urls:
            try:
                url = reverse(url_name)
                print_success(f"{description}: {url}")
            except:
                print_warning(f"{description}: Not configured")
        
        print_warning("\nAdvanced API endpoints (check manually):")
        print("   • http://localhost:8000/analytics/api/anomalies/detect/")
        print("   • http://localhost:8000/analytics/api/patterns/recognize/")
        print("   • http://localhost:8000/analytics/api/predictions/forecast/")
        
        return True
    except Exception as e:
        print_error(f"URL configuration error: {e}")
        return False


def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║        ARGUS AI MODULES - SYSTEM HEALTH CHECK           ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    checks = [
        ("Python Packages", check_python_packages),
        ("spaCy Model", check_spacy_model),
        ("Redis Connection", check_redis_connection),
        ("Environment Variables", check_environment_variables),
        ("Database", check_database),
        ("Celery", check_celery),
        ("ML Models", check_ml_models),
        ("URL Routing", check_urls),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Error checking {name}: {e}")
            results.append((name, False))
    
    # Final Summary
    print_header("FINAL SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{status}{Colors.ENDC} - {name}")
    
    print(f"\n{Colors.BOLD}Overall: {passed}/{total} checks passed{Colors.ENDC}")
    
    if passed == total:
        print_success("\n🎉 All checks passed! System is ready.")
        print("\n📚 Next steps:")
        print("   1. python manage.py runserver")
        print("   2. celery -A argus worker --loglevel=info --pool=solo")
        print("   3. celery -A argus beat --loglevel=info")
    elif passed >= total * 0.7:
        print_warning("\n⚠️  System is partially ready. Fix optional issues for full functionality.")
    else:
        print_error("\n❌ System is not ready. Fix critical issues before proceeding.")
    
    print(f"\n📖 See AI_QUICKSTART.md for detailed setup instructions\n")
    
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
