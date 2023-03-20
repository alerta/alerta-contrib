from setuptools import find_packages, setup

version = '5.3.2'

setup(
    name='alerta-logger',
    version=version,
    description='Alerta plugin for syslog logging',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    packages=find_packages(),
    py_modules=['alerta_logger'],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'syslog = alerta_logger:Syslog'
        ]
    }
)
