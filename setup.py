import os
import setuptools

from lager_cli import __version__ as lager_version

def readme():
    path = os.path.dirname(__file__)
    with open(os.path.join(path, 'README.md')) as f:
        return f.read()

name = 'lager-fixture'
description = 'Lager Test Fixture Wrapper'
author = 'Lager Data LLC'
email = 'hello@lagerdata.com'
classifiers = [
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Topic :: Software Development',
]

if __name__ == "__main__":
    setuptools.setup(
        name=name,
        version=lager_version,
        description=description,
        long_description=readme(),
        classifiers=classifiers,
        url='https://github.com/lagerdata/lager_fixture',
        author=author,
        author_email=email,
        maintainer=author,
        maintainer_email=email,
        license='AGPLv3',
        python_requires=">=3.6",
        packages=setuptools.find_packages(),
        install_requires='''
            pyserial==3.4
        ''',
        entry_points={
            'console_scripts': [
            ],
        }
    )