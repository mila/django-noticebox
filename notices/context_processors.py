
from notices.models import Notice

class LazyCount(object):

    def __init__(self, queryset):
        self.queryset = queryset

    def __call__(self):
        try:
            return self._count
        except AttributeError:
            self._count = self.queryset.count()
        return self._count


def notices(request):
    user = getattr(request, 'user', None)
    if user and user.is_authenticated():
        queryset = Notice.objects.for_user(user).filter(atime=None)
        return {
            'notice_unread_count': LazyCount(queryset),
        }
    return {}