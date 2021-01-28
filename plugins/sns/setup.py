
from setuptools import setup, find_packages

version = '6.0.0'

setup(
    name="alerta-sns",
    version=version,
    description='Alerta plugin for AWS SNS (with Fifo)',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='nick.satterly@gmail.com',
    packages=find_packages(),
    py_modules=['alerta_sns'],
    install_requires=[
        'boto3'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'sns = alerta_sns:SnsTopicPublisher'
        ]
    }
)
