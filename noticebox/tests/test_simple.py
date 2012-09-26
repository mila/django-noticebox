
import re

from noticebox.handlers import user_notice
from noticebox.tests.base import BaseNoticeTestCase


__all__ = ('NoticesTestCase',)


class NoticesTestCase(BaseNoticeTestCase):
    """
    A simple test that things work all together.
    """

    urls = 'noticebox.tests.urls'

    def setUp(self):
        self.user = self.create_user('alice')

    def test_all(self):
        # First crate notice
        user_notice([self.user], preset='hello')
        # It should be sent by email
        self.assertEqual(1, len(self.mail_outbox))
        self.assertEqual('Hello alice!', self.mail_outbox[0].subject)
        # And it should be visible on the website
        self.client.login(username='alice', password='alice')
        r = self.client.get('/notices/')
        self.assertEqual(200, r.status_code)
        # With the link to the notice detail
        url_match = re.search(r'/notices/\d+/', r.content)
        self.assertTrue(url_match)
        detail_url = url_match.group()
        r = self.client.get(detail_url)
        self.assertEqual(200, r.status_code)
        self.assertTrue('Hello alice, how are you?' in r.content)
