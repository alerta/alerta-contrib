from setuptools import find_packages, setup

version = '1.0.0'

setup(
    name='alerta-jira',
    version=version,
    description='Alerta plugin for create tasks in jira',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Alexandre Azedo',
    author_email='aazedo@gocontact.pt',
    packages=find_packages(),
    py_modules=['alerta_jira'],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'jira = alerta_jira:JiraCreate'
        ]
    }
)
