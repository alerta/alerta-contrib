from setuptools import setup, find_packages

version = '0.0.2'

setup(
    name="alerta-routing",
    version=version,
    description='Alerta routing rules for plugins',
    url='https://github.com/demshin/alerta-contrib',
    license='Apache License 2.0',
    author='Aleksandr Demshin ',
    author_email='demshin@gmail.com',
    packages=find_packages(),
    py_modules=['routing'],
    install_requires=[],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.routing': [
            'rules = routing:rules'
        ]
    }
)