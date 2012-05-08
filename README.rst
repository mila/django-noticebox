
This Django application provides an user notification functionality.
User notices can be send by email, saved in database or both.

Usage
=====


Views
-----

Notices in a database can be displayed on the web site using two simple views
defined in the `notices.views` module:

    `NoticeListView`

        Displays paginated list of notices for the authenticated user.

    `NoticeDetailView`

        Display notice detail and marks it as read.


Both views  are included in the `notices.urls` urlpatterns which means that if
no customization is needed then they can be simply included in the url
configuration: ::

    urlpatterns = patterns('',
        # ...
        (r'^notices/', include('notices.urls')),
        # ...
	)


Notice creation
---------------

Handlers
........

In the `notices.handlers` module are defined following callables for
a notice creation:

    `save_notice`

        Creates a notice model instance and saves it in the database.

    `mail_notice`

        Creates an email messages with the notice and sends it.

    `user_notice`

        Saves notice in the database and sends email. Effectively calls
        both `save_notice` and `mail_notice`.


Default preset (templates)
..........................

All the handlers follow same signature. The first argument should be
a user instance, a user list or a user queryset. The subject and body strings
should be given as keyword arguments: ::

    user_notice(user, subject="Hello!", body="Hello,\nhow are you?")

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
        By default returns given subject HTML escaped.

    `notices/default/web_body.html`

        Renders a notice body to be displayed on the website.
        By default returns given subject HTML escaped and new lines replaced
        by HTML paragraphs (using `linebreaks` template filter).


Custom presets (templates)
..........................

Note that the handlers do not require any specific keyword arguments (like
`subject` or `body`). The given keyword arguments are simply passed to
a template in the context.

Non-default templates will be used if specied in a `preset` argument.
For example following call will render tamplates in the `notices/welcome/`
directory with the `username` variable in the context: ::

    user_notice(user, preset="welcome", username="alice")


Testing
=======

All tests in the application can be run using Django admin utility: ::

	django-admin.py test notices --settings=notices.tests.settings