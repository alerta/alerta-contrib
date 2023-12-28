from setuptools import setup, find_packages

version = '1.0.0'

setup(
    name="alerta-ip2locationio",
    version=version,
    description='Alerta plugin to query geolocation information from IP2Location.io API.',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='IP2Location',
    author_email='support@ip2location.com',
    py_modules=['alerta_ip2locationio'],
    packages=find_packages(),
    install_requires=[
        'requests'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'ip2locationio = alerta_ip2locationio:IP2Locationio'
        ]
    }
)
