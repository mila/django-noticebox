
from datetime import datetime

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models

from noticebox.managers import NoticeManager


class Notice(models.Model):

    user = models.ForeignKey(User)
    subject = models.CharField(max_length=100)
    body = models.TextField()
    ctime = models.DateTimeField(auto_now_add=True, editable=False)
    atime = models.DateTimeField(null=True, blank=True, editable=False)

    objects = NoticeManager()

    class Meta:
        db_table = 'noticebox_notice'

    def __unicode__(self):
        return self.subject

    def get_absolute_url(self):
        return reverse('notice_detail', kwargs={'pk': self.pk})

    def _get_is_read(self):
        return self.atime is not None
    def _set_is_read(self, value):
        self.atime = datetime.now() if value else None
    is_read = property(_get_is_read, _set_is_read)
    del _get_is_read, _set_is_read
