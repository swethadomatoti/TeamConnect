from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TeamConnect.settings')#Without this, Celery would be disconnected from your Django project.
app = Celery('TeamConnect')#Manages every tasks
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks() 
