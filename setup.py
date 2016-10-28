# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


requires = [
    'six',
    'docopt',
    'requests',
    'AppDirs',
    'python-dateutil',
    'unidecode',
]


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content


setup(
    name='pycdstar',
    version="0.3.2",
    description='A python wrapper for the CDStar API',
    long_description=read("README.md"),
    author='Robert Forkel',
    author_email='forkel@shh.mpg.de',
    url='https://github.com/clld/pycdstar',
    install_requires=requires,
    license="Apache 2",
    zip_safe=False,
    keywords='',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            "cdstar = pycdstar.cli:main"
        ]
    },
    tests_require=['nose', 'coverage', 'mock==1.0', 'httmock'],
)
