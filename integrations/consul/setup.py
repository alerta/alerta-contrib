
from setuptools import setup, find_packages

version = '1.1.0'

setup(
    name="alerta-consul",
    version=version,
    description='Send emails from Alerta',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Marco Supino',
    author_email='marco@supino.org',
    py_modules=['consulalerta','consulheartbeat'],
    install_requires=[
        'alerta',
        'python-consul'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'consul-alerta = consulalerta:main',
            'consul-heartbeat = consulheartbeat:main'
        ]
    },
    keywords="alerta monitoring consul",
    classifiers=[
        'Topic :: System :: Monitoring',
    ]
)
