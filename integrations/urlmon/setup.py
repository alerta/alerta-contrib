#!/usr/bin/env python

import setuptools

version = '3.3.0'

setuptools.setup(
    name="alerta-urlmon",
    version=version,
    description='Alerta script for URL monitoring',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    py_modules=['urlmon'],
    install_requires=[
        'alerta'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'alerta-urlmon = urlmon:main'
        ]
    },
    keywords="alerta url monitoring",
    classifiers=[
        'Topic :: System :: Monitoring',
    ]
)
