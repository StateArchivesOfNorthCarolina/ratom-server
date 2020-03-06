.. image:: https://github.com/libratom/ratom-logos/raw/master/basic_variations/RATOM_Vector_Logo_v1_300px.png

RATOM API
========================

.. image:: https://travis-ci.org/StateArchivesOfNorthCarolina/ratom-server.svg?branch=develop
    :target: https://travis-ci.org/StateArchivesOfNorthCarolina/ratom-server

Below you will find basic setup and deployment instructions for the ratom_api
project. To begin you should have the following applications installed on your
local development system:

- Python >= 3.7
- NodeJS >= 10.16
- `pip <http://www.pip-installer.org/>`_ >= 19
- `virtualenv <http://www.virtualenv.org/>`_ >= 1.10
- `virtualenvwrapper <http://pypi.python.org/pypi/virtualenvwrapper>`_ >= 3.0
- Postgres >= 9.3
- git >= 1.7

Django version
------------------------

The Django version configured in this template is conservative. If you want to
use a newer version, edit ``requirements/base.txt``.

Getting Started
------------------------

First clone the repository from Github and switch to the new directory::

    $ git clone git@github.com:StateArchivesOfNorthCarolina/ratom-server.git
    $ cd ratom_api

To setup your local environment you can use the quickstart make target `setup`,
which will install Python dependencies (via pip) into a virtualenv named
"ratom_api", configure a local django settings file, and create a database via
Postgres named "ratom_api" with all migrations run::

    $ make setup
    $ workon ratom_api

If you require a non-standard setup, you can walk through the manual setup steps
below making adjustments as necessary to your needs.

To setup your local environment you should create a virtualenv and install the
necessary requirements::

    # Check that you have python3.7 installed
    $ which python3.7
    $ mkvirtualenv ratom_api -p `which python3.7`
    (ratom_api)$ pip install -r requirements/dev.txt

Next, we'll set up our local environment variables. We use `django-dotenv
<https://github.com/jpadilla/django-dotenv>`_ to help with this. It reads
environment variables located in a file name ``.env`` in the top level directory
of the project. The only variable we need to start is
``DJANGO_SETTINGS_MODULE``::

    (ratom_api)$ cp ratom/settings/local.example.py ratom/settings/local.py
    (ratom_api)$ echo "DJANGO_SETTINGS_MODULE=ratom.settings.local" > .env

Create the Postgres database and run the initial migrate::

    (ratom_api)$ createdb -E UTF-8 ratom_api
    (ratom_api)$ python manage.py migrate

If you want to use `Travis <http://travis-ci.org>`_ to test your project,
rename ``project.travis.yml`` to ``.travis.yml``, overwriting the ``.travis.yml``
that currently exists.  (That one is for testing the template itself.)::

    (ratom_api)$ mv project.travis.yml .travis.yml


Black
-----

Run::

    $ pre-commit install

You can also use ``black`` to format on save. For example, configuration for VS Code::

    {
        "settings": {
            "python.formatting.provider": "black",
            "editor.formatOnSave": true,
            "python.linting.flake8Enabled": true,
            "python.linting.mypyEnabled": true
        }
    }


Import
-----------

A management command, ``import_psts``, can be used to ``.pst`` files into RATOM.

For example::

    python manage.py import_psts /Volumes/Seagate/RATOM/RevisedEDRMv1_Complete/kate_symes/* --clean

The search index can be rebuilt with::

    python manage.py search_index -f --rebuild --parallel


Development
-----------

🤯


Tests
----------

To run the projet unit tests, use::

    make test

A full-stack test with a real Enron .pst file is skipped by default. To enable it, run::

    TEST_ENRON_DATA_SET=true make test

HTML-based coverage reports are generated into ``htmlcov/``.


Sample Data
-----------

An API endpoint, at ``/api/v1/reset-sample-data/``, will reset sample datasets
with an authenicated POST request. This URL is disabled unless the
``RATOM_SAMPLE_DATA_ENABLED`` environment variable is set to ``true``. This is
enabled by default on staging and in development.

To reset the project sample data using a management command, run::

    python manage.py reset_sample_data

To create a new sample dataset from an existing account in your database, run::

    python manage.py sample_data --account="albert_meyers" --total=10 > ./api/sample_data/albert_meyers.json

Then populate additional entries in ``api.sample_data.data.SAMPLE_DATA_SETS``.


Deployment
----------

Deployment for this project is done by TravisCI on each merge to ``develop``.
You can inspect the ``.travis.yml`` file to see how it's done, or to update the
process. It relies on the
`caktus.django-k8s <https://github.com/caktus/ansible-role-django-k8s>`_ Ansible
role.

The frontend is deployed to a separate pod via its own repo, using the same process.

You can also test or update the deployment locally in the ``deployment/`` directory::

    pip install -r requirements/dev.txt
    cd deployment/
    ansible-galaxy install -r requirements.yaml
    ansible-playbook deploy.yaml

Note: This will deploy the image with the ``:latest`` tag. Normally, CI/CD will
deploy a tag with a commit sha to ensure the that the Kubernetes ``Deployment``
updates the underlying pods. You can override the ``k8s_container_image_tag`` on
the command line, if needed, to deploy a different image::

    ansible-playbook deploy.yaml -l caktus-ratom -e k8s_container_image_tag=my-docker-tag

You can see the available images in
`DockerHub <https://hub.docker.com/repository/docker/govsanc/ratom-server>`_


License(s)
==========

Logos, documentation, and other non-software products of the RATOM team are
distributed under the terms of Creative Commons 4.0 Attribution. Software
developed for the RATOM project is distributed under the terms of the MIT
License. See the LICENSE file for additional details.

Copyright 2020, The University of North Carolina at Chapel Hill.


Development Team
================

Developed by `Caktus Group <https://www.caktusgroup.com/>`_ for the Review,
Appraisal, and Triage of Mail (RATOM) project.

See https://ratom.web.unc.edu/ for RATOM project details, staff bios, and news.
