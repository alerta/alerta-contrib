#!/usr/bin/env python

import setuptools

setuptools.setup(
    name="alerta-snmptrap",
    version='5.0.0',
    description='Alerta script for SNMP traps',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    py_modules=['handler'],
    install_requires=[
        'alerta'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'alerta-snmptrap = handler:main'
        ]
    },
    keywords="alerta snmp trap monitoring",
    classifiers=[
        'Topic :: System :: Monitoring',
    ]
)
