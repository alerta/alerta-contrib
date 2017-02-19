
from setuptools import setup, find_packages

version = '0.3.2'

setup(
    name="alerta-hipchat",
    version=version,
    description='Alerta plugin for HipChat',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    packages=find_packages(),
    py_modules=['alerta_hipchat'],
    install_requires=[
        'requests',
        'jinja2'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'hipchat = alerta_hipchat:SendRoomNotification'
        ]
    }
)
