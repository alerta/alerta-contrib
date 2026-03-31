from setuptools import setup

version = '1.1.1'

setup(
    name='alerta-consul',
    version=version,
    description='Alerta integration for Consul health checks',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Marco Supino',
    author_email='marco@supino.org',
    py_modules=['consul_alerta', 'consul_heartbeat'],
    install_requires=[
        'alerta',
        'python-consul'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'consul-alerta = consul_alerta:main',
            'consul-heartbeat = consul_heartbeat:main'
        ]
    },
    keywords='alerta monitoring consul',
    classifiers=[
        'Topic :: System :: Monitoring',
    ]
)
