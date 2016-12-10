
from setuptools import setup, find_packages

version = '1.0.0'

setup(
    name="alerta-consul",
    version=version,
    description='Send emails from Alerta',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Marco Supino',
    author_email='marco@supino.org',
    py_modules=['consul-alerta','consul-heartbeat'],
    install_requires=[
        'alerta',
        'python-consul'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'consul-alerta = consul-alerta:main',
            'consul-heartbeat = consul-heartbeat:main',
        ]
    },
    keywords="alerta monitoring consul",
    classifiers=[
        'Topic :: System :: Monitoring',
    ]
)
