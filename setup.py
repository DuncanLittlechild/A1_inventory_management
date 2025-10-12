# setup.py
from setuptools import setup, find_packages

setup(
    name="A1-inventory-management",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
