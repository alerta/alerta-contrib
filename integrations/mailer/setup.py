#!/usr/bin/env python

import setuptools

version = '3.3.2'

setuptools.setup(
    name="alerta-mailer",
    version=version,
    description='Send emails from Alerta',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    py_modules=['mailer'],
    data_files=[('.', ['email.tmpl', 'email.html.tmpl'])],
    install_requires=[
        'alerta',
        'kombu',
        'redis',
        'jinja2'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'alerta-mailer = mailer:main'
        ]
    },
    keywords="alerta monitoring mailer sendmail smtp",
    classifiers=[
        'Topic :: System :: Monitoring',
    ]
)
