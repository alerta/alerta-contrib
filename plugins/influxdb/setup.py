
from setuptools import setup, find_packages

version = '5.4.2'

setup(
    name="alerta-influxdb",
    version=version,
    description='Alerta plugin for InfluxDB',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    packages=find_packages(),
    py_modules=['alerta_influxdb'],
    install_requires=[
        'influxdb>=5.0.0'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'influxdb = alerta_influxdb:InfluxDBWrite'
        ]
    }
)
