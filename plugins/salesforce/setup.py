
from setuptools import setup, find_packages

version = '0.1'

setup(
    name="alerta-salesforce",
    version=version,
    description='Alerta plugin for SalesForce',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Michael Chambers',
    author_email='mchambers@mirantis.com',
    packages=find_packages(),
    py_modules=['alerta_salesforce'],
    install_requires=[
        'simple-salesforce',
        'cachetools'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'salesforce = alerta_salesforce:OpenCase'
        ]
    }
)