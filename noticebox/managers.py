
from django.db import models


class NoticeManager(models.Manager):

    def for_user(self, user):
        """
        Returns all notices for the given user.
        """
        return self.get_query_set().filter(user=user)
