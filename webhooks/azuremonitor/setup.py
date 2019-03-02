from setuptools import setup, find_packages

version = '5.0.1'

setup(
    name="alerta-azure-monitor",
    version=version,
    description='Alerta webhook for Azure Monitor',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Anton Delitsch',
    author_email='anton@trugen.net',
    packages=find_packages(),
    py_modules=['alerta_azuremonitor'],
    install_requires=[
        'python-dateutil'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.webhooks': [
            'azuremonitor = alerta_azuremonitor:AzureMonitorWebhook'
        ]
    }
)
