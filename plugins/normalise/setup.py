
from setuptools import setup, find_packages

version = '0.1'

setup(
    name="mirantis-normalise",
    version=version,
    description='Alerta plugin for alert normalisation',
    url='https://github.com/michael-chambers/alerta-contrib',
    license='MIT',
    author='Michael Chambers',
    author_email='mchambers@mirantis.com',
    packages=find_packages(),
    install_requires=[
        'flask'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'mirantis-normalise = alerta_normalise:NormaliseAlert'
        ]
    }
)
