from setuptools import find_packages, setup

version = "0.1.5"

setup(
    name="alerta-netbox",
    version=version,
    description="Alerta plugin for alert enhancement with Netbox data",
    url="https://github.com/x3me/alerta-contrib",
    license="MIT",
    author="Victor Gorchilov",
    author_email="victor.gorchilov@x3me.net",
    packages=find_packages(),
    py_modules=["alerta_netbox"],
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        "cachetools",
    ],
    entry_points={"alerta.plugins": ["netbox = alerta_netbox:NetboxEnhance"]},
)
