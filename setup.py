from distutils.core import setup

dependencies = (
    'numpy', 'matplotlib', 'seaborn', 'numba'
)

packages = ['', 'apps', 'config', 'obj', 'utils']
for n, package in enumerate(packages):
    packages[n] = 'termutils.' + package

url = 'https://github.com/GabrielSCabrera'
setup(
    name = 'TermUtils',
    packages = packages,
    version = '0.0.1',
    description = 'Utilities compatible with xterm-256color',
    author = 'Gabriel S. Cabrera',
    author_email = 'gabriel.sigurd.cabrera@gmail.com',
    url = url,
    download_url = url + 'archive/v0.0.1.tar.gz',
    keywords = ['terminal', 'xterm', 'gui'],
    install_requires = dependencies,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.8'
    ],
)
