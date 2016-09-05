#!/usr/bin/env python

import setuptools

version = '0.2.1'

setuptools.setup(
    name="alerta-pagerduty",
    version=version,
    description='Alerta plugin for PagerDuty',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    py_modules=['pagerduty'],
    install_requires=[
        'requests',
        'alerta-server'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'alerta.plugins': [
            'pagerduty = pagerduty:TriggerEvent'
        ]
    }
)
