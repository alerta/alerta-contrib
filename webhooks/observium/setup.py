from setuptools import setup, find_packages

version = '0.0.5'

setup(
    name="alerta-observium",
    version=version,
    description='Alerta webhook for Obseervium NMS',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Iskren Hadzhinedev',
    author_email='iskren.hadzhinedev@x3me.net',
    packages=find_packages(),
    py_modules=['alerta_observium'],
    install_requires=[
        'python-dateutil'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.webhooks': [
            'observium = alerta_observium:ObserviumWebhook'
        ]
    }
)
