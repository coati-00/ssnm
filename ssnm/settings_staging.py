# flake8: noqa
from settings_shared import *

TEMPLATE_DIRS = (
    "/var/www/ssnm/ssnm/ssnm/templates",
)

MEDIA_ROOT = '/var/www/ssnm/uploads/'
# put any static media here to override app served static media
STATICMEDIA_MOUNTS = (
    ('/sitemedia', '/var/www/ssnm/ssnm/sitemedia'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ssnm',
        'HOST': '',
        'PORT': 6432,
        'USER': '',
        'PASSWORD': '',
    }
}

COMPRESS_ROOT = "/var/www/ssnm/ssnm/media/"
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
DEBUG = True
TEMPLATE_DEBUG = DEBUG
STAGING_ENV = True

if 'migrate' not in sys.argv:
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')

STATSD_PREFIX = 'ssnm-staging'

try:
    from local_settings import *
except ImportError:
    pass
