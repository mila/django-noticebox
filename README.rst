
Django-noticebox is a reusable Django application which provides functionality
for sending notices to site users. The notices can be displayed when user
signs in, sent by email or both.


This application is inspired by James Tauber's django-notification_ but
it is designed to be much more lightweight.

.. _django-notification: https://github.com/jtauber/django-notification


============
Installation
============

The django-noticebox application can be installed using standard setuptools
`setup.py` script: ::

    $ python setup.py install

Installation using `easy_install` or `pip` is also possible. Alternatively
you can simply put the library anywhere to your `PYTHONPATH`.


=====
Usage
=====


Notice creation
---------------

In the `noticebox.handlers` module are defined following callables for
a notice creation:

    `save_notice(users, preset=None, **kwargs)`

        Creates a notice model instance and saves it in the database.

    `mail_notice(users, preset=None, **kwargs)`

        Creates an email messages with the notice and sends it.

    `user_notice(users, preset=None, **kwargs)`

        Saves notice in the database and sends email. Effectively calls
        both `save_notice` and `mail_notice`.

All the handlers follow same signature. The first argument should be
a user instance, a user list or a user queryset. The subject and body strings
should be given as keyword arguments: ::

    user_notice(user, subject="Hello!", body="Hello,\nhow are you?")

The `save_notice` and `mail_notice` handlers are actually class instances so
they can be customized if necessary.


Notice templates
................

The actual subjects and bodies are rendered using Django template
system:

    `notices/default/email_subject.txt`

        Renders an email subject. By default returns given subject unchanged.
        This template can be customized if (for example) a common prefix should
        be added.

    `notices/default/email_body.txt`

        Renders an email body. By default returns given body unchanged.
        This template can be customized if (for example) a common footer should
        be added.

    `notices/default/web_subject.html`

        Renders a notice subject to be displayed on the website.
        By default returns the given subject HTML escaped.

    `notices/default/web_body.html`

        Renders a notice body to be displayed on the website.
        By default returns the given subject HTML escaped and new lines
        replaced by HTML paragraphs (using `linebreaks` template filter).



Presets (alternative templates)
...............................

The handlers do not actually require any specific keyword arguments
(neither `subject` nor `body`). The given keyword arguments are simply passed
to the template in the context.

Non-default templates will be used if a `preset` argument is specified.
For example following call will render tamplates in the `notices/welcome/`
directory with the `username` variable in the context: ::

    user_notice(user, preset="welcome", username="alice")



Notice display (views)
----------------------

Notices in a database can be displayed on the web site when user logs in.
Two class based views are defined in the `noticebox.views` module:

    `NoticeListView`

        Displays paginated list of notices for the authenticated user.

    `NoticeDetailView`

        Display notice detail and marks it as read.


Both views  are included in the `noticebox.urls` urlpatterns which means that if
no customization is needed then they can be simply included in the url
configuration: ::

    urlpatterns = patterns('',
        # ...
        (r'^notices/', include('noticebox.urls')),
        # ...
    )

Simple templates for the views are present but it may be better to override
them for real projects.

Context processor
-----------------

The application provides a context processor which makes count of unread
messages available in the template: ::

    TEMPLATE_CONTEXT_PROCESSORS = (
        # ...
        'noticebox.context_processors.notices',
        # ...
    )

The unread notice count is available in the `notice_unread_count`
variable. No database queries are executed until it is necessary.


=======
Testing
=======


All tests can be discovered and run the Django test runner. For simplicity
minimal Django settings are provided so all the tests can be run using
Django admin utility like this: ::

    django-admin.py test noticebox \
        --settings=noticebox.tests.settings --pythonpath=$PWD
