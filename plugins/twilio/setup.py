#!/usr/bin/env python

import os

from setuptools import setup, find_packages

version = '0.1.0'

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="alerta-twilio",
    version=version,
    description='Alerta plugin for Twilio SMS',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    packages=find_packages(),
    py_modules=['twilio_sms'],
    install_requires=[
        'twilio',
        'alerta-server'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'alerta.plugins': [
            'twilio_sms = twilio_sms:SendSMSMessage'
        ]
    }
)
