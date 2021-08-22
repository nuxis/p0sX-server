from p0sx.settings.base import *

import environ
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

env = environ.Env()

ENVIRONMENT = env.str('ENVIRONMENT', default='dev')
ALLOWED_HOSTS = env.str('ALLOWED_HOSTS').split(',')

# SECURITY WARNING: keep the secret key used in' production secret!
SECRET_KEY = env.str('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env.str('POSTGRES_DB'),
        'USER': env.str('POSTGRES_USER'),
        'PASSWORD': env.str('POSTGRES_PASSWORD'),
        'HOST': env.str('POSTGRES_HOST'),
        'PORT': '5432',
    }
}

SITE_URL = env.str('SITE_URL')
CELERY_RESULT_BACKEND = 'django-db'
BROKER_URL = 'redis://{host}:{port}/{number}'.format(
    host=env.str('CELERY_BROKER_HOST'),
    port=env.str('CELERY_BROKER_PORT', default='6379'),
    number=env.int('CELERY_BROKER_NUMBER')
),

STATIC_ROOT = env.str('STATIC_ROOT')
MEDIA_ROOT = env.str('MEDIA_ROOT')

SENTRY_DSN = env.str('SENTRY_DSN', default=None)
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), RedisIntegration(), CeleryIntegration()],
        traces_sample_rate=1.0,
        environment=ENVIRONMENT,
        send_default_pii=True,
        release=VERSION
    )