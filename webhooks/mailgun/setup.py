from setuptools import find_packages, setup

version = '5.0.0'

setup(
    name='alerta-mailgun',
    version=version,
    description='Alerta webhook for Mailgun',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Anton Delitsch',
    author_email='anton@trugen.net',
    packages=find_packages(),
    py_modules=['alerta_mailgun'],
    install_requires=[
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.webhooks': [
            'mailgun = alerta_mailgun:MailgunWebhook'
        ]
    }
)
