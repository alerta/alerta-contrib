from setuptools import setup, find_packages

version = '5.0.0'

setup(
    name="alerta-msteamswebhook",
    version=version,
    description='Alerta webhook for MS Teams',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Jarno Huuskonen',
    author_email='jjh74@users.noreply.github.com',
    packages=find_packages(),
    py_modules=['alerta_msteamswebhook'],
    install_requires=[
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.webhooks': [
            'msteams = alerta_msteamswebhook:MsteamsWebhook'
        ]
    }
)
