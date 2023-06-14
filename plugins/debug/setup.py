from setuptools import find_packages, setup

version = '7.0.0'

setup(
    name='alerta-debug',
    version=version,
    description='Alerta plugin for debug & tracing',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='nick.satterly@gmail.com',
    packages=find_packages(),
    py_modules=['alerta_debug'],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'debug = alerta_debug:DebugTracing'
        ]
    },
    python_requires='>=3.5'
)
