# import multiprocessing to avoid this bug (http://bugs.python.org/issue15881#msg170215)
import multiprocessing
assert multiprocessing
import re
from setuptools import setup, find_packages


def get_version():
    """
    Extracts the version number from the version.py file.
    """
    VERSION_FILE = 'dynamic_db_router/version.py'
    mo = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', open(VERSION_FILE, 'rt').read(), re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError('Unable to find version string in {0}.'.format(VERSION_FILE))


def get_requirements(path):
    with open(path, 'r') as requirements_file:
        return requirements_file.read().split('\n')


setup(
    name='django-dynamic-db-router',
    version=get_version(),
    description='Simply route complex django queries to multiple databases.',
    long_description=open('README.rst').read(),
    url='https://github.com/ambitioninc/django-dynamic-db-router',
    author='Erik Swanson',
    author_email='opensource@ambition.com',
    keywords='',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    license='MIT',
    install_requires=get_requirements('requirements/setup.txt'),
    tests_require=get_requirements('requirements/test.txt'),
    include_package_data=True,
    test_suite='run_tests.run_tests',
    zip_safe=False,
)
