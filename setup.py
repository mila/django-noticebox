#!/usr/bin/env python

import codecs
import os
from setuptools import setup, find_packages


url='http://github.com/mila/django-noticebox/tree/master'

try:
    long_description = codecs.open('README.rst', "r", "utf-8").read()
except IOError:
    long_description = "See %s" % url


setup(
    name='django-noticebox',
    version=__import__("noticebox").__version__,
    description='Django-noticebox is a reusable Django application which '
                'provides functionality for sending notices to site users. '
                'The notices can be displayed when user signs in, '
                'sent by email or both.',
    long_description=long_description,
    author='Miloslav Pojman',
    author_email='miloslav.pojman@gmail.com',
    url=url,
    packages=find_packages(),
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
)
