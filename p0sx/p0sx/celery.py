import pathlib
import sys

from django.conf import settings

from celery import Celery

# Add PWD to sys_path
sys.path.insert(0, '.')

app = Celery('p0sx')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django apps.
app.autodiscover_tasks(settings.INSTALLED_APPS)