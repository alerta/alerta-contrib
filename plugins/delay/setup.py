from setuptools import setup, find_packages

version = '1.0.0'

setup(
    name="alerta-delay",
    version=version,
    description='Alerta plugin for delay (autoshelve) to prevent notifications within a set timout.',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Terje Solend Nomeland, Are Schjetne, Øystein Middelthun',
    author_email='tjnome@gmail.com, sixcare.as@gmail.com, oystein@middelthun.no',
    packages=find_packages(),
    py_modules=['alerta_delay'],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'delay = alerta_delay:DelayHandler'
        ]
    }
)