Django Dynamic Db Router
========================

Working with multiple databases within django is supported, but the
syntax requires peppering ``.using('my_database')`` throughout all
queries that need to be routed to different databases. This is
especially painful when trying to use libraries that were written
without multiple database support in mind. With this library, running
complex queries across different databases is as simple as:

.. code-block:: python

    from dynamic_db_router import in_database

    with in_database('non-default-db'):
        result = run_complex_query()

To set up you django project to be able to use this router, simply
``pip install django-dynamic-db-router`` and add
``DATABASE_ROUTERS=['dynamic_db_router.DynamicDbRouter']`` to your
Django settings.

Django Dynamic DB Router includes a number of additional features,
such as:

- Using ``in_database`` as a function decorator.
- Read and write protection controls.
- Creating temporary database configurations dynamically.

For more information, and complete API documentation, see the
quickstart guide or code documentation, linked below.


Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   installation
   ref/dynamic_db_router
   contributing
   release_notes

