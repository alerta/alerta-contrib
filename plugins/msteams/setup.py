
from setuptools import setup, find_packages

version = '5.0.1'

setup(
    name="alerta-msteams",
    version=version,
    description='Alerta plugin for Microsoft Teams',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Anton Delitsch',
    author_email='anton@trugen.net',
    packages=find_packages(),
    py_modules=['alerta_msteams'],
    install_requires=[
        'pymsteams',
        'jinja2'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'msteams = alerta_msteams:SendConnectorCardMessage'
        ]
    }
)
