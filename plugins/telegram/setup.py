
from setuptools import setup, find_packages

version = '0.0.3'

setup(
    name="alerta-telegram",
    version=version,
    description='Alerta plugin for Telegram',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    packages=find_packages(),
    py_modules=['alerta_telegram'],
    install_requires=[
        'telepot'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'telegram = alerta_telegram:TelegramBot'
        ]
    }
)
