from setuptools import setup, find_packages

version = '0.0.1'

setup(
    name="alerta-atlas",
    version=version,
    description='Alerta webhook for mongodb atlas',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Matthieu Serrepuy',
    author_email='matthieu@serrepuy.fr',
    packages=find_packages(),
    py_modules=['alerta_atlas'],
    install_requires=[],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.webhooks': [
          'atlas = alerta_atlas:MongodbAtlasWebhook'
        ]
    }
)
