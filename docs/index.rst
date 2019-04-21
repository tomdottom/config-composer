
Welcome to ConfigSource's documentation!
========================================

ConfigSource makes configuration of applications easier by seperating what
configuration parameters you need from where you intend to get those parameters
(environment variables, envfile, AWS parameter store, HashiCorp Vault secrets,
etc ...).

The *config specification* (ConfigSpec) lives with your application and
provides type conversions.

The *source specification* (SourceSpec) is intended to be set at deploy time
and allows teams to easily adjust the source of configuration options
without changing the application.

For more see :ref:`beyond-12-factor-app-config`

Quick Example
-------------

.. literalinclude:: quickstart.py

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   api



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
