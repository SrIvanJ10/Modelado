"""
import os
from celery import Celery
from celery.schedules import crontab, schedule

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "villamora-api.settings")

app = Celery("app")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
app = Celery('app')

# Using a string here means the worker doesn’t have to serialize
# the configuration object to child processes
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs
app.autodiscover_tasks()