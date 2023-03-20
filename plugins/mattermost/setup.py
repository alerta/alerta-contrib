from setuptools import find_packages, setup

version = '1.1.3'

setup(
    name='alerta-mattermost',
    version=version,
    description='Alerta plugin for Mattermost',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Dmitrii Sitnikov (WWHW)',
    author_email='no-reply@wwhw.org',
    packages=find_packages(),
    py_modules=['alerta_mattermost'],
    install_requires=[
        'matterhook',
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'mattermost = alerta_mattermost:ServiceIntegration'
        ]
    }
)
