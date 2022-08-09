from p0sx.settings.base import *

ALLOWED_HOSTS = ['aspargesgaarden.no']

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'secret'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'p0sx',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'p0sx',
        'PASSWORD': '123',
        'HOST': 'localhost',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '5432',                      # Set to empty string for default.
    }
}

# SumUp affiliate key. Create one on your SumUp account with application-id com.polarparty.p0sx
SUMUP_AFFILIATE_KEY = 'b7231c79-0828-4f82-97d1-8f63234b5798'
# SumUp callback hostname, must include http:// or https:// and port if required.
SUMUP_CALLBACK_HOSTNAME = 'https://p0sx.eth0.no/'
# SumUp Merchant code
SUMUP_MERCHANT_CODE = 'MFD3L9DH'

# GeekEvents event id for the current party
GE_EVENT_ID = None
GE_SSO_SUCCESS_REDIRECT = None