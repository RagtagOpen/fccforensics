"""A set of Python utilities to download and analyze FCC comment data

See:
https://github.com/csinchok/fcc-analysis
"""


# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

import unittest
def unittest_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(start_dir='fcc_analysis', pattern='test_*.py')
    return test_suite


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='fcc_analysis',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see


    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.1',

    description='Analyzing FCC comments on net neutrality',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/RagtagOpen/fccforensics',

    # Author details
    author='Ragtag',
    author_email='info@ragtag.org',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    entry_points={
        'console_scripts': [
            'fcc = fcc_analysis.bin:main',
        ],
    },



    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    test_suite='setup.unittest_test_suite',

    install_requires=['requests', 'tqdm', 'elasticsearch>=5.0.0,<6.0.0', 'elasticsearch-dsl>=5.0.0,<6.0.0', 'pylint'],

)
