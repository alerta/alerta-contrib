
from setuptools import setup, find_packages

version = '5.0.0'

setup(
    name="alerta-rocketchat",
    version=version,
    description='Alerta plugin for Rocket.Chat',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='nick.satterly@gmail.com',
    py_modules=['alerta_rocketchat'],
    install_requires=[
        'requests'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'rocketchat = alerta_rocketchat:PostMessage'
        ]
    }
)
