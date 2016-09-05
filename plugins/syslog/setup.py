#!/usr/bin/env python

import setuptools

version = '0.2.0'

setuptools.setup(
    name="alerta-logger",
    version=version,
    description='Alerta plugin for syslog logging',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    py_modules=['logger'],
    install_requires=[
        'alerta-server'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'alerta.plugins': [
            'syslog = logger:Syslog'
        ]
    }
)
