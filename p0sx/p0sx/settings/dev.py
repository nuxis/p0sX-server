from p0sx.settings.base import *

ALLOWED_HOSTS = ['*']

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'secret'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

SITE_URL = 'https://p0sx.eth0.no/'

# SumUp affiliate key. Create one on your SumUp account with application-id com.polarparty.p0sx
SUMUP_AFFILIATE_KEY = 'b7231c79-0828-4f82-97d1-8f63234b5798'
# SumUp callback hostname, must include http:// or https:// and port if required.
SUMUP_CALLBACK_HOSTNAME = 'https://p0sx.eth0.no/'
# SumUp Merchant code
SUMUP_MERCHANT_CODE = 'MFD3L9DH'
