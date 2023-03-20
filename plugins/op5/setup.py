from setuptools import find_packages, setup

version = '5.0.2'

setup(
    name='alerta-op5',
    version=version,
    description='Alerta plugin for OP5 Monitor',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Anton Delitsch',
    author_email='anton@trugen.net',
    packages=find_packages(),
    py_modules=['alerta_op5'],
    install_requires=[
        'op5lib==1.0'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'op5 = alerta_op5:OP5Acknowledge'
        ]
    }
)
