from setuptools import find_packages, setup

version = '5.4.0'

setup(
    name='alerta-geoip',
    version=version,
    description='Alerta plugin for GeoIP Lookup',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    packages=find_packages(),
    py_modules=['alerta_geoip'],
    install_requires=[
        'requests'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'geoip = alerta_geoip:GeoLocation'
        ]
    }
)
