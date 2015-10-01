
Quickstart
==========


Installation
------------

Installing Requests is simple with pip, just run this in your terminal::

    pip install pycdstar

You may also install from a clone of the GitHub repository, running
its `setup.py <https://github.com/clld/pycdstar/blob/master/setup.py>`_ like so::

    python setup.py develop


Configuration
-------------

pycdstar can be configured to discover access information for a cdstar service.
This configuration can either be passed to an API client per session or stored in
a configuration file. pycdstar uses the `appdirs` package to determine default
locations for configuration files on different platforms, see the
`appdirs README <https://github.com/ActiveState/appdirs#some-example-output>`_ for
details.

.. code-block:: ini

    [service]
    url=http://127.0.0.1:8080
    user=user
    password=pwd


Authentication
~~~~~~~~~~~~~~

pycdstar so far only supports authentication via HTTP Basic Auth.

Logging
~~~~~~~

Logging can be configured using standard
`python logging configuration syntax <https://docs.python.org/2/library/logging.config.html#configuration-file-format>`_.


Notes
=====

- Coverage of the API
- Mutation tracking: We have not gone to the lengths described
  `elsewhere <http://variable-scope.com/posts/mutation-tracking-in-nested-json-structures-using-sqlalchemy>`_
  to track mutation of