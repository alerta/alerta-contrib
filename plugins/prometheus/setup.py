#!/usr/bin/env python

import setuptools

version = '0.1.0'

setuptools.setup(
    name="alerta-prometheus",
    version=version,
    description='Alerta plugin for Prometheus Alertmanager',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    py_modules=['prometheus'],
    install_requires=[
        'requests',
        'alerta-server'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'alerta.plugins': [
            'prometheus = prometheus:AlertmanagerSilence'
        ]
    }
)
