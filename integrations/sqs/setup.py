#!/usr/bin/env python

import setuptools

version = '3.3.0'

setuptools.setup(
    name="alerta-sqs",
    version=version,
    description='Alerta integration for AWS SQS',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    py_modules=['alerta_sqs'],
    install_requires=[
        'alerta',
        'boto'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'alerta-sqs = alerta_sqs:main'
        ]
    },
    keywords="alerta monitoring amazon sqs",
    classifiers=[
        'Topic :: System :: Monitoring',
    ]
)
