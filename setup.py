# setup.py
from setuptools import setup, find_packages

setup(
    name="A1_inventory_management",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
