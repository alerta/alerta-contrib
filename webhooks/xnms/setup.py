from setuptools import find_packages, setup

version = "0.0.1"

setup(
    name="alerta-xnms",
    version=version,
    description="Alerta webhook for xNMS",
    url="https://github.com/x3me/alerta-contrib",
    license="MIT",
    author="Iskren Hadzhinedev",
    author_email="iskren.hadzhinedev@x3me.net",
    packages=find_packages(),
    py_modules=["alerta_xnms"],
    include_package_data=True,
    zip_safe=True,
    entry_points={"alerta.webhooks": ["xnms = alerta_xnms:XnmsWebhook"]},
)
