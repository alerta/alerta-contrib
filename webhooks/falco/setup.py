from setuptools import find_packages, setup

version = '0.0.3'

setup(
    name='alerta-falco',
    version=version,
    description='Alerta webhook for Falco',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Juan Kungfoo @ binbash',
    author_email='juan.delacamara@binbash.com.ar',
    packages=find_packages(),
    py_modules=['alerta_falco'],
    install_requires=[
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.webhooks': [
            'falco = alerta_falco:FalcoWebhook'
        ]
    }
)
