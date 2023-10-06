from setuptools import setup, find_packages

version = '0.0.1'

setup(
    name="alerta-gcp",
    version=version,
    description='Alerta webhook for GCP',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Matthieu Serrepuy',
    author_email='matthieu@serrepuy.fr',
    packages=find_packages(),
    py_modules=['alerta_gcp'],
    install_requires=[],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.webhooks': [
          'gcp = alerta_gcp:GoogleCloudPlatformWebhook'
        ]
    }
)
