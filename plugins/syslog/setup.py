
from setuptools import setup, find_packages

version = '0.3.0'

setup(
    name="alerta-logger",
    version=version,
    description='Alerta plugin for syslog logging',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    packages=find_packages(),
    py_modules=['alerta_logger'],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'syslog = alerta_logger:Syslog'
        ]
    }
)
