from setuptools import setup, find_packages

version = '0.0.2'

setup(
    name="alerta-customtimeout",
    version=version,
    description='Alerta plugin to permit a global custom timeout to be supplied via alerta config',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Thomas Collins',
    author_email='thomaswcollins@gmail.com',
    packages=find_packages(),
    py_modules=['alerta_customtimeout'],
    install_requires=[],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'customtimeout = alerta_customtimeout:CustomTimeout'
        ]
    }
)