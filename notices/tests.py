
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core import mail
from django.core.mail.backends.locmem import EmailBackend as LocMemEmailBackend
from django.test import TestCase

from notices.handlers import EmailHandler, DatabaseHandler
from notices.models import Notice


class BrokenEmailBackend(LocMemEmailBackend):

    def send_messages(self, messages):
        if self.fail_silently:
            pass
        else:
            raise IOError("This email backend is broken")


class DatabaseHandlerTestCase(TestCase):

    def create_handler(self, **kwargs):
        return DatabaseHandler(**kwargs)

    def create_user(self, username='alice'):
        email = '%s@example.com' % username
        return User.objects.create_user(username, email)

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
        subject_template = 'notices/test/email_subject.txt'
        handler = self.create_handler(subject_template=subject_template)
        handler([self.create_user()], subject='Test subject', body='Test body',
                site=Site.objects.get_current())
        notice = Notice.objects.get()
        self.assertTrue('Test subject' in notice.subject)
        self.assertTrue('example.com' in notice.subject)

    def test_custom_body_template(self):
        body_template='notices/test/email_body.txt'
        handler = self.create_handler(body_template=body_template)
        handler([self.create_user()], subject='Test subject', body='Test body',
                site=Site.objects.get_current())
        notice = Notice.objects.get()
        self.assertTrue('Test body' in notice.body)
        self.assertTrue('http://example.com/' in notice.body)

    def test_preset_subject_template_all(self):
        handler = self.create_handler(preset='test')
        handler([self.create_user()], subject='Test subject', body='Test body',
                site=Site.objects.get_current())
        notice = Notice.objects.get()
        self.assertTrue('Test subject' in notice.subject)
        self.assertTrue('example.com' in notice.subject)

    def test_preset_body_template_all(self):
        handler = self.create_handler(preset='test')
        handler([self.create_user()], subject='Test subject', body='Test body',
                site=Site.objects.get_current())
        notice = Notice.objects.get()
        self.assertTrue('Test body' in notice.body)
        self.assertTrue('http://example.com/' in notice.body)

    def test_preset_subject_template_single(self):
        handler = self.create_handler()
        handler([self.create_user()], subject='Test subject', body='Test body',
                preset='test', site=Site.objects.get_current())
        notice = Notice.objects.get()
        self.assertTrue('Test subject' in notice.subject)
        self.assertTrue('example.com' in notice.subject)

    def test_preset_body_template_single(self):
        handler = self.create_handler()
        handler([self.create_user()], subject='Test subject', body='Test body',
                preset='test', site=Site.objects.get_current())
        notice = Notice.objects.get()
        self.assertTrue('Test body' in notice.body)
        self.assertTrue('http://example.com/' in notice.body)



class EmailHandlerTestCase(TestCase):

    @property
    def outbox(self):
        return getattr(mail, 'outbox', [])

    def create_handler(self, **kwargs):
        return EmailHandler(**kwargs)

    def create_user(self, username='alice'):
        email = '%s@example.com' % username
        return User.objects.create_user(username, email)

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
        backend = 'notices.tests.BrokenEmailBackend'
        handler = self.create_handler(backend=backend)
        with self.assertRaises(IOError):
            handler([self.create_user()], subject='Test subject', body='Test body')
        self.assertEqual(0, len(self.outbox))

    def test_fail_silently_all(self):
        backend = 'notices.tests.BrokenEmailBackend'
        handler = self.create_handler(backend=backend, fail_silently=True)
        handler([self.create_user()], subject='Test subject', body='Test body')
        self.assertEqual(0, len(self.outbox))

    def test_fail_silently_single(self):
        backend = 'notices.tests.BrokenEmailBackend'
        handler = self.create_handler(backend=backend)
        handler([self.create_user()], subject='Test subject', body='Test body',
                fail_silently=True)
        self.assertEqual(0, len(self.outbox))

    def test_custom_from_email(self):
        handler = self.create_handler(from_email='test@example.com')
        handler([self.create_user()], subject='Test subject', body='Test body')
        self.assertEqual('test@example.com', self.outbox[0].from_email)

    def test_custom_subject_template(self):
        subject_template = 'notices/test/email_subject.txt'
        handler = self.create_handler(subject_template=subject_template)
        handler([self.create_user()], subject='Test subject', body='Test body',
                site=Site.objects.get_current())
        self.assertTrue('Test subject' in self.outbox[0].subject)
        self.assertTrue('example.com' in self.outbox[0].subject)

    def test_custom_body_template(self):
        body_template='notices/test/email_body.txt'
        handler = self.create_handler(body_template=body_template)
        handler([self.create_user()], subject='Test subject', body='Test body',
                site=Site.objects.get_current())
        self.assertTrue('Test body' in self.outbox[0].body)
        self.assertTrue('http://example.com/' in self.outbox[0].body)

    def test_preset_subject_template_all(self):
        handler = self.create_handler(preset='test')
        handler([self.create_user()], subject='Test subject', body='Test body',
                site=Site.objects.get_current())
        self.assertTrue('Test subject' in self.outbox[0].subject)
        self.assertTrue('example.com' in self.outbox[0].subject)

    def test_preset_body_template_all(self):
        handler = self.create_handler(preset='test')
        handler([self.create_user()], subject='Test subject', body='Test body',
                site=Site.objects.get_current())
        self.assertTrue('Test body' in self.outbox[0].body)
        self.assertTrue('http://example.com/' in self.outbox[0].body)

    def test_preset_subject_template_single(self):
        handler = self.create_handler()
        handler([self.create_user()], subject='Test subject', body='Test body',
                preset='test', site=Site.objects.get_current())
        self.assertTrue('Test subject' in self.outbox[0].subject)
        self.assertTrue('example.com' in self.outbox[0].subject)

    def test_preset_body_template_single(self):
        handler = self.create_handler()
        handler([self.create_user()], subject='Test subject', body='Test body',
                preset='test', site=Site.objects.get_current())
        self.assertTrue('Test body' in self.outbox[0].body)
        self.assertTrue('http://example.com/' in self.outbox[0].body)
