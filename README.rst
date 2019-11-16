

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


Black
-----

Run::

    $ pre-commit install

You can also use ``black`` to format on save. For example, configuration for VS Code::

    {
        "settings": {
            "python.formatting.provider": "black",
            "editor.formatOnSave": true
        }
    }


Development
-----------

🤯

Staging environment
-------------------

GKE Cluster Access
~~~~~~~~~~~~~~~~~~

* Download and install the Google Cloud SDK: https://cloud.google.com/sdk/install

* Download and install kubectl: https://kubernetes.io/docs/tasks/tools/install-kubectl/ (please ensure you install v1.15 or later; v1.16 is current as of October, 2019)

* Login to GCP and populate credentials in your ``~/.kube/config``::

      gcloud auth login
      gcloud config set project ratom-258217
      gcloud container clusters get-credentials --region=us-east1 ratom-cluster

* Verify access to the cluster::

      $ kubectl cluster-info
      Kubernetes master is running at https://35.229.102.139
      GLBCDefaultBackend is running at https://35.229.102.139/api/v1/namespaces/kube-system/services/default-http-backend:http/proxy       Heapster is running at https://35.229.102.139/api/v1/namespaces/kube-system/services/heapster/proxy
      KubeDNS is running at https://35.229.102.139/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
      Metrics-server is running at https://35.229.102.139/api/v1/namespaces/kube-system/services/https:metrics-server:/proxy

      To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.

* Set the namespace in your ``kubectl`` context to ``ratom-staging``::

    kubectl config set-context --current --namespace=ratom-staging


Interacting with Pods
~~~~~~~~~~~~~~~~~~~~~

You can interact with running pods via ``kubectl``, for example::

    # list running pods
    $ kubectl get pods
    NAME                       READY   STATUS    RESTARTS   AGE
    api-55c4fbb789-b8m2v       1/1     Running   0          13m
    api-55c4fbb789-zmksn       1/1     Running   0          13m
    frontend-687d4b9bf-9xcfz   1/1     Running   0          15m
    frontend-687d4b9bf-pnqkw   1/1     Running   0          15m

    # tail logs for the api
    $ kubectl logs -f deployment/api
    # <snip>
    [pid: 15|app: 0|req: 10/14] 10.52.1.7 () {58 vars in 1375 bytes} [Fri Nov  8 11:19:57 2019] GET /admin/ratom/message/ => generated 28852 bytes in 129 msecs (HTTP/1.1 200) 10 headers in 513 bytes (1 switches on core 2)
    [pid: 14|app: 0|req: 5/15] 10.52.1.7 () {60 vars in 1271 bytes} [Fri Nov  8 11:20:32 2019] POST /graphql => generated 240 bytes in 30 msecs (HTTP/1.1 200) 8 headers in 400 bytes (1 switches on core 1)

    # start a shell in a pod, where you can run management commands, etc.
    $ kubectl exec -it api-55c4fbb789-b8m2v bash
    root@api-55c4fbb789-b8m2v:/code#

    # copy a file to a pod
    $ kubectl cp /path/to/source api-55c4fbb789-b8m2v:/path/to/dest


Deployment
~~~~~~~~~~

Deployment for this project is done by CircleCI on each merge to ``develop``. You can inspect
the ``.circle/config.yml`` file to see how it's done, or to update the process. It relies on the
`django-k8s <https://github.com/caktus/ansible-role-django-k8s>`_ Ansible role.

The frontend is deployed to a separate pod via its own repo, using the same process.

You can also test or update the deployment locally in the ``deployment/`` directory::

    pip install -r requirements/dev.txt
    cd deployment/
    ansible-galaxy install -r requirements.yaml
    ansible-playbook deploy.yaml

Note: This will deploy the image with the ``:latest`` tag. Normally, CI/CD will deploy a tag
with a commit sha to ensure the that the Kubernetes ``Deployment`` updates the underlying pods.
You can override the ``k8s_container_image_tag`` on the command line, if needed, to deploy a different
image::

    ansible-playbook deploy.yaml -l gcp-staging -e k8s_container_image_tag=my-docker-tag

You can see the available images in the GCR repo for this project in GCP:

https://console.cloud.google.com/gcr/images/ratom-258217/US/ratom_api?project=ratom-258217&organizationId=450077367739&gcrImageListsize=30
