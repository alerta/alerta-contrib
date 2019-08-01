from setuptools import setup, find_packages

version = '1.0.0'

setup(
    name="alerta-fail2ban",
    version=version,
    description='Alerta Webhook for Fail2Ban',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Milos Buncic',
    author_email='milosbuncic@gmail.com',
    packages=find_packages(),
    py_modules=['alerta_fail2ban'],
    install_requires=[],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.webhooks': [
            'fail2ban = alerta_fail2ban:Fail2BanWebhook'
        ]
    }
)
