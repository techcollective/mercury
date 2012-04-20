=======
Mercury
=======

Mercury is a simple invoicing system. It is being developed by TechCollective_,
a worker owned and operated cooperative in San Francisco, CA.

.. _TechCollective: http://www.techcollective.com

Introduction
============

After using a paid online invoicing service, we felt the need to switch to an
open source alternative. Unsatisfied with all the options we evaluated, one of
our developers wondered: "How difficult would it be to hack up a quick solution
using excellent Django_'s excelling `admin interface`_?"

The answer turned out to be: "Quite hard". We've been using the result for all
our invoicing needs since mid-2010.

.. _Django: http://www.djangoproject.com
.. _admin interface: http://docs.djangoproject.com/en/1.4/ref/contrib/admin/


Features
========

* Simple and fast
* Convenient auto-completion of customer and product/service names when
  creating an invoice
* Download invoices in PDF format
* Simple filtering/reporting capabilities

Installing mercury
==================

Please bear in mind that mercury is in beta.

The recommended way to install mercury is using pip and virtualenv. If you just
want to take it for a test drive, follow the installation instructions below,
then continue with "`Getting up and running`_".

To deploy into a production environment, follow the installation instructions
below and then read the "Deployment_" section.

Initial Requirements
--------------------

* PostgreSQL 8.2 or higher plus headers (the package is called posgresql-dev
  or postgresql-devel on many Linux distributions). If you're comfortable
  messing around with the Django database backend settings, it should be
  possible to use other databases too, although PostgreSQL is the only choice
  recommended for production use.
* Python 2.6 or 2.7
* Git (tested with 1.7)
* pip
* virtualenv

Installation
------------

You shouldn't have to run any the commands below as root.

Getting the source
~~~~~~~~~~~~~~~~~~

::

  $ git clone git://github.com/techcollective/mercury.git

The master branch should be stable, and is what is deployed on our own server.

Create and activate a virtualenv
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ virtualenv --no-site-packages -p /path/to/python2.6or2.7 VIRTUALENV_NAME
  $ source /path/to/VIRTUALENV_NAME/bin/activate

Installing dependencies
~~~~~~~~~~~~~~~~~~~~~~~

::

  $ pip install -r /path/to/mercury/requirements/development-frozen.txt

This should download and install all of mercury's dependencies.

.. _Getting up and running:

Running the test server
=======================

TODO (For the impatient: './manage.py syncdb, ./manage.py migrate, ./manage.py
loaddata configuration/fixtures/{initial_settings,admin_user}.json, ./manage.py
runserver')

.. _Deployment:

Deployment
==========

TODO (For the impatient: create fabfile/hosts.py using hosts_example.py as a
template, then type 'fab' for a list of commands. See the deploy directory for
a sample nginx config and centos initscript for gunicorn)
