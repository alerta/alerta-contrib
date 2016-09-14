
from setuptools import setup, find_packages

version = '0.3.0'

setup(
    name="alerta-normalise",
    version=version,
    description='Alerta plugin for alert normalisation',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    packages=find_packages(),
    py_modules=['alerta_normalise'],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'normalise = alerta_normalise:NormaliseAlert'
        ]
    }
)
