.. _settings:

Settings
========

.. list-table::
   :widths: 15 10 30
   :header-rows: 1

   * - Name
     - Type
     - Description
   * - ``TWINED_BASE_URL``
     - str
     - The server address for generating absolute webhook URLs, eg ``"https://api.you.com"``
   * - ``TWINED_DEFAULT_NAMESPACE``
     - str
     - The namespace used by default (if none specified) when creating Service Revisions. Typically your organisation, and should be in kebab case, eg ``"mega-corp"``.
   * - ``TWINED_DEFAULT_PROJECT_NAME``
     - str
     - The GCP project name used by default (if none specified) when creating Service Revisions. This is the project where the default-namespace services reside. Often (but not necessarily), this is the same as the namespace eg ``"mega-corp"``.
   * - ``TWINED_DEFAULT_TAG``
     - str
     - The tag used by default (if none specified) when creating new Service Revisions. ``"latest"`` is used if not specified.
   * - ``TWINED_SERVICES``
     - dict
     - DEPRECATED - DO NOT USE. The ``ServiceRevision`` model replaces the outgoing ``RegisteredService`` model, allows update of the parameters specified here, without rebooting django.
   * - ``TWINED_DATA_STORES``
     - dict
     - A dictionary defining one or more Data Stores, which map a database table (django Model) to a bucket on GCP, syncing metadata between the files in the bucket and filterable / searchable columns in teh DB table.
   * - ``TWINED_SERVICE_REVISION_SELECTION_CALLBACK``
     - callable
     - A function that takes two positional arguments (the namespace and name of a service) and returns a service revision. The function is used to select the service revision returned by the services endpoint. Defaults to returning the service revision with the latest semantic version tag.
