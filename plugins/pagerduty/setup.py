
from setuptools import setup, find_packages

version = '5.3.5'

setup(
    name="alerta-pagerduty",
    version=version,
    description='Alerta plugin for PagerDuty',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    packages=find_packages(),
    py_modules=['alerta_pagerduty'],
    install_requires=[
        'requests',
        'pdpyras'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'pagerduty = alerta_pagerduty:TriggerEvent'
        ]
    }
)
