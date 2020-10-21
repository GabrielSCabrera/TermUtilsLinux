from distutils.core import setup

dependencies = (
    # REQUIRED PACKAGES
)

packages = ['', '<MODULE 1 NAME>', '<MODULE 2 NAME>']
for n, package in enumerate(packages):
    packages[n] = '<PACKAGE IMPORT NAME>' + package

url = '<GITHUB HYPERLINK>'
setup(
    name = '<PACKAGE NAME>',
    packages = packages,
    version = '0.0.1',
    description = '<PACKAGE DESCRIPTION>',
    author = '<NAME>',
    author_email = <'EMAIL ADDRESS'>,
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
