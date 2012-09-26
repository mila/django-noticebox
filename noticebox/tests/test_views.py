
from noticebox.models import Notice
from noticebox.tests.base import BaseNoticeTestCase


__all__ = ('NoticeListViewTestCase', 'NoticeDetailViewTestCase')


class NoticeListViewTestCase(BaseNoticeTestCase):
    """
    Tests the `NoticeListView` class.
    """

    urls = 'noticebox.tests.urls'

    def setUp(self):
        self.user = self.create_user('alice')
        self.notice = Notice.objects.create(
            user=self.user, subject='Hello <i>alice</i>!',
            body='Hello <i>alice</i>, how are you?',
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
        self.assertContains(r, 'Hello <i>alice</i>!')


class NoticeDetailViewTestCase(BaseNoticeTestCase):
    """
    Tests the `NoticeDetailView` class.
    """

    urls = 'noticebox.tests.urls'

    def setUp(self):
        self.user = self.create_user('alice')
        self.notice = Notice.objects.create(
            user=self.user, subject='Hello <i>alice</i>!',
            body='Hello <i>alice</i>, how are you?',
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
        self.assertContains(r, 'Hello <i>alice</i>!')
        self.assertContains(r, 'Hello <i>alice</i>, how are you?')

    def test_notice_is_marked_as_read(self):
        self.client.login(username='alice', password='alice')
        self.client.get(self.url)
        notice = Notice.objects.get(id=self.notice.id)
        self.assertTrue(notice.is_read)
