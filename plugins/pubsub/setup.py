
from setuptools import setup, find_packages

version = '5.2.1'

setup(
    name="alerta-pubsub",
    version=version,
    description='Alerta plugin for sending alerts to pubsub',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Arindam Choudhury',
    author_email='arindam@live.com',
    packages=find_packages(),
    py_modules=['alerta_pubsub'],
    install_requires=[
        'google-cloud',
        'oauth2client'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'pubsub = alerta_pubsub:SendToPubsub'
        ]
    }
)
