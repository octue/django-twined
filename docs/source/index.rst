.. ATTENTION::
    This library is in very early stages. Like the idea of it? Please
    `star us on GitHub <https://github.com/octue/django-twined>`_ and contribute via the
    `issues board <https://github.com/octue/django-twined/issues>`_ and the
    `twined roadmap <https://github.com/orgs/octue/projects/19>`_.

=============
Django Twined
=============

**django-twined** helps run data services based on the :ref:`twined framework<https://twined.readthedocs.io>`_ from your
own django server.

If you're a scientist or engineer getting started with creating online data services, here is definitely
not the right place to start! Check out the documentation for :ref:`twined<https://twined.readthedocs.io>`_ and
the example :ref:`app templates in the SDK<https://github.com/octue/octue-sdk-python/tree/main/octue/templates>`_.

.. epigraph::
   *"Twined" [t-why-nd] ~ encircled, twisted together, interwoven*


.. _aims:

Aims
====

This is an installable app for django, that provides consumers (for websocket connections to data services)
and a task manager which runs your apps.

This is great for advanced use cases where:
 - you have specific security/firewalling requirements, or
 - you want to manage your own auth, or
 - you have specific/unusual data integration needs, or
 - you have a pre-existing django-based web app and want to connect it into the twined ecosystem
 - you want to run your apps on a cluster, and provide a single entrypoint for external services to connect

**Health warning:** to use this plugin to deploy your twined apps, you'll need to handle all your own data
storage/orchestration, devops, server management, security and auth.

So for most users we'd recommend using :ref:`octue.com<https://www.octue.com>`_ which does all this for you!


.. _reason_for_being:

Raison d'etre
=============

To help scientists and engineers solve the crisis. :ref:`More here<https://twined.readthedocs.io/en/latest/#raison-d-etre>`.

.. toctree::
   :maxdepth: 2

   self
   installation
   quick_start
   examples
   license
   version_history
