
from setuptools import setup, find_packages

version = '5.3.1'

setup(
    name="alerta-logstash",
    version=version,
    description='Alerta plugin for ELK logstash',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    packages=find_packages(),
    py_modules=['alerta_logstash'],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'logstash = alerta_logstash:LogStashOutput'
        ]
    }
)
