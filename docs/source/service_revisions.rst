.. _service_revisions:

==========================
Running a service registry
==========================
Once the :ref:`services endpoint <adding_services_endpoint>` has been added, your app can be used as a service registry -
i.e. service revisions can be registered and requested from it.

Registering a service revision
==============================
To register a service revision:

.. code-block:: python

    import requests

    response = requests.post(
        "<base_url>/<chosen_path_for_django_twined_urls>/services/<namespace>/<name>",
        json={"revision_tag": "<revision_tag>", "is_default": True},
    )

For example, if your base URL is ``myapp.org/api``, you've registered the ``django-twined`` URLs under
``integrations/octue``, and the service revision you want to register is ``my-org/my-service:1.2.9``, the request would
be:

.. code-block:: python

    import requests

    response = requests.post(
        "myapp.org/api/integrations/octue/services/my-org/my-app",
        json={"revision_tag": "1.2.9", "is_default": True},
    )

Getting a specific service revision
===================================
Make a request like the following:

.. code-block:: python

    import requests

    response = requests.get(
        "myapp.org/api/integrations/octue/services/my-org/my-app?revision_tag=1.2.9",
    )

    response.json()
    >>> {
        "namespace": "my-org",
        "name": "my-service",
        "revision_tag": "1.2.9",
        "is_default": True,
    }

Currently, the only useful information this provides is whether the requested service revision is the default or not.
Later, more useful information will be returned including how to send a question to that specific service revision and
access tokens to do so.

Getting the latest service revision
===================================
This request is the same as above except the revision tag is omitted. By default, the service revision with the latest
semantic version revision tag will be returned.

.. code-block:: python

    import requests

    response = requests.get(
        "myapp.org/api/integrations/octue/services/my-org/my-app",
    )

    response.json()
    >>> {
        "namespace": "my-org",
        "name": "my-service",
        "revision_tag": "1.2.9",
        "is_default": True,
    }

Controlling which service revision is returned by default
=========================================================
The ``TWINED_SERVICE_REVISION_SELECTION_CALLBACK`` setting can be set to a user-defined callable to control which
service revision is returned when a service is requested but the revision tag isn't specified. This callable must take
two keyword arguments: ``namespace`` and ``name`` and must return a single instance of the ``ServiceRevision`` model.

Examples of how this feature can be used include:

- A/B testing
- Returning certain service revisions based on the request or the requester
- Controlling the availability of beta versions of services
- Other custom routing of questions to services
