#!/usr/bin/env python

import setuptools

version = '0.1.2'

setuptools.setup(
    name="alerta-influxdb",
    version=version,
    description='Alerta plugin for InfluxDB',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    py_modules=['influxdb'],
    install_requires=[
        'requests',
        'alerta-server'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'alerta.plugins': [
            'influxdb = influxdb:InfluxDBWrite'
        ]
    }
)
