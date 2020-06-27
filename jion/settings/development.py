import os
from jion.settings.common import *

SECRET_KEY = os.environ.get('SECRET_KEY', '')
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
