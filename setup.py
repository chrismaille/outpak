"""Setup.py."""
import datetime
from codecs import open as copen
from os import path
from setuptools import setup, find_packages
from outpak import __version__


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with copen(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

install_requires = [
    "buzio",
    "docopt",
    "PyYAML"
]

if 'dev' in __version__:
    now = datetime.datetime.now()
    release_number = (now - datetime.datetime(2018, 1, 24)
                      ).total_seconds() / 60
    version = "{}{}".format(__version__, int(release_number))
else:
    version = __version__

setup(
    name='outpak',
    version=version,
    description='Install git+protocol packages in '
    'requirements.txt without SSH keys',
    long_description=long_description,
    author='Chris Maillefaud',
    include_package_data=True,
    # Choose your license
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: User Interfaces',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    keywords='pip install git personal token',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'pak=outpak.cmd:start'
        ],
    },
)
