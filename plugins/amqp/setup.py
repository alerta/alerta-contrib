
from setuptools import setup, find_packages

version = '5.4.1'

setup(
    name="alerta-amqp",
    version=version,
    description='Alerta plugin for AMQP messaging',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    packages=find_packages(),
    py_modules=['alerta_amqp'],
    install_requires=[
        'kombu'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'amqp = alerta_amqp:FanoutPublisher'
        ]
    }
)
