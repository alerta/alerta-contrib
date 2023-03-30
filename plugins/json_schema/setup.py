
from setuptools import setup, find_packages

version = '0.2.0'

setup(
    name="alerta-json_schema-plugin",
    version=version,
    description='Example Alerta plugin for testing',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    packages=find_packages(),
    py_modules=['alerta_json_schema'],
    install_requires=['jsonschema','jsonpickle'],
    package_data={},
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'json_schema = alerta_json_schema:AlertaJsonSchema'
        ]
    }
)

