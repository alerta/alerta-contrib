from setuptools import setup, find_packages

version = "0.0.1"

setup(
    name="alerta-graylog",
    version=version,
    description="Alerta webhook for Graylog",
    url="https://github.com/alerta/alerta-contrib",
    license="MIT",
    author="Nikolay Chobanov",
    author_email="nikolay.chobanov@x3me.net",
    packages=find_packages(),
    py_modules=["alerta_graylog"],
    install_requires=["python-dateutil"],
    include_package_data=True,
    zip_safe=True,
    entry_points={"alerta.webhooks": ["graylog = alerta_graylog:GraylogWebhook"]},
)
