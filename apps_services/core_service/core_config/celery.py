import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_config.settings.py')

app = Celery('sistema_frequencia')
# Usando RabbitMQ como Broker
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()