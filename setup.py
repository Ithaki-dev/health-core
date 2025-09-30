from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in health_core/__init__.py
from health_core import __version__ as version

setup(
	name="health_core",
	version=version,
	description="Core functionality for 4Geeks Health system",
	author="4Geeks",
	author_email="health@4geeks.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)