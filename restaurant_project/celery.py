import os
from celery import Celery

# установите переменную окружения DJANGO_SETTINGS_MODULE,
# указывающую на настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_project.settings')

app = Celery('restaurant_project')

# загрузка настроек Celery из файла настроек Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# автоматическое обнаружение задач в приложениях Django
app.autodiscover_tasks()
