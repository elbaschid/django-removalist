# -*- coding: utf-8 -*-
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

requires = ['django', 'structlog']
tests_require = ['pytest', 'pytest-cache', 'pytest-cov', 'factory-boy']


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name="django-removalist",
    version='0.0.0',
    description="Simplify renaming of tables through Django Migrations'",
    long_description="\n\n".join([open("README.rst").read()]),
    license='MIT',
    author="Sebastian Vetter",
    author_email="seb@mobify.com",
    url="https://django-removalist.readthedocs.io",
    packages=find_packages(exclude=['tests']),
    install_requires=requires,
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython'],
    extras_require={'test': tests_require},
    cmdclass={'test': PyTest})
