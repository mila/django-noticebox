
import os

from django.contrib.auth.models import User
from django.core import mail
from django.core.mail.backends.locmem import EmailBackend as LocMemEmailBackend
from django.test import TestCase

from notices.handlers import EmailHandler, DatabaseHandler, CompositeHandler
from notices.models import Notice


__all__ = ('DatabaseHandlerTestCase', 'EmailHandlerTestCase',
           'CompositeHandlerTestCase')


TEMPLATE_DIRS = [os.path.abspath('%s/../templates/' % __file__)]


class BrokenEmailBackend(LocMemEmailBackend):
    """
    Fake email backend used for testing fail_silently option.
    """

    def send_messages(self, messages):
        if self.fail_silently:
            pass
        else:
            raise IOError("This email backend is broken")


class AbstractHandlerTestCase(TestCase):

    def __call__(self, *args, **kwargs):
        with self.settings(TEMPLATE_DIRS=TEMPLATE_DIRS):
            super(AbstractHandlerTestCase, self).__call__(*args, **kwargs)

    def create_user(self, username='alice'):
        email = '%s@example.com' % username
        return User.objects.create_user(username, email)


class DatabaseHandlerTestCase(AbstractHandlerTestCase):
    """
    Tests the DatabaseHandler class.
    """

    def create_handler(self, **kwargs):
        return DatabaseHandler(**kwargs)

    def test_notice_to_empty_list(self):
        handler = self.create_handler()
        handler([])
        self.assertEqual(0, Notice.objects.count())

    def test_notice_to_user_list(self):
        handler = self.create_handler()
        handler([self.create_user('alice'), self.create_user('bob')])
        self.assertEqual(2, Notice.objects.count())

    def test_notice_subject(self):
        handler = self.create_handler()
        handler([self.create_user()], subject='Test subject', body='Test body')
        self.assertEqual('Test subject', Notice.objects.get().subject)

    def test_notice_body(self):
        handler = self.create_handler()
        handler([self.create_user()], subject='Test subject', body='Test body')
        self.assertEqual('<p>Test body</p>', Notice.objects.get().body)

    def test_custom_subject_template(self):
        subject_template = 'notices/hello/web_subject.html'
        handler = self.create_handler(subject_template=subject_template)
        handler([self.create_user()])
        notice = Notice.objects.get()
        self.assertEqual('Hello alice!',  notice.subject)

    def test_custom_body_template(self):
        body_template='notices/hello/web_body.html'
        handler = self.create_handler(body_template=body_template)
        handler([self.create_user()])
        notice = Notice.objects.get()
        self.assertEqual('<p>Hello alice, how are you?</p>',  notice.body)

    def test_preset_subject_template_all(self):
        handler = self.create_handler(preset='hello')
        handler([self.create_user()])
        notice = Notice.objects.get()
        self.assertEqual('Hello alice!',  notice.subject)

    def test_preset_body_template_all(self):
        handler = self.create_handler(preset='hello')
        handler([self.create_user()])
        notice = Notice.objects.get()
        self.assertEqual('<p>Hello alice, how are you?</p>',  notice.body)

    def test_preset_subject_template_single(self):
        handler = self.create_handler()
        handler([self.create_user()], preset='hello')
        notice = Notice.objects.get()
        self.assertEqual('Hello alice!',  notice.subject)

    def test_preset_body_template_single(self):
        handler = self.create_handler()
        handler([self.create_user()], preset='hello')
        notice = Notice.objects.get()
        self.assertEqual('<p>Hello alice, how are you?</p>',  notice.body)


