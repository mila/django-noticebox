"""
Handlers define how are notices created and delivered to the users.

Two handlers are implemented. DatabaseHandler saves notices in the database
and EmailHandler sends notices using email messages. Both of them are
implemented as callable classes so that they can be easily customized.

If the default functionality is sufficient then `save_notice`
and `mail_notice` global instances can be used (and class bases
implementation can be ignored). The `user_notice` function is a shortcut
for calling both `save_notice` and `mail_notice`.
"""


from django.core.mail import EmailMessage
from django.core.mail import get_connection
from django.template import Context
from django.template.loader import get_template

from noticebox.models import Notice


def _user_list(user_or_user_list):
    if hasattr(user_or_user_list, 'email'):
        return [user_or_user_list]
    return user_or_user_list


class BaseHandler(object):
    """
    Provides common functionality to both DatabaseHandler and EmailHandler.
    """

    default_preset = 'default'
    default_subject_template = None
    default_body_template = None

    def __init__(self, preset=None, subject_template=None, body_template=None,
                 **kwargs):
        self.preset = preset or self.default_preset
        self.subject_template = subject_template or self.default_subject_template
        self.body_template = body_template or self.default_body_template
        super(BaseHandler, self).__init__(**kwargs)

    def render(self, user, preset=None, **kwargs):
        """
        Renders and returns notice subject and body.
        """
        if preset is None:
            preset = self.preset
        context = self.get_context(user, **kwargs)
        subject = self.get_subject_template(user, preset).render(context)
        body = self.get_body_template(user, preset).render(context)
        return subject, body

    def get_context(self, user, **kwargs):
        """
        Returns a template context for subject and body rendering.
        """
        return Context(dict(kwargs, user=user))

    def get_subject_template(self, user, preset):
        """
        Returns a template to be used for subject rendering.
        """
        return get_template(self.subject_template % {'preset': preset})

    def get_body_template(self, user, preset):
        """
        Returns a template to be used for body rendering.
        """
        return get_template(self.body_template % {'preset': preset})


class DatabaseHandler(BaseHandler):
    """
    Saves notices in the database so that they can be later displayed on web.
    """

    default_subject_template = 'noticebox/%(preset)s/web_subject.html'
    default_body_template = 'noticebox/%(preset)s/web_body.html'

    def __init__(self, **kwargs):
        super(DatabaseHandler, self).__init__(**kwargs)

    def __call__(self, users, preset=None, **kwargs):
        """
        Creates notices and saves them in database.
        """
        notices = [self.create_notice(user, preset, **kwargs)
                   for user in _user_list(users)]
        self.save_notices(notices)

    def create_notice(self, user, preset, **kwargs):
        """
        Creates and returns Notice instances for the given user.
        """
        subject, body = self.render(user, preset, **kwargs)
        return Notice(user=user, subject=subject, body=body)

    def save_notices(self, notices):
        """
        Saves given notices to database.
        """
        Notice.objects.bulk_create(notices)


class EmailHandler(BaseHandler):
    """
    Sends notices using email.
    """

    default_subject_template = 'noticebox/%(preset)s/email_subject.txt'
    default_body_template = 'noticebox/%(preset)s/email_body.txt'

    def __init__(self, backend=None, backend_options=None,
                fail_silently=False, from_email=None, **kwargs):
        self.backend = backend
        self.backend_options = backend_options
        self.fail_silently = fail_silently
        self.from_email = from_email
        super(EmailHandler, self).__init__(**kwargs)

    def __call__(self, users, preset=None, fail_silently=None, **kwargs):
        """
        Creates email messages with notice and sends them via email.
        """
        if fail_silently is None:
            fail_silently = self.fail_silently
        messages = [self.create_message(user, preset, **kwargs)
                    for user in _user_list(users) if user.email]
        self.send_messages(messages, fail_silently=fail_silently)

    def create_message(self, user, preset, **kwargs):
        """
        Creates and returns an email message for the given user.
        """
        subject, body = self.render(user, preset, **kwargs)
        return EmailMessage(from_email=self.from_email, to=(user.email,),
                            subject=subject, body=body)

    def send_messages(self, messages, fail_silently):
        """
        Returns an email backend to be used for email sending.
        """
        backend_options = self.backend_options or {}
        connection = get_connection(self.backend, fail_silently=fail_silently,
                                    **backend_options)
        connection.send_messages(messages)


save_notice = DatabaseHandler()
mail_notice = EmailHandler()

def user_notice(users, preset=None, fail_silently=None, **kwargs):
    """
    Saves notices in database and also sends them via email.
    """
    save_notice(users, preset, **kwargs)
    mail_notice(users, preset, fail_silently=fail_silently, **kwargs)
