from setuptools import setup, find_packages

version = '5.0.0'

setup(
    name="alerta-sentry",
    version=version,
    description='Alerta webhook for Sentry',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='nick.satterly@gmail.com',
    packages=find_packages(),
    py_modules=['alerta_sentry'],
    install_requires=[
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.webhooks': [
            'sentry = alerta_sentry:SentryWebhook'
        ]
    }
)
