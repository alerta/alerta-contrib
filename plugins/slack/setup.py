#!/usr/bin/env python

import setuptools

version = '0.1.3'

setuptools.setup(
    name="alerta-slack",
    version=version,
    description='Alerta plugin for Slack',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    py_modules=['slack'],
    install_requires=[
        'requests',
        'alerta-server'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'alerta.plugins': [
            'slack = slack:ServiceIntegration'
        ]
    }
)
