"""Setup script for pycddlib."""

# pycddlib is a Python wrapper for Komei Fukuda's cddlib
# Copyright (c) 2008, Matthias Troffaes
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

classifiers = """\
Development Status :: 4 - Beta
License :: OSI Approved :: GNU General Public License (GPL)
Intended Audience :: Science/Research
Topic :: Scientific/Engineering :: Mathematics
Programming Language :: C
Programming Language :: Cython
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 3
Operating System :: OS Independent"""

import sys
import os.path

# at the moment, cython and setuptools don't work well together, so
# only one of these should be True
USE_CYTHON = not os.path.exists('cdd.c')
USE_SETUPTOOLS = not USE_CYTHON
USE_MPIR = (sys.platform == 'win32') # mpir or gmp?
GET_GMP = os.environ.get('READTHEDOCS', None) == 'True' # download gmp?

if USE_SETUPTOOLS:
    from setuptools import setup
    from setuptools.extension import Extension
else:
    from distutils.core import setup
    from distutils.extension import Extension

if USE_CYTHON:
    from Cython.Distutils import build_ext
    cmdclass = {'build_ext': build_ext}
else:
    cmdclass = {}

define_macros = [('GMPRATIONAL', None)]
libraries = []
if not GET_GMP:
    if USE_MPIR:
        define_macros += [('MPIR', None)]
        libraries += ['mpir']
    else:
        libraries += ['gmp']

# get version from Cython file (without requiring extensions to be compiled!)
for line in open('cdd.pyx'):
    if line.startswith("__version__"):
       version = line[line.find('"')+1:line.rfind('"')]
       break
else:
    raise RuntimeError("failed to extract version from cdd.pyx")

# get documentation from README.rst file
doclines = open('README.rst').read().split('\n')

cdd_dir = 'cddlib/lib-src'
cdd_sources = [
    '{0}/{1}'.format(cdd_dir, srcfile) for srcfile in [
        'cddcore.c',
        'cddio.c',
        'cddlib.c',
        'cddlp.c',
        'cddmp.c',
        'cddproj.c',
        'setoper.c',
        ]
    ]
cdd_headers = [
    '{0}/{1}'.format(cdd_dir, hdrfile) for hdrfile in [
        'cdd.h',
        'cddmp.h',
        'cddtypes.h',
        'setoper.h',
        ]
    ]

cddgmp_dir = 'cddlib/lib-src-gmp'
cddgmp_sources = cdd_sources + [
    '{0}/{1}'.format(cddgmp_dir, srcfile) for srcfile in [
        'cddcore_f.c',
        'cddio_f.c',
        'cddlib_f.c',
        'cddlp_f.c',
        'cddmp_f.c',
        'cddproj_f.c',
        ]
    ]
cddgmp_headers = cdd_headers + [
    '{0}/{1}'.format(cddgmp_dir, hdrfile) for hdrfile in [
        'cdd_f.h',
        'cddmp_f.h',
        'cddtypes_f.h',
        ]
    ]

include_dirs = [cdd_dir, cddgmp_dir]
if GET_GMP:
    import subprocess
    GMP_DIR = 'gmp-5.0.5'
    if not os.path.exists(GMP_DIR + ".tar.bz2"):
        import urllib
        urllib.urlretrieve(
            "ftp://ftp.gmplib.org/pub/{0}/{0}.tar.bz2".format(GMP_DIR),
            GMP_DIR + ".tar.bz2")
    if not os.path.exists(GMP_DIR):
        import tarfile
        f = tarfile.open(GMP_DIR + ".tar.bz2", "r:bz2")
        try:
            f.extractall()
        finally:
            f.close()
    if not os.path.exists(GMP_DIR + "/gmp.h"):
        process = subprocess.Popen(
            ["./configure", "--disable-shared"], cwd=GMP_DIR)
        process.wait()
    if not os.path.exists(GMP_DIR + "/.libs/libgmp.a"):
        process = subprocess.Popen(["make"], cwd=GMP_DIR)
        process.wait()
    include_dirs += [GMP_DIR]
    library_dirs=[GMP_DIR + "/.libs/"],

# generate include files from template
cddlib_pxi_in = open("cddlib.pxi.in", "r").read()
cddlib_pxi = open("cddlib.pxi", "w")
cddlib_pxi.write(
    cddlib_pxi_in
    .replace("@cddhdr@", "cdd.h")
    .replace("@dd@", "dd")
    .replace("@mytype@", "mytype"))
cddlib_pxi.close()
cddlib_f_pxi = open("cddlib_f.pxi", "w")
cddlib_f_pxi.write(
    cddlib_pxi_in
    .replace("@cddhdr@", "cdd_f.h")
    .replace("@dd@", "ddf")
    .replace("@mytype@", "myfloat"))
cddlib_f_pxi.close()

setup(
    name = "pycddlib",
    version = version,
    ext_modules= [
        Extension("cdd",
                  ["cdd.pyx" if USE_CYTHON else "cdd.c"] + cddgmp_sources,
                  include_dirs=include_dirs,
                  depends=cddgmp_headers,
                  define_macros=define_macros,
                  libraries=libraries,
                  ),
        ],
    author = "Matthias Troffaes",
    author_email = "matthias.troffaes@gmail.com",
    license = "GPL",
    keywords = "convex, polyhedron, linear programming, double description method",
    platforms = "any",
    description = doclines[0],
    long_description = "\n".join(doclines[2:]),
    url = "http://pypi.python.org/pypi/pycddlib",
    classifiers = classifiers.split('\n'),
    cmdclass = cmdclass,
)
