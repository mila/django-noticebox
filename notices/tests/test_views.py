
from django.contrib.auth.models import User

from notices.models import Notice
from notices.tests.base import AbstractNoticeTestCase


__all__ = ('NoticeListViewTestCase', 'NoticeDetailViewTestCase')


class NoticeListViewTestCase(AbstractNoticeTestCase):
    """
    Tests the NoticeListView class.
    """

    urls = 'notices.tests.urls'

    def setUp(self):
        self.user = self.create_user('alice')
        self.notice = Notice.objects.create(
            user=self.user, subject='Hello alice!',
            body='Hello alice, how are you?',
        )

    def test_returns_302_if_not_logged_in(self):
        r = self.client.get('/notices/')
        self.assertEqual(302, r.status_code)

    def test_returns_200_if_logged_in(self):
        self.client.login(username='alice', password='alice')
        r = self.client.get('/notices/')
        self.assertEqual(200, r.status_code)

    def test_response_contains_notice_url(self):
        self.client.login(username='alice', password='alice')
        r = self.client.get('/notices/')
        self.assertContains(r, '/notices/%d/' % self.notice.id)

    def test_response_contains_notice_subject(self):
        self.client.login(username='alice', password='alice')
        r = self.client.get('/notices/')
        self.assertContains(r, 'Hello alice!')


class NoticeDetailViewTestCase(AbstractNoticeTestCase):
    """
    Tests the NoticeDetailView class.
    """

    urls = 'notices.tests.urls'

    def setUp(self):
        self.user = self.create_user('alice')
        self.notice = Notice.objects.create(
            user=self.user, subject='Hello alice!',
            body='Hello alice, how are you?',
        )
        self.url = '/notices/%d/' % self.notice.id

    def test_returns_302_if_not_logged_in(self):
        r = self.client.get(self.url)
        self.assertEqual(302, r.status_code)

    def test_returns_200_if_logged_in(self):
        self.client.login(username='alice', password='alice')
        r = self.client.get(self.url)
        self.assertEqual(200, r.status_code)

    def test_response_contains_notice_subject_and_body(self):
        self.client.login(username='alice', password='alice')
        r = self.client.get(self.url)
        self.assertContains(r, 'Hello alice!')
        self.assertContains(r, 'Hello alice, how are you?')

    def test_notice_is_marked_as_read(self):
        self.client.login(username='alice', password='alice')
        self.client.get(self.url)
        notice = Notice.objects.get(id=self.notice.id)
        self.assertTrue(notice.is_read)
