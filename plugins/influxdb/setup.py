
from setuptools import setup, find_packages

version = '0.3.3-combined2'

setup(
    name="alerta-influxdb",
    version=version,
    description='Alerta plugin for InfluxDB v1.1',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    packages=find_packages(),
    py_modules=['alerta_influxdb'],
    install_requires=[
        'influxdb'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'influxdb = alerta_influxdb:InfluxDBWrite'
        ]
    }
)
