from setuptools import setup, find_packages

version = "0.1.0"

setup(
    name="alerta-matrix",
    version=version,
    description="Alerta plugin for Matrix",
    url="https://github.com/alerta/alerta-contrib",
    license="MIT",
    author="Magnus Walbeck",
    author_email="mw@mwalbeck.org",
    packages=find_packages(),
    py_modules=["alerta_matrix"],
    install_requires=["requests"],
    include_package_data=True,
    zip_safe=True,
    entry_points={"alerta.plugins": ["matrix = alerta_matrix:SendMessage"]},
)
