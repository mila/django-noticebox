
from django.core.mail import EmailMessage
from django.core.mail import get_connection
from django.template import Context
from django.template.loader import get_template

from notices.models import Notice


class TemplateHandler(object):


    default_preset = 'default'
    default_subject_template = None
    default_body_template = None

    def __init__(self, preset=None, subject_template=None, body_template=None, **kwargs):
        self.preset = preset or self.default_preset
        self.subject_template = subject_template or self.default_subject_template
        self.body_template = body_template or self.default_body_template
        super(TemplateHandler, self).__init__(**kwargs)

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


class DatabaseHandler(TemplateHandler):

    default_subject_template = 'notices/%(preset)s/web_subject.html'
    default_body_template = 'notices/%(preset)s/web_body.html'

    def __init__(self, **kwargs):
        super(DatabaseHandler, self).__init__(**kwargs)

    def __call__(self, users, preset=None, **kwargs):
        """
        Creates notices and sends them in database.
        """
        if preset is None:
            preset = self.preset
        messages = [
            self.create_notice(user, preset, **kwargs)
            for user in users
        ]
        self.save_notices(messages)

    def create_notice(self, user, preset, **kwargs):
        """
        Creates and returns Notice instances for the given user.
        """
        context = self.get_context(user, **kwargs)
        subject = self.get_subject_template(user, preset).render(context)
        body = self.get_body_template(user, preset).render(context)
        return Notice(user=user, subject=subject, body=body)

    def save_notices(self, notices):
        """
        Saves given notices to database.
        """
        Notice.objects.bulk_create(notices)


class EmailHandler(TemplateHandler):

    default_subject_template = 'notices/%(preset)s/email_subject.txt'
    default_body_template = 'notices/%(preset)s/email_body.txt'

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
        if preset is None:
            preset = self.preset
        if fail_silently is None:
            fail_silently = self.fail_silently
        messages = [
            self.create_message(user, preset, **kwargs)
            for user in users
        ]
        self.send_messages(messages, fail_silently=fail_silently)

    def create_message(self, user, preset, **kwargs):
        """
        Creates and returns an email message for the given user.
        """
        context = self.get_context(user, **kwargs)
        subject = self.get_subject_template(user, preset).render(context)
        body = self.get_body_template(user, preset).render(context)
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
