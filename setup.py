import re

from setuptools import setup

VERSION_FILE = "quotequail/__init__.py"
with open(VERSION_FILE, encoding="utf8") as fd:
    version = re.search(r'__version__ = ([\'"])(.*?)\1', fd.read()).group(2)

with open("README.rst", encoding="utf-8") as file:
    long_description = file.read()

setup(
    name="quotequail",
    version=version,
    url="http://github.com/closeio/quotequail",
    license="MIT",
    author="Thomas Steinacher",
    author_email="engineering@close.com",
    maintainer="Thomas Steinacher",
    maintainer_email="engineering@close.com",
    description=(
        "A library that identifies quoted text in plain text and HTML email "
        "messages."
    ),
    long_description=long_description,
    packages=[
        "quotequail",
    ],
    test_suite="tests",
    tests_require=["lxml"],
    platforms="any",
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Email",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
