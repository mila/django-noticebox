
from django.core.mail import EmailMessage
from django.core.mail import get_connection
from django.template import Context
from django.template.loader import get_template


class EmailHandler(object):

    default_preset = 'default'
    default_subject_template = 'notices/%(preset)s/email_subject.txt'
    default_body_template = 'notices/%(preset)s/email_body.txt'

    def __init__(self, backend=None, backend_options=None,
                  fail_silently=False, from_email=None, preset=None,
                  subject_template=None, body_template=None):
        self.backend = backend
        self.backend_options = backend_options
        self.fail_silently = fail_silently
        self.from_email = from_email
        self.preset = preset or self.default_preset
        self.subject_template = subject_template or self.default_subject_template
        self.body_template = body_template or self.default_body_template

    def __call__(self, users, fail_silently=None, preset=None, **kwargs):
        """
        Creates email messages with notice and sends them.
        """
        if fail_silently is None:
            fail_silently = self.fail_silently
        if preset is None:
            preset = self.preset
        messages = [
            self.create_message(user, preset=preset, **kwargs)
            for user in users
        ]
        connection = self.get_connection(fail_silently=fail_silently)
        connection.send_messages(messages)

    def get_connection(self, fail_silently):
        """
        Returns an email backend to be used for email sending.
        """
        backend_options = self.backend_options or {}
        return get_connection(self.backend, fail_silently=fail_silently,
                              **backend_options)

    def create_message(self, user, preset, **kwargs):
        """
        Creates and returns an email message for the given user.
        """
        context = self.get_context(user, **kwargs)
        subject = self.get_subject_template(user, preset).render(context)
        body = self.get_body_template(user, preset).render(context)
        return EmailMessage(from_email=self.from_email, to=[user.email],
                            subject=subject, body=body)

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
