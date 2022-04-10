from setuptools import setup, find_packages

version = '1.0.0'

setup(
    name="alerta-falco",
    version=version,
    description='Alerta Webhook for Falco',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Puppet Security Team',
    author_email='security@puppet.com',
    packages=find_packages(),
    py_modules=['alerta_falco'],
    install_requires=[],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.webhooks': [
            'falco = alerta_falco:FalcoWebhook'
        ]
    }
)

