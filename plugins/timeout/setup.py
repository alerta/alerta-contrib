from setuptools import find_packages, setup

version = '4.0.3'

setup(
    name='alerta-timeout',
    version=version,
    description='Alerta plugin to permit a global custom timeout to be supplied via alerta config',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Thomas Collins',
    author_email='thomaswcollins@gmail.com',
    packages=find_packages(),
    py_modules=['alerta_timeout'],
    install_requires=[],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'timeout = alerta_timeout:Timeout'
        ]
    }
)
