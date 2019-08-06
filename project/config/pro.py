from .settings import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'database1',
        'USER': 'database1_role',
        'PASSWORD': 'database1_password',
        'HOST': 'database1', # <-- Important: same name as docker-compose service
        'PORT': 5432,
    }
}

# EMAIL_HOST = os.getenv('EMAIL_HOST')
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
# EMAIL_PORT = os.getenv('EMAIL_PORT') or 587
# EMAIL_USE_TLS = True

SITE_ID = 1
