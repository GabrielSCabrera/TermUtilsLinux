from distutils.core import setup

dependencies = (
    'numpy'
)

packages = ['', 'config', 'obj', 'utils']
for n, package in enumerate(packages):
    packages[n] = 'termutils' + package

url = 'https://github.com/GabrielSCabrera'
setup(
    name = 'TermUtils',
    packages = packages,
    version = '0.0.1',
    description = '<PACKAGE DESCRIPTION>',
    author = '<NAME>',
    author_email = 'EMAIL ADDRESS',
    url = url,
    download_url = url + 'archive/v0.0.1.tar.gz',
    keywords = ['<KEYWORD 1>', '<KEYWORD 2>', '<KEYWORD 3>'],
    install_requires = dependencies,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: <INTENDED AUDIENCE>',
        'Intended Audience :: <INTENDED AUDIENCE>',
        'Programming Language :: Python :: 3.8'
        'Programming Language :: Python :: 3.9'
    ],
)
