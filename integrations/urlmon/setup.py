#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="alerta-urlmon",
    version='3.2.0',
    description="Alerta URL monitor daemon",
    license="MIT",
    author="Nick Satterly",
    author_email="nick.satterly@theguardian.com",
    url="http://github.com/alerta/alerta-contrib",
    py_modules=['urlmon'],
    install_requires=[
        'alerta-server',
    ],
    entry_points={
        'console_scripts': [
            'alerta-urlmon = urlmon:main'
        ]
    },
    keywords="alerta url monitor daemon",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Monitoring',
    ]
)

