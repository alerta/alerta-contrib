from setuptools import find_packages, setup

version = "0.1.0"

setup(
    name="x3me-enhance",
    version=version,
    description="Alerta plugin for alert enhancement with Netbox data",
    url="",
    license="MIT",
    author="Victor Gorchilov",
    author_email="victor.gorchilov@x3me.net",
    packages=find_packages(),
    py_modules=["alerta_x3me_enhance"],
    include_package_data=True,
    zip_safe=True,
    entry_points={"alerta.plugins": ["enhance = alerta_x3me_enhance:EnhanceAlert"]},
)
