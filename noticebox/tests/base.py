
import os

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase


TEMPLATE_DIRS = [os.path.abspath('%s/../templates/' % __file__)]
TEMPLATE_CONTEXT_PROCESSORS = ['noticebox.context_processors.notices']


class BaseNoticeTestCase(TestCase):
    """
    Base class for tests defined in this application.
    """

    def __call__(self, *args, **kwargs):
        with self.settings(
                TEMPLATE_DIRS=TEMPLATE_DIRS,
                TEMPLATE_CONTEXT_PROCESSORS=TEMPLATE_CONTEXT_PROCESSORS,
                DEFAULT_FROM_EMAIL='admin@example.com'):
            super(BaseNoticeTestCase, self).__call__(*args, **kwargs)

    @property
    def mail_outbox(self):
        return getattr(mail, 'outbox', [])

    def create_user(self, username='alice', email=None):
        if email is None:
            email = '%s@example.com' % username
        return User.objects.create_user(username, email, username)
