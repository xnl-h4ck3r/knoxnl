#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="knoxnl",
    packages=find_packages(),
    version="0.1",
    description="A python wrapper around the amazing KNOXSS API by Brute Logic (requires an API Key)",
    long_description=open("README.md").read(),
    author="@xnl-h4ck3r",
    url="https://github.com/xnl-h4ck3r/knoxnl",
    py_modules=["knoxnl"],
    install_requires=["argparse","requests","termcolor"],
)
