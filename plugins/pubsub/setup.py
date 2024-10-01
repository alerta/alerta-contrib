from setuptools import find_packages, setup

version = '5.2.2'

setup(
    name='alerta-pubsub',
    version=version,
    description='Alerta plugin for sending alerts to pubsub',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Arindam Choudhury',
    author_email='arindam@live.com',
    packages=find_packages(),
    py_modules=['alerta_pubsub'],
    install_requires=[
        'google-cloud-pubsub',
        'oauth2client',
        'grpcio==1.53.0'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'pubsub = alerta_pubsub:SendToPubsub'
        ]
    }
)
