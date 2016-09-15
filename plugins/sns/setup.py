
from setuptools import setup, find_packages

version = '0.3.1'

setup(
    name="alerta-sns",
    version=version,
    description='Alerta plugin for AWS SNS',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    packages=find_packages(),
    py_modules=['alerta_sns'],
    install_requires=[
        'boto'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'sns = alerta_sns:SnsTopicPublisher'
        ]
    }
)
