
from setuptools import setup, find_packages

setup(
    name="alerta-pinger",
    version='3.2.0',
    description="Alerta Pinger daemon",
    license="MIT",
    author="Nick Satterly",
    author_email="nick.satterly@theguardian.com",
    url="http://github.com/alerta/alerta-contrib",
    py_modules=['pinger'],
    install_requires=[
        'alerta',
    ],
    entry_points={
        'console_scripts': [
            'alerta-pinger = pinger:main'
        ]
    },
    keywords="alerta ping daemon",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Monitoring',
    ]
)