class EmailHandlerTestCase(AbstractHandlerTestCase):
    """
    Tests  the EmailHandler class.
    """

    @property
    def outbox(self):
        return getattr(mail, 'outbox', [])

    def create_handler(self, **kwargs):
        return EmailHandler(**kwargs)

    def test_send_to_empty_list(self):
        handler = self.create_handler()
        handler([])
        self.assertEqual(0, len(self.outbox))

    def test_send_to_user_list(self):
        handler = self.create_handler()
        handler([self.create_user('alice'), self.create_user('bob')])
        self.assertEqual(2, len(self.outbox))

    def test_email_subject(self):
        handler = self.create_handler()
        handler([self.create_user()], subject='Test subject', body='Test body')
        self.assertEqual('Test subject', self.outbox[0].subject)

    def test_email_body(self):
        handler = self.create_handler()
        handler([self.create_user()], subject='Test subject', body='Test body')
        self.assertEqual('Test body', self.outbox[0].body)

    def test_from_email(self):
        handler = self.create_handler()
        handler([self.create_user()], subject='Test subject', body='Test body')
        self.assertEqual('admin@example.com', self.outbox[0].from_email)

    def test_to_email(self):
        handler = self.create_handler()
        handler([self.create_user()], subject='Test subject', body='Test body')
        self.assertEqual(['alice@example.com'], self.outbox[0].to)

    def test_fail_silently_none(self):
        backend = 'notices.tests.test_handlers.BrokenEmailBackend'
        handler = self.create_handler(backend=backend)
        with self.assertRaises(IOError):
            handler([self.create_user()], subject='Test subject', body='Test body')
        self.assertEqual(0, len(self.outbox))

    def test_fail_silently_all(self):
        backend = 'notices.tests.test_handlers.BrokenEmailBackend'
        handler = self.create_handler(backend=backend, fail_silently=True)
        handler([self.create_user()], subject='Test subject', body='Test body')
        self.assertEqual(0, len(self.outbox))

    def test_fail_silently_single(self):
        backend = 'notices.tests.test_handlers.BrokenEmailBackend'
        handler = self.create_handler(backend=backend)
        handler([self.create_user()], subject='Test subject', body='Test body',
                fail_silently=True)
        self.assertEqual(0, len(self.outbox))

    def test_custom_from_email(self):
        handler = self.create_handler(from_email='test@example.com')
        handler([self.create_user()], subject='Test subject', body='Test body')
        self.assertEqual('test@example.com', self.outbox[0].from_email)

    def test_custom_subject_template(self):
        subject_template = 'notices/hello/email_subject.txt'
        handler = self.create_handler(subject_template=subject_template)
        handler([self.create_user()])
        self.assertEqual('Hello alice!',  self.outbox[0].subject)

    def test_custom_body_template(self):
        body_template='notices/hello/email_body.txt'
        handler = self.create_handler(body_template=body_template)
        handler([self.create_user()])
        self.assertEqual('Hello alice, how are you?',  self.outbox[0].body)

    def test_preset_subject_template_all(self):
        handler = self.create_handler(preset='hello')
        handler([self.create_user()])
        self.assertEqual('Hello alice!',  self.outbox[0].subject)

    def test_preset_body_template_all(self):
        handler = self.create_handler(preset='hello')
        handler([self.create_user()])
        self.assertEqual('Hello alice, how are you?',  self.outbox[0].body)

    def test_preset_subject_template_single(self):
        handler = self.create_handler()
        handler([self.create_user()], preset='hello')
        self.assertEqual('Hello alice!',  self.outbox[0].subject)

    def test_preset_body_template_single(self):
        handler = self.create_handler()
        handler([self.create_user()], preset='hello')
        self.assertEqual('Hello alice, how are you?',  self.outbox[0].body)


class CompositeHandlerTestCase(AbstractHandlerTestCase):
    """
    Tests the CompositeHandler class.
    """

    @property
    def outbox(self):
        return getattr(mail, 'outbox', [])

    def create_handler(self, **kwargs):
        handler =  CompositeHandler()
        handler.register(DatabaseHandler())
        handler.register(EmailHandler())
        return handler

    def test_handle_empty_list(self):
        handler = self.create_handler()
        handler([])
        self.assertEqual(0, Notice.objects.count())
        self.assertEqual(0, len(self.outbox))

    def test_handle_user_list(self):
        handler = self.create_handler()
        handler([self.create_user('alice'), self.create_user('bob')])
        self.assertEqual(2, Notice.objects.count())
        self.assertEqual(2, len(self.outbox))
