#!/usr/bin/env python

import setuptools

version = '0.1.1'

setuptools.setup(
    name="alerta-twilio",
    version=version,
    description='Alerta plugin for Twilio SMS',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    py_modules=['alerta_twilio_sms'],
    install_requires=[
        'twilio',
        'alerta-server'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'alerta.plugins': [
            'twilio_sms = alerta_twilio_sms:SendSMSMessage'
        ]
    }
)
