from setuptools import setup, find_packages

version = '1.0.0'

setup(
    name="alerta-query",
    version=version,
    description='Alerta Generic Webhook by query parameters',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Pablo Villaverde',
    author_email='pvillaverdecastro@gmail.com',
    packages=find_packages(),
    py_modules=['alerta_query'],
    install_requires=[],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.webhooks': [
            'query = alerta_query:QueryWebhook'
        ]
    }
)

