
from django.conf.urls import patterns, url

from noticebox.views import NoticeListView, NoticeDetailView


urlpatterns = patterns('',
    url(r'^$', NoticeListView.as_view(), name='notice_list'),
    url(r'^(?P<pk>\d+)/$', NoticeDetailView.as_view(), name='notice_detail'),
)
