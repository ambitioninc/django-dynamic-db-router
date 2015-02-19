Quickstart
==========

First, make sure you have setup Django Dynamic DB Router by installing
the package using ``pip install django-dynamic-db-router`` and make
sure you have added
``DATABASE_ROUTERS=['dynamic_db_router.DynamicDbRouter']`` to your
Django settings.

Once you have installed and set up ``django-dynamic-db-router`` all
your routing of queries between different databases can be done with
``dynamic_db_router.in_databases``, which can be used as a context
manager or function decorator. There are two main use cases for
``in_database``. The first is to connect to databases that are already
configured in your Django settings ``DATABASES`` parameter. The second
is to establish a connection to a database that has not been
configured, and route queries there. Both of these use cases will be
described below.

Routing to Configured Databases
-------------------------------

In the case that you have multiple databases set up in your django
project, you will should have a ``settings.py`` file containing
something like:

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'my_local_database',
            'USER': 'postgres',
            'PASSWORD': 'my-pass',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        },
        'external': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'my_external_database',
            'USER': 'postgres',
            'PASSWORD': 'my-pass',
            'HOST': 'example.com',
            'PORT': '5432',
        },
        # ...
    }
    DATABASE_ROUTERS = ['dynamic_db_router.DynamicDbRouter']

possibly with additional databases configured. With this
configuration, all queries will, by default, go to the ``'default'``
database. To route queries to the ``'external'`` database, you could
use Django's built in ``.using('external')`` method on
querysets. However, this becomes cumbersome when doing a large number
of queries, or using libraries that don't take multiple databases into
account.

It is much easier to do these queries in a context manager, where you
can write the queries such that they will automatically be routed to
the correct database. This is what the ``in_database`` context manager
provides:

.. code-block:: python

    from dynamic_db_router import in_database

    from my_app.models import MyModel
    from some_app.utils import complex_query_function

    with in_database('external'):
        input = MyModel.objects.filter(field_a="okay")
        output = complex_query_function(input)

In the example above, the ``MyModel.objects.filter`` query will be
performed against the ``'external'`` database, but so will any queries
made by ``complex_query_function``, which otherwise may be impossible
to guarantee with ``.using``. These queries will only be routed to the
``'external'`` database for the ``with`` block, and will automatically
route to the ``'default'`` database outside of the ``with`` block
again.

Often times when working with multiple databases, you want to control
whether you can read and write to a given database. For this reason,
the ``in_database`` context manager takes two optional parameters,
``read`` and ``write``. These control whether reads and writes go to
the provided database, respectively, and default to ``read=True`` and
``write=False``.

Allowing writing to the ``'external'`` database then, would look like:

.. code-block:: python

    with in_database('external', write=True):
        MyModel.objects.create(
            field_a='bad',
            field_b=17774,
        )

It should be noted that with ``write=False`` attempts to write inside
the context manager will *not* fail, but will be routed to the
``'default'`` database. This also holds for ``read=False``. It is up
to the user to understand what sorts queries are being run within the
context manager. In the example above, if ``write`` were set to
``False``, the ``MyModel`` object would still be created, but in the
``'default'`` database.

Additionally, if you want to define a function which always pulls its
results from a certain database, ``in_database`` can be used as a
function decorator:

.. code-block:: python

    from dynamic_db_router import in_database

    @in_database('external')
    def get_external_models_count(models):
        counts = {}
        for model in models:
            counts[model] = model.objects.count()
        return counts

Whenever this function is run, it will route the queries in the
function to the ``'external'`` database. The decorator version of
``in_database`` takes all the same arguments as the context-manager
version, so it is possible to control read/write permissions in the
same way.


Dynamic Database Configuration and Routing
------------------------------------------

In addition to accessing databases that are already configured in
``django.conf.settings.DATABASES``, ``django-dynamic-db-router`` can
also be used to dynamically set up a database configuration, route
queries to it and tear down the configuration as the context manager
or decorated function exits.

In order for this to function properly, the database you are trying to
connect to dynamically must already be set up with tables
corresponding to whatever models you want to use to query them. Given
such a database, dynamically connecting to it and querying it is as
simple as passing ``in_database`` a dictionary with connection
information, rather than a string:

.. code-block:: python

    from dynamic_db_router import in_database
    from my_app.models import MyModel

    external_db = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'my_external_database',
        'USER': 'postgres',
        'PASSWORD': 'my-pass',
        'HOST': 'example.com',
        'PORT': '5432',
    }

    with in_database(external_db):
        target = MyModel.objects.get(field_b=17774)

In the example above, even though there is no entry for the database
configuration in ``settings.DATABASES``, ``in_databases`` is able to
access the database, run the query, and clean up after itself.

When using a configuration as an argument, ``in_databases`` still
supports read and write controls as described above, and supports use
as a function decorator.
