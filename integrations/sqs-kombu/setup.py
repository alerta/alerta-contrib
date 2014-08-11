#!/usr/bin/env python

import setuptools

version = '0.1.0'

setuptools.setup(
    name="alerta-sqs",
    version=version,
    description='Alerta daemon for AWS SQS',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    py_modules=['sqs'],
    install_requires=[
        'alerta'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'alerta.plugins': [
            'influxdb = influxdb:InfluxDBWrite'
        ]
    }
)
