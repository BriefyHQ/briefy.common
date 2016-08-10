.. highlight:: shell

Getting Started
===============

Prerequisites
-------------

* Git
* Python 3.5


Get the code
------------
Given you have privileges to access the codebase on GitHub, execute the following command on
a shell prompt::

  $ git clone git@github.com:BriefyHQ/briefy.common.git

Local Install
-------------
Access the directory containing *briefy.common* codebase::

  $ cd briefy.common

Create a virtual environment::

  $ python3 -m venv .

Install package & dependencies
++++++++++++++++++++++++++++++

For development::


    $ ./bin/pip install -r requirements/dev.txt


For staging / production::

    $ ./bin/pip install -r requirements.txt


Running tests
-------------

To run all tests, first, it is needed to setup a mock server for AWS SQS::

    $ docker run -d -p 127.0.0.1:5000:5000 --name sqs briefy/aws-test:latest sqs
    $ export SQS_IP=127.0.0.1 SQS_PORT=5000

Run all tests::

    $ ./bin/tox


Check style::

    $ ./bin/flake8 src/briefy/common tests setup.py

To run just a subset of the tests::

    $ ./bin/py.test tests/queue


Reporting Bugs
--------------

Report bugs at https://github.com/BriefyHQ/briefy.common/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Generating the documentation
----------------------------

Install this package and its dependencies::

    $ ./bin/pip install -r requirements/dev.txt


Generate the HTML documentation::

    $ make server

Open the your browser at http://localhost:8000
