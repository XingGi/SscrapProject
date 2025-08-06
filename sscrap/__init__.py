# sscrap/__init__.py

# Ini akan memastikan app Celery selalu diimpor saat Django dimulai.
from .celery import app as celery_app

__all__ = ('celery_app',)