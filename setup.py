# -*- coding: utf-8 -*-
import pathlib
from setuptools import find_packages, setup
from configparser import ConfigParser

cfg = ConfigParser()
cfg.read(filenames=['setup.cfg'])
VERSION = cfg.get('metadata', 'version')
PACKAGE_NAME = cfg.get('metadata', 'name')
PYTHON_REQUIRES = cfg.get('options', 'python_requires')

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text(encoding='utf8')

# Add future dependencies here
DEPENDENCIES = ["pathlib"]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author="Yurii Cherkasov",
    author_email="strategarius@protonmail.com",
    description="Provides functionality of generating source code programmatically",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/yuchdev/code_generator",
    project_urls={
        "Bug Tracker": "https://github.com/yuchdev/code_generator/issues",
    },
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate you support Python 3. These classifiers are *not*
        # checked by 'pip install'. See instead 'python_requires' below.
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(where=str(HERE / 'src')),
    package_dir={'': 'src'},
    package_data={PACKAGE_NAME: ['defaults/*']},
    python_requires=PYTHON_REQUIRES,
    include_package_data=True,
    install_requires=DEPENDENCIES,
)
