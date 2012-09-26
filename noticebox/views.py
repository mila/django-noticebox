
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView

from noticebox.models import Notice


class NoticeListView(ListView):
    """
    A view which displays a list of user's notices.
    """

    paginate_by = 20

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NoticeListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return Notice.objects.for_user(self.request.user).order_by('-ctime')


class NoticeDetailView(DetailView):
    """
    A view which displays notice detail and marks is as read.
    """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NoticeDetailView, self).dispatch(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        instance = super(NoticeDetailView, self).get_object(*args, **kwargs)
        instance.is_read = True
        instance.save(force_update=True)
        return instance

    def get_queryset(self):
        return Notice.objects.for_user(self.request.user)
