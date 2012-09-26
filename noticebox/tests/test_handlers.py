
from django.core.mail.backends.locmem import EmailBackend as LocMemEmailBackend

from noticebox.handlers import EmailHandler, DatabaseHandler, user_notice
from noticebox.models import Notice
from noticebox.tests.base import BaseNoticeTestCase


__all__ = ('DatabaseHandlerTestCase', 'EmailHandlerTestCase',
           'UserNoticeShortcutTestCase')


class DatabaseHandlerTestCase(BaseNoticeTestCase):
    """
    Tests the `DatabaseHandler` class.
    """

    def create_handler(self, **kwargs):
        return DatabaseHandler(**kwargs)

    def test_notice_to_empty_list(self):
        handler = self.create_handler()
        handler([])
        self.assertEqual(0, Notice.objects.count())

    def test_notice_to_single_user(self):
        handler = self.create_handler()
        handler(self.create_user())
        self.assertEqual(1, Notice.objects.count())

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
        subject_template = 'noticebox/hello/web_subject.html'
        handler = self.create_handler(subject_template=subject_template)
        handler([self.create_user()])
        notice = Notice.objects.get()
        self.assertEqual('Hello alice!',  notice.subject)

    def test_custom_body_template(self):
        body_template='noticebox/hello/web_body.html'
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

    def test_subject_is_escaped(self):
        handler = self.create_handler()
        handler([self.create_user()], subject='<script>', body='')
        self.assertEqual('&lt;script&gt;', Notice.objects.get().subject)

    def test_body_is_escaped(self):
        handler = self.create_handler()
        handler([self.create_user()], subject='', body='<script>')
        self.assertEqual('<p>&lt;script&gt;</p>', Notice.objects.get().body)


class EmailHandlerTestCase(BaseNoticeTestCase):
    """
    Tests the `EmailHandler` class.
    """

    def create_handler(self, **kwargs):
        return EmailHandler(**kwargs)

    def test_send_to_empty_list(self):
        handler = self.create_handler()
        handler([])
        self.assertEqual(0, len(self.mail_outbox))

    def test_send_to_single_user(self):
        handler = self.create_handler()
        handler(self.create_user())
        self.assertEqual(1, len(self.mail_outbox))

    def test_send_to_user_list(self):
        handler = self.create_handler()
        handler([self.create_user('alice'), self.create_user('bob')])
        self.assertEqual(2, len(self.mail_outbox))

    def test_email_subject(self):
        handler = self.create_handler()
        handler([self.create_user()], subject='Test subject', body='Test body')
        self.assertEqual('Test subject', self.mail_outbox[0].subject)

    def test_email_body(self):
        handler = self.create_handler()
        handler([self.create_user()], subject='Test subject', body='Test body')
        self.assertEqual('Test body', self.mail_outbox[0].body)

    def test_from_email(self):
        handler = self.create_handler()
        handler([self.create_user()], subject='Test subject', body='Test body')
        self.assertEqual('admin@example.com', self.mail_outbox[0].from_email)

    def test_to_email(self):
        handler = self.create_handler()
        handler([self.create_user()], subject='Test subject', body='Test body')
        self.assertEqual(['alice@example.com'], self.mail_outbox[0].to)

    def test_fail_silently_none(self):
        backend = 'noticebox.tests.test_handlers.BrokenEmailBackend'
        handler = self.create_handler(backend=backend)
        with self.assertRaises(IOError):
            handler([self.create_user()], subject='Test subject', body='Test body')
        self.assertEqual(0, len(self.mail_outbox))

    def test_fail_silently_all(self):
        backend = 'noticebox.tests.test_handlers.BrokenEmailBackend'
        handler = self.create_handler(backend=backend, fail_silently=True)
        handler([self.create_user()], subject='Test subject', body='Test body')
        self.assertEqual(0, len(self.mail_outbox))

    def test_fail_silently_single(self):
        backend = 'noticebox.tests.test_handlers.BrokenEmailBackend'
        handler = self.create_handler(backend=backend)
        handler([self.create_user()], subject='Test subject', body='Test body',
                fail_silently=True)
        self.assertEqual(0, len(self.mail_outbox))

    def test_custom_from_email(self):
        handler = self.create_handler(from_email='test@example.com')
        handler([self.create_user()], subject='Test subject', body='Test body')
        self.assertEqual('test@example.com', self.mail_outbox[0].from_email)

    def test_custom_subject_template(self):
        subject_template = 'noticebox/hello/email_subject.txt'
        handler = self.create_handler(subject_template=subject_template)
        handler([self.create_user()])
        self.assertEqual('Hello alice!',  self.mail_outbox[0].subject)

    def test_custom_body_template(self):
        body_template='noticebox/hello/email_body.txt'
        handler = self.create_handler(body_template=body_template)
        handler([self.create_user()])
        self.assertEqual('Hello alice, how are you?',  self.mail_outbox[0].body)

    def test_preset_subject_template_all(self):
        handler = self.create_handler(preset='hello')
        handler([self.create_user()])
        self.assertEqual('Hello alice!',  self.mail_outbox[0].subject)

    def test_preset_body_template_all(self):
        handler = self.create_handler(preset='hello')
        handler([self.create_user()])
        self.assertEqual('Hello alice, how are you?',  self.mail_outbox[0].body)

    def test_preset_subject_template_single(self):
        handler = self.create_handler()
        handler([self.create_user()], preset='hello')
        self.assertEqual('Hello alice!',  self.mail_outbox[0].subject)

    def test_preset_body_template_single(self):
        handler = self.create_handler()
        handler([self.create_user()], preset='hello')
        self.assertEqual('Hello alice, how are you?',  self.mail_outbox[0].body)

    def test_user_without_email_is_skipped(self):
        handler = self.create_handler()
        handler([self.create_user(email='')], subject='Test subject', body='Test body')
        self.assertEqual(0,  len(self.mail_outbox))


class UserNoticeShortcutTestCase(BaseNoticeTestCase):
    """
    Tests the `user_notice` shortcut.
    """

    def test_handle_empty_list(self):
        user_notice([])
        self.assertEqual(0, Notice.objects.count())
        self.assertEqual(0, len(self.mail_outbox))

    def test_handle_single_user(self):
        user_notice(self.create_user())
        self.assertEqual(1, Notice.objects.count())
        self.assertEqual(1, len(self.mail_outbox))

    def test_handle_user_list(self):
        user_notice([self.create_user('alice'), self.create_user('bob')])
        self.assertEqual(2, Notice.objects.count())
        self.assertEqual(2, len(self.mail_outbox))


class BrokenEmailBackend(LocMemEmailBackend):
    """
    Fake email backend used for testing fail_silently option.
    """

    def send_messages(self, messages):
        if self.fail_silently:
            pass
        else:
            raise IOError("This email backend is broken")
