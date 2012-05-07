"""
Django settings for testing this application.

The tests can be executed by running a command similar to: ::

    django-admin.py test notices --settings=notices.test_settings

"""


INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',

    'notices',
]

DATABASES = {
    'default': {
        'ENGINE' : 'django.db.backends.sqlite3',
        'NAME' : '',
        'USER' : '',
        'PASSWORD' : '',
        'HOST' : '',
        'PORT' : '',
    },
}

ROOT_URLCONF = 'notices.urls'

DEFAULT_FROM_EMAIL = 'admin@example.com'

SITE_ID = 1