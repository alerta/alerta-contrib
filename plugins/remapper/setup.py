from setuptools import find_packages, setup

version = '1.0.0'

setup(
    name='alerta-remapper',
    version=version,
    description='Alerta plugin for alert fields remapping',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='OJ',
    author_email='diego.ojeda@binbash.com.ar',
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
