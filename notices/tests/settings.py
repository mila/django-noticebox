"""
Django settings for testing this application.

The tests can be executed by running a command similar to: ::

    django-admin.py test notices --settings=notices.tests.settings

"""


INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',

    'notices',
]

DATABASES = {
    'default': {
        'ENGINE' : 'django.db.backends.sqlite3',
        'NAME' : '',
    },
}

ROOT_URLCONF = 'notices.urls'

DEFAULT_FROM_EMAIL = 'admin@example.com'

# Do not slow down test execution.
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)