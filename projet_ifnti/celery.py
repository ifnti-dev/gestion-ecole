
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet_ifnti.settings")
app = Celery("projet_ifnti")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
