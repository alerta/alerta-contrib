#!/usr/bin/env python

import setuptools

version = '0.2.1'

setuptools.setup(
    name="alerta-normalise",
    version=version,
    description='Alerta plugin for alert normalisation',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    py_modules=['alerta_normalise'],
    install_requires=[
        'alerta-server'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'alerta.plugins': [
            'normalise = alerta_normalise:NormaliseAlert'
        ]
    }
)
