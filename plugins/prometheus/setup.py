
from setuptools import setup, find_packages

version = '0.3.4'

setup(
    name="alerta-prometheus",
    version=version,
    description='Alerta plugin for Prometheus Alertmanager',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    packages=find_packages(),
    py_modules=['alerta_prometheus'],
    install_requires=[
        'requests'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'prometheus = alerta_prometheus:AlertmanagerSilence'
        ]
    }
)
