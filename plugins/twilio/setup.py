
from setuptools import setup, find_packages

version = '5.4.0'

setup(
    name="alerta-twilio",
    version=version,
    description='Alerta plugin for Twilio SMS',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    packages=find_packages(),
    py_modules=['alerta_twilio_sms'],
    install_requires=[
        'twilio>=6.0.0'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'twilio_sms = alerta_twilio_sms:SendSMSMessage'
        ]
    }
)
