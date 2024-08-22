from setuptools import find_packages, setup

version = '1.0.0'

setup(
    name='alerta-remapper',
    version=version,
    description='Alerta plugin for alert enhancement',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='OJ',
    author_email='oj@example.com',
    packages=find_packages(),
    py_modules=['alerta_remapper'],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'remapper = alerta_remapper:RemapAlert'
        ]
    }
)
