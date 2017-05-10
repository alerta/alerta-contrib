#!/usr/bin/env python

import setuptools

version = '3.4.3'

setuptools.setup(
    name="alerta-syslog",
    version=version,
    description='Alerta script for Syslog messages',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    py_modules=['syslogfwder'],
    install_requires=[
        'alerta'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'alerta-syslog = syslogfwder:main'
        ]
    },
    keywords="alerta syslog monitoring",
    classifiers=[
        'Topic :: System :: Monitoring',
    ]
)
