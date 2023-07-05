.. _service_revisions:

==========================
Running a service registry
==========================
Once the :ref:`services endpoint <adding_services_endpoint>` has been added, your app can be used as a service registry -
ie service revisions can be registered and requested from it.

Registering a service revision
==============================
To register a service revision:

.. code-block:: python

    import requests

    response = requests.post(
        "<base_url>/<chosen_path_for_django_twined_urls>/services/<namespace>/<name>",
        json={"revision_tag": "<revision_tag>"},
    )

For example, if your base URL is ``myapp.org/api``, you've registered the ``django-twined`` URLs under
``integrations/octue``, and the service revision you want to register is ``my-org/my-service:1.2.9``, the request would
be:

.. code-block:: python

    import requests

    response = requests.post(
        "https://myapp.org/api/integrations/octue/services/my-org/my-service",
        json={"revision_tag": "1.2.9"},
    )

Getting the default service revision
====================================
You can request the default service revision by not specifying a revision tag. By default, the service revision with the
latest semantic version revision tag will be returned.

.. code-block:: python

    import requests

    response = requests.get(
        "https://myapp.org/api/integrations/octue/services/my-org/my-service",
    )

    response.json()
    >>> {
        "namespace": "my-org",
        "name": "my-service",
        "revision_tag": "1.2.9",
        "is_default": True,
    }

.. tip::

    If you know the exact revision you want to use, you can still fetch further information for it.

    .. code-block:: python

        import requests

        response = requests.get(
            "https://myapp.org/api/integrations/octue/services/my-org/my-service"
            "?revision_tag=1.2.9",
        )

        response.json()
        >>> {
            "namespace": "my-org",
            "name": "my-service",
            "revision_tag": "1.2.9",
            "is_default": True,
        }

    Currently, the only useful information this provides is whether the requested service revision is the default or not.
    Later, more useful information will be returned (eg how to send a question to that specific service revision and
    access tokens to do so).


Controlling whether a service revision is set as the default at registration
============================================================================
The ``TWINED_SERVICE_REVISION_IS_DEFAULT_CALLBACK`` setting can be set to a user-defined callable to control whether a
service revision is set as the default for its service during registration. The callable must take one argument,
``service_revision`` (an instance of the ``ServiceRevision`` model), and return a boolean indicating whether the
revision should be set as the default. The default callable sets the service revision as the default if its revision
tag is the latest semantic version for the service.

Examples of how this feature can be used include:

- A/B testing
- Controlling the availability of beta versions of services
- Other custom selection of service revisions

`Click here <https://github.com/octue/django-twined/blob/main/django_twined/models/service_revisions.py#L18>`_ to see
the default callable as an example.
