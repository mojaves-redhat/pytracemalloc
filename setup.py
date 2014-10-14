#!/usr/bin/env python

# Todo list to prepare a release:
#  - git pull --rebase
#  - downloaded latest Python 2.7 and 3.3 releases, patch them, install them
#  - run unit tests with Python 2.7 and 3.3
#  - update VERSION in _tracemalloc.c and setup.py
#  - reset option in setup.py: DEBUG=False
#  - set release date in the doc/changelog.rst file
#  - git commit -a
#  - git tag -a pytracemalloc-VERSION
#  - git push
#  - git push --tags
#  - python setup.py register sdist upload
#
# After the release:
#  - set version to n+1
#  - git commit
#  - git push

from __future__ import with_statement
from distutils.core import setup, Extension
import ctypes
import os
import subprocess
import sys

# Debug pytracemalloc
DEBUG = False

VERSION = '1.2'

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: C',
    'Programming Language :: Python',
    'Topic :: Security',
    'Topic :: Software Development :: Debuggers',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

def main():
    if sys.version_info >= (3, 4):
        print("tracemalloc is now part of Python 3.4!")
        print("Third party pytracemalloc module is no more needed.")
        sys.exit(1)

    pythonapi = ctypes.cdll.LoadLibrary(None)
    if not hasattr(pythonapi, 'PyMem_SetAllocator'):
        print("WARNING: PyMem_SetAllocator: missing, %s has not been patched" % sys.executable)
    else:
        print("PyMem_SetAllocator: present")

    cflags = []
    if not DEBUG:
        cflags.append('-DNDEBUG')

    with open('README.rst') as f:
        long_description = f.read().strip()

    ext = Extension(
        '_tracemalloc',
        ['_tracemalloc.c', 'hashtable.c'],
        extra_compile_args = cflags)

    options = {
        'name': 'pytracemalloc',
        'version': VERSION,
        'license': 'MIT license',
        'description': 'Track memory allocations per Python file',
        'long_description': long_description,
        "url": "http://pytracemalloc.readthedocs.org/",
        'download_url': 'https://github.com/haypo/pytracemalloc',
        'author': 'Victor Stinner',
        'author_email': 'victor.stinner@gmail.com',
        'ext_modules': [ext],
        'classifiers': CLASSIFIERS,
        'py_modules': ["tracemalloc"],
    }
    setup(**options)

if __name__ == "__main__":
    main()

