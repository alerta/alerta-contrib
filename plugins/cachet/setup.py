
from setuptools import setup, find_packages

version = '5.0.1'

setup(
    name="alerta-cachet",
    version=version,
    description='Alerta plugin for Cachet status page',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    packages=find_packages(),
    py_modules=['alerta_cachet'],
    install_requires=[
        'python-cachetclient'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'cachet = alerta_cachet:CachetIncident'
        ]
    }
)
