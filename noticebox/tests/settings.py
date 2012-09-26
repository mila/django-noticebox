"""
Django settings for testing this application.

The tests can be executed by running a command similar to: ::

    django-admin.py test noticebox \
        --settings=noticebox.tests.settings --pythonpath=$PWD

"""


INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',

    'noticebox',
]

DATABASES = {
    'default': {
        'ENGINE' : 'django.db.backends.sqlite3',
        'NAME' : '',
    },
}

ROOT_URLCONF = 'noticebox.urls'

DEFAULT_FROM_EMAIL = 'admin@example.com'

# Do not slow down test execution.
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
