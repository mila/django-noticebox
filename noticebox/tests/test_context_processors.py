
from django.contrib.auth.models import AnonymousUser
from django.template.context import RequestContext
from django.test.client import RequestFactory

from noticebox.models import Notice
from noticebox.tests.base import BaseNoticeTestCase


__all__ = ('NoticesContextPreprocessorTestCase',)


class NoticesContextPreprocessorTestCase(BaseNoticeTestCase):
    """
    Tests the `notices` context preprocessor.
    """

    def setUp(self):
        self.user = self.create_user()
        self.notice = Notice.objects.create(
            user=self.user, subject='Hello', body='')

    def test_count_is_not_in_context_if_no_user(self):
        request = RequestFactory().get('/')
        context = RequestContext(request)
        self.assertFalse('notice_unread_count' in context)

    def test_count_is_not_in_context_if_anonymous(self):
        request = RequestFactory().get('/')
        request.user = AnonymousUser()
        context = RequestContext(request)
        self.assertFalse('notice_unread_count' in context)

    def test_count_is_in_context_if_authenticated(self):
        request = RequestFactory().get('/')
        request.user = self.user
        context = RequestContext(request)
        self.assertTrue('notice_unread_count' in context)

    def test_only_unread_notices_are_counted(self):
        self.notice.is_read = True
        self.notice.save()
        request = RequestFactory().get('/')
        request.user = self.user
        context = RequestContext(request)
        value = context['notice_unread_count']
        self.assertEqual(0, value())

    def test_value_is_cached(self):
        request = RequestFactory().get('/')
        request.user = self.user
        with self.assertNumQueries(1):
            context = RequestContext(request)
            value = context['notice_unread_count']
            self.assertEqual(1, value())
            self.assertEqual(1, value())
