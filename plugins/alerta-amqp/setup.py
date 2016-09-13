#!/usr/bin/env python

import setuptools

version = '0.2.1'

setuptools.setup(
    name="alerta-amqp",
    version=version,
    description='Alerta plugin for AMQP messaging',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    py_modules=['alerta_amqp'],
    install_requires=[
        'alerta-server',
        'kombu'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'alerta.plugins': [
            'amqp = alerta_amqp:FanoutPublisher'
        ]
    }
)
