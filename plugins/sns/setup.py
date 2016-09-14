#!/usr/bin/env python

import setuptools

version = '0.2.1'

setuptools.setup(
    name="alerta-sns",
    version=version,
    description='Alerta plugin for AWS SNS',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    py_modules=['alerta_sns'],
    install_requires=[
        'alerta-server',
        'boto'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'alerta.plugins': [
            'sns = alerta_sns:SnsTopicPublisher'
        ]
    }
)
