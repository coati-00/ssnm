from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

setup(
    name="ecomap",
    version="0.5",
    description="ecomaps!",
    author="Kurt Eldridge",
    author_email="kfe2102@columbia.edu",
    url="http://www.ccnmtl.columbia.edu/",
    install_requires = ["TurboGears >= 0.8a5"],
    scripts = ["ecomap_start.py"],
    zip_safe=False,
    packages=find_packages(),
    package_data = find_package_data(where='ecomap',
                                     package='ecomap'),
    )
    
