from setuptools import setup, find_packages

version = '0.0.1'

setup(
    name="alerta-statuscake",
    version=version,
    description='Alerta webhook for statuscake',
    url='https://github.com/alerta/alerta-contrib',
    license='Apache License 2.0',
    author='Matthieu Serrepuy',
    author_email='matthieu@serrepuy.fr',
    packages=find_packages(),
    py_modules=['alerta_statuscake'],
    install_requires=[],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.webhooks': [
          'statuscake = alerta_statuscake:StatusCakeWebhook'
        ]
    }
)
