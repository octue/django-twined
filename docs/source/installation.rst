.. _installation:

============
Installation
============

Install the library
-------------------
**django-twined** is available on `pypi <https://pypi.org/>`_, so installation into your python virtual environment is dead
simple:

.. code-block:: py

    poetry add django-twined

Not using `poetry <https://python-poetry.org/>`_  yet? You definitely should, there's a small learning curve then it removes a world of pip agony :)

Install the django app
----------------------
You'll need to install ``django_twined``, ``django_gcp`` and ``jsoneditor`` as apps in your django settings:

.. code-block:: py

    INSTALLED_APPS = [
        # ...
        'django_gcp',  # For event handlers and flexible storages
        'django_twined',
        'jsoneditor',  # For editing JSON in modeladmin views
        # ...
    ]

.. tip::
    You can use `django-gcp <https://django-gcp.readthedocs.io/en/latest/>`_ for your media/static storage, event handlers and task queues too!

.. _adding_services_endpoint:

Add the services endpoint
-------------------------
Include the django-twined URLs in your ``your_app/urls.py``:

.. code-block:: python

   from django.urls import include, re_path

   urlpatterns = [
      # ...other routes
      # Use whatever regex you want:
      re_path(r"^integrations/octue/", include("django_twined.urls")),
   ]

Using ``python manage.py show_urls`` you can now see the endpoint for registering and getting service revisions appear in your app.

Run migrations
--------------
Then run ``python manage.py migrate django_twined`` to add the models used for managing services, events and questions to your database.

Add the base URL
----------------
Finally, make sure the ``BASE_URL`` setting is present in ``settings.py`` - it's used to create absolute URLs for webhooks.

.. code-block:: py

    BASE_URL = "https://your-server.com"
