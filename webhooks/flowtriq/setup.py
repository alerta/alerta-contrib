from setuptools import find_packages, setup

version = '1.0.0'

setup(
    name='alerta-flowtriq',
    version=version,
    description='Alerta webhook for Flowtriq DDoS detection',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Jacob Masse',
    author_email='jacob@flowtriq.com',
    packages=find_packages(),
    py_modules=['alerta_flowtriq'],
    install_requires=[],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.webhooks': [
            'flowtriq = alerta_flowtriq:FlowtriqWebhook'
        ]
    }
)
