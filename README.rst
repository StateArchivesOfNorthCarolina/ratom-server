

.. EDIT the below links to use the project's github repo path. Or just remove them.

.. image:: https://requires.io/github/GITHUB_ORG/ratom_api/requirements.svg?branch=master
.. image:: https://requires.io/github/GITHUB_ORG/ratom_api/requirements.svg?branch=develop

Ratom_Api
========================

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

    $ git clone git@github.com:[ORGANIZATION]/ratom_api.git
    $ cd ratom_api

To setup your local environment you can use the quickstart make target `setup`, which will
install Python dependencies (via pip) into a virtualenv named
"ratom_api", configure a local django settings file, and create a database via
Postgres named "ratom_api" with all migrations run::

    $ make setup
    $ workon ratom_api

If you require a non-standard setup, you can walk through the manual setup steps below making
adjustments as necessary to your needs.

To setup your local environment you should create a virtualenv and install the
necessary requirements::

    # Check that you have python3.7 installed
    $ which python3.7
    $ mkvirtualenv ratom_api -p `which python3.7`
    (ratom_api)$ pip install -r requirements/dev.txt

Next, we'll set up our local environment variables. We use `django-dotenv
<https://github.com/jpadilla/django-dotenv>`_ to help with this. It reads environment variables
located in a file name ``.env`` in the top level directory of the project. The only variable we need
to start is ``DJANGO_SETTINGS_MODULE``::

    (ratom_api)$ cp ratom_api/settings/local.example.py ratom_api/settings/local.py
    (ratom_api)$ echo "DJANGO_SETTINGS_MODULE=ratom_api.settings.local" > .env

Create the Postgres database and run the initial migrate::

    (ratom_api)$ createdb -E UTF-8 ratom_api
    (ratom_api)$ python manage.py migrate

If you want to use `Travis <http://travis-ci.org>`_ to test your project,
rename ``project.travis.yml`` to ``.travis.yml``, overwriting the ``.travis.yml``
that currently exists.  (That one is for testing the template itself.)::

    (ratom_api)$ mv project.travis.yml .travis.yml

Development
-----------

🤯

Deployment
----------

Deployment for this project is done by CircleCI on each merge to ``develop``. You can inspect
the ``.circle/config.yml`` file to see how it's done, or update the process.

You can also test or update the deployment locally in the ``deployment/`` directory::

    pip install -r requirements/dev.txt
    cd deployment/
    ansible-galaxy install -r requirements.yaml
    gcloud auth login
    gcloud config set project ratom-258217
    gcloud container clusters get-credentials --region=us-east1 ratom-cluster
    ansible-playbook deploy.yaml

Note: This will deploy the image with the ``:latest`` tag. Normally, CI/CD will deploy a tag
with a commit sha to ensure the that the Kubernetes ``Deployment`` updates the underlying pods.
You can override the ``CONTAINER_IMAGE_TAG`` on the command line, if needed, to deploy a different
image::

    ansible-playbook deploy.yaml -e CONTAINER_IMAGE_TAG=my-docker-tag

You can see the available images in the GCR repo for this project in GCP:

https://console.cloud.google.com/gcr/images/ratom-258217/US/ratom_api?project=ratom-258217&organizationId=450077367739&gcrImageListsize=30
