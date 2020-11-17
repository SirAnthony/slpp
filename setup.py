#!/usr/bin/env python
from setuptools import setup
from os import path

cur_dir = path.abspath(path.dirname(__file__))
with open(path.join(cur_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='SLPP',
    description='SLPP is a simple lua-python data structures parser',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='1.2.2',
    author='SirAnthony',
    url='https://github.com/SirAnthony/slpp',
    license='MIT',
    keywords=['lua'],
    py_modules=['slpp'],
    install_requires=['six'],
)
