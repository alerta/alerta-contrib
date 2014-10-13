#!/usr/bin/env python

import setuptools

version = '3.3.0'

setuptools.setup(
    name="alerta-syslog",
    version=version,
    description='Alerta script for Syslog messages',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    py_modules=['syslog', 'transform', 'settings'],
    install_requires=[
        'alerta'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'alerta-syslog = syslog:main'
        ]
    },
    keywords="alerta syslog monitoring",
    classifiers=[
        'Topic :: System :: Monitoring',
    ]
)
