"""Briefy Common."""
from setuptools import find_packages
from setuptools import setup

import os


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'HISTORY.rst')) as f:
    CHANGES = f.read()

requires = [
    'babel',
    'boto3',
    'colander',
    'colanderalchemy',
    'flask_babel',
    'graphviz',
    'libthumbor',
    'newrelic',
    'phonenumbers',
    'prettyconf',
    'pyCrypto',
    'python-logstash',
    'python-slugify',
    'pytz',
    'requests',
    'setuptools',
    'wheel',
    'zope.component',
    'zope.configuration',
    'zope.event',
    'zope.interface',
]

requires_db = [
    'alembic',
    'dogpile.cache',
    'geoalchemy2',
    'redis',
    'psycopg2',
    'sqlalchemy',
    'sqlalchemy-utils',
    'zope.sqlalchemy',
]

test_requirements = [
    'flake8',
    'pytest'
]

setup(
    name='briefy.common',
    version='2.0.1',
    description='Common utilities to be used by Briefy packages.',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Programming Language :: Python',
    ],
    author='Briefy Tech Team',
    author_email='developers@briefy.co',
    url='https://github.com/BriefyHQ/briefy-common',
    keywords='broker queue',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['briefy', ],
    include_package_data=True,
    zip_safe=False,
    test_suite='tests',
    tests_require=test_requirements,
    install_requires=requires,
    extras_require={'db': requires_db},
    entry_points="""""",
)
