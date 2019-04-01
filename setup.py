#! -*- coding: utf-8 -*-

from __future__ import print_function
from setuptools import Extension, setup, find_packages
import tempfile
import subprocess
import shutil
import sys
import subprocess
import os
import distutils
import platform
import contextlib

try:
    from Cython.Distutils import build_ext
except ImportError:
    def build_ext(*args, **kwargs):
        from Cython.Distutils import build_ext
        return build_ext(*args, **kwargs)

@contextlib.contextmanager
def chdir(new_dir):
    old_dir = os.getcwd()
    try:
        os.chdir(new_dir)
        sys.path.insert(0, new_dir)
        yield
    finally:
        del sys.path[0]
        os.chdir(old_dir)


COMPILE_OPTIONS = ['-O3', '-Wno-strict-prototypes', '-Wno-unused-function', '-std=c++11']

LINK_OPTIONS = []

CPP_OPTIONS = []

USE_OPENMP_DEFAULT = '0' if sys.platform != 'darwin' else None
if os.environ.get('USE_OPENMP', USE_OPENMP_DEFAULT) == '1':
    COMPILE_OPTIONS.append('-fopenmp')
    LINK_OPTIONS.append('-fopenmp')
    CPP_OPTIONS.append('-fopenmp')

if sys.platform == 'darwin':
    COMPILE_OPTIONS.append('-stdlib=libc++')
    LINK_OPTIONS.append('-lc++')
    # g++ (used by unix compiler on mac) links to libstdc++ as a default lib.
    # See: https://stackoverflow.com/questions/1653047/avoid-linking-to-libstdc
    LINK_OPTIONS.append('-nodefaultlibs')


root = os.path.abspath(os.path.dirname(__file__))

cpp_sources = ['depccg.cpp',
               'cat.cpp',
               'cacheable.cpp',
               'chart.cpp',
               'combinator.cpp',
               'feat.cpp',
               'tree.cpp',
               'utils.cpp']

c_sources = ['morpha.c']

pyx_modules = ['depccg.parser',
               'depccg.tree',
               'depccg.cat',
               'depccg.combinator',
               'depccg.utils',
               'depccg.morpha']


def clean():
    depccg_dir = os.path.join(root, 'depccg')
    for name in os.listdir(depccg_dir):
        file_path = os.path.join(depccg_dir, name)
        if any(file_path.endswith(ext) for ext in ['.so', '.cpp', '.c']):
            os.unlink(file_path)
    with chdir('cpp'):
        subprocess.call(["make", "clean"], env=os.environ)


def generate_cython(root, source):
    print('Cythonizing sources')
    p = subprocess.call([sys.executable,
                         os.path.join(root, 'bin', 'cythonize.py'),
                         source], env=os.environ)
    if p != 0:
        raise RuntimeError('Running cythonize failed')


def generate_cpp(options):
    options = ' '.join(options)
    options = f'OPTIONS={options}'
    with chdir('cpp'):
        p = subprocess.call(["make", options], env=os.environ)
        if p != 0:
            raise RuntimeError('Running cythonize failed')


def numpy_includes():
    import numpy
    return numpy.get_include()

ext_modules = [
        Extension(pyx,
                  [pyx.replace('.', '/') + '.cpp'],
                  include_dirs=['.', numpy_includes(), 'cpp'],
                  extra_compile_args=COMPILE_OPTIONS,
                  extra_link_args=LINK_OPTIONS +
                  [os.path.join('cpp', cpp.replace('cpp', 'o')) for cpp in cpp_sources] +
                  [os.path.join('cpp', cpp.replace('c', 'o')) for cpp in c_sources],
                  language='c++')
        for pyx in pyx_modules]


if len(sys.argv) > 1 and sys.argv[1] == 'clean':
    clean()
else:
    generate_cpp(CPP_OPTIONS)

    generate_cython(root, 'depccg')

    setup(
        name="depccg",
        # version=__version__,  # NOQA
        description='A parser for natural language based on combinatory categorial grammar',
        author='Masashi Yoshikawa',
        author_email='yoshikawa.masashi.yh8@is.naist.jp',
        url='https://github.com/masashi-y/depccg',
        license='MIT License',
        packages=find_packages(),
        package_data={'depccg': ['models/*']},
        ext_modules=ext_modules,
        cmdclass={"build_ext": build_ext},
        scripts=['bin/depccg_en', 'bin/depccg_ja'],
        setup_requires=['Cython==0.28.3', 'numpy >=1.15, <1.16'],
        zip_safe=False,
    )
