from setuptools import find_packages, setup

version = '0.1.1'

setup(
    name='alerta-zammad',
    version=version,
    description='Alerta plugin for Zammad',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Jonas Reindl',
    author_email='jreindl@mgit.at',
    packages=find_packages(),
    py_modules=['alerta_zammad'],
    install_requires=[
        'requests'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'zammad = alerta_zammad:ZammadTicket'
        ]
    }
)
