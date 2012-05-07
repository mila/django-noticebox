
import os

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase


TEMPLATE_DIRS = [os.path.abspath('%s/../templates/' % __file__)]


class AbstractNoticeTestCase(TestCase):
    """
    Base class for tests defined in this application.
    """

    def __call__(self, *args, **kwargs):
        with self.settings(TEMPLATE_DIRS=TEMPLATE_DIRS):
            super(AbstractNoticeTestCase, self).__call__(*args, **kwargs)

    @property
    def mail_outbox(self):
        return getattr(mail, 'outbox', [])


    def create_user(self, username='alice'):
        email = '%s@example.com' % username
        return User.objects.create_user(username, email, username)
