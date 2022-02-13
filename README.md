[![PyPI version](https://badge.fury.io/py/django-twined.svg)](https://badge.fury.io/py/django-twined)
[![codecov](https://codecov.io/gh/octue/django-twined/branch/master/graph/badge.svg)](https://codecov.io/gh/octue/django-twined)
[![Documentation Status](https://readthedocs.org/projects/django-twined/badge/?version=latest)](https://django-twined.readthedocs.io/en/latest/?badge=latest)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

# Django Twined

This is a plugin for django, enabling you to orchestrate [twined-based octue services](https://octue.readthedocs.io) services from your own django
server.

Documentation is [here](https://django-twined.readthedocs.io/en/latest/).

This is great for advanced use cases where:

- you have specific security/firewalling requirements, or
- you want to manage your own auth, or
- you have specific/unusual data integration needs, or
- already have a web based data service, and want to expose it in the twined ecosystem.

**Health warning:** to use this plugin to deploy your services, you'll need to handle all your own data
storage/orchestration, devops, server management, security and auth. So for most users we'd recommend getting in touch at
[octue.com](https://www.octue.com/contact) so we can help!
