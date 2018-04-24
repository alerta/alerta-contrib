
from setuptools import setup, find_packages

version = '5.3.3'

setup(
    name="alerta-forward",
    version=version,
    description='Alerta plugin for forwarding alerts',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='SKob',
    author_email='skob@me.com',
    packages=find_packages(),
    py_modules=['alerta_forward'],
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'alerta'
    ],
    entry_points={
        'alerta.plugins': [
            'forward = alerta_forward:ForwardAlert'
        ]
    }
)
