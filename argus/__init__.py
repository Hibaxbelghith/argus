# Celery app import - only if Celery is installed
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    # Celery not installed - running in simple mode
    __all__ = ()

