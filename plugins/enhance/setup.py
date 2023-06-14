from setuptools import find_packages, setup

version = '5.3.3'

setup(
    name='alerta-enhance',
    version=version,
    description='Alerta plugin for alert enhancement',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    packages=find_packages(),
    py_modules=['alerta_enhance'],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'enhance = alerta_enhance:EnhanceAlert'
        ]
    }
)
