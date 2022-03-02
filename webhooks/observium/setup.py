from setuptools import find_packages, setup

version = "0.0.6"

setup(
    name="alerta-observium",
    version=version,
    description="Alerta webhook for Observium NMS",
    url="https://github.com/x3me/alerta-contrib",
    license="MIT",
    author="Iskren Hadzhinedev",
    author_email="iskren.hadzhinedev@x3me.net",
    packages=find_packages(),
    py_modules=["alerta_observium"],
    include_package_data=True,
    zip_safe=True,
    entry_points={"alerta.webhooks": ["observium = alerta_observium:ObserviumWebhook"]},
)
