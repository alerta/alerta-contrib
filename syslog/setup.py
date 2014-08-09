#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="alerta-syslog",
    version='3.2.0',
    description="Alerta Syslog daemon",
    license="MIT",
    author="Nick Satterly",
    author_email="nick.satterly@theguardian.com",
    url="http://github.com/alerta/alerta-contrib",
    packages=[''],
    install_requires=[
        'alerta-server',
    ],
    entry_points={
        'console_scripts': [
            'alerta-syslog = syslog:main'
        ]
    },
    keywords="alerta syslog daemon",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Monitoring',
    ]
)

