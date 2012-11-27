import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "iomock",
    version = "0.1",
    author = "Martin Sivak",
    author_email = "msivak@redhat.com",
    description = ("Python module which provides mock classes that "
                   "emulate file access methods in os, os.path, glob."),
    license = "GPLv2+",
    keywords = "mock testing file open os glob",
    url = "https://github.com/MarSik/python-iomock",
    packages = ['iomock'],
    setup_requires= ['nose>=1.0'],
    test_suite = "iomock",
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
    ],
)
