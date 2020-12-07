.. _registering_applications:

========================
Registering Applications
========================

One or more applications can :ref:`installed<_installing_app_dependencies>`_ and
:ref:`configured<_configuring>`_ in your django settings. ``django-twined`` will automatically register applications
that are successfully configured in the settings, turning them into services accessible via websocket.


.. _installing_app_dependencies:

Installing app dependencies
===========================

You'll need to install dependencies for your applications. Assuming your apps are based on the :ref:`templates<>`_, they
have a ``setup.py`` file which describes their dependencies. The easiest thing to do is to simply install them.

Your ``requirements.txt`` file might look like:
.. code-block::

   git+ssh://git@github.com/your_handle/app-name.git@0.0.3#egg=app_name
   git+ssh://git@github.com/your_handle/other-app-name.git@0.0.1-nowake#egg=other_app_name

The path locations of these apps (used for the configuration above) can be determined using e.g. ``pip show app_name``.

You may need tighter control over specific versions of their dependencies which is achievable using ``poetry``, a pip
lock file or by manually specifying precise versions of those dependencies in your requirements file.

.. ATTENTION::

   A current limitation is that all applications you run must have compatible dependencies, and will run on the same
   stack as your django server. :ref:`This issue<>`_ describes the particular issue, which is part of a wider
   architectural decision making process. **In short: Expect this setup to evolve.**


.. _configuring_apps:

Configuring apps
================

First, configure them in your ``settings.py``:

.. code-block:: python

   TWINED_SERVICES = {
       # The unique slugified name of the service (typically the same as the application name)
       "service-name": {
           # The default version to use if not specified in the URL
           "default_version": "0.0.1",
           "0.0.1": {
               "app_path": "/apps/app-name", # Path to where the app.py file is for this application
               "log_level": "info", # This will be provided to the application logger
               "skip_checks": False, # Tells the application to skip checks of incoming files
               "configuration_values": None, # Either a json string, object, or path to a json file on your server containing configuration values
               "configuration_manifest": None, # Either a json string, Manifest object, or path to a json file on your server containing configuration manifest
           }
       }
       # You can run any number of apps as services, but see the caveat below about their dependencies
       "other-service-name": {
           # The default version to use if not specified in the URL
           "default_version': "0.0.1",
           "0.0.1": {
               'app_path': '/apps/other-app-name',
               "log_level": "info",
               "skip_checks": False,
               'configuration_values': None,
               'configuration_manifest': None,
           }
       }
   }
