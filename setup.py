from setuptools import setup, find_packages

setup(
    name='sly-string-toolkit',
    version='1.2.0',
    packages=find_packages(),
    install_requires=[
        'keystone-engine',
        'watchdog'
    ],
)
