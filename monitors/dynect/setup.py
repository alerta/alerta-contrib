#!/usr/bin/env python

import setuptools

setuptools.setup(
    name="alerta-dynect",
    version='3.3.0',
    description='Alerta script for Dynect DNS alerts',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Nick Satterly',
    author_email='diego.vazquez@theguardian.com',
    py_modules=['dynmon'],
    install_requires=[
        'alerta',
        'DynectDNS'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'alerta-dynect = dynmon:main'
        ]
    },
    keywords="alerta Dynect DNS monitoring",
    classifiers=[
        'Topic :: System :: Monitoring',
    ]
)
