
from django.db import models


class NoticeManager(models.Manager):

    def for_user(self, user):
        return self.get_query_set().filter(user=user)