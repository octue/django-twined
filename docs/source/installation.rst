.. _installation:

============
Installation
============

**django-twined** is available on `pypi <https://pypi.org/>`_, so installation into your python virtual environment is dead
simple:

.. code-block:: py

    pip install django-twined

Don't have a virtual environment with pip? You probably should! ``pyenv`` is your friend. Google it.

You'll need to install it as an app in your django settings:

.. code-block:: py

    INSTALLED_APPS = [
        ...
        'django_twined'
        ...

There is presently no need to run ``makemigrations`` because django-twined deliberately doesn't create models
(enabling it to run without a database). It does provide abstract models for you to use in your wider application
though.
