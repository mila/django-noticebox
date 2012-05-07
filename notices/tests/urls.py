
from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url('^notices/', include('notices.urls')),
)