import threading
from functools import wraps
from uuid import uuid4

from django.db import connections

THREAD_LOCAL = threading.local()


class DynamicDbRouter(object):
    """A router that decides what db to read from based on a variable
    local to the current thread.
    """

    def db_for_read(self, model, **hints):
        return getattr(THREAD_LOCAL, 'DB_FOR_READ_OVERRIDE', 'default')

    def db_for_write(self, model, **hints):
        return getattr(THREAD_LOCAL, 'DB_FOR_WRITE_OVERRIDE', 'default')

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_syncdb(self, db, model):
        return None

    def allow_migrate(self, db, model):
        return self.allow_syncdb(db, model)


class in_database(object):
    """A decorator and context manager to do queries on a given database.

    :type database: str or dict
    :param database: The database to run queries on. A string
        will route through the matching database in
        ``django.conf.settings.DATABASES``. A dictionary will set up a
        connection with the given configuration and route queries to it.

    :type read: bool, optional
    :param read: Controls whether database reads will route through
        the provided database. If ``False``, reads will route through
        the ``'default'`` database. Defaults to ``True``.

    :type write: bool, optional
    :param write: Controls whether database writes will route to
        the provided database. If ``False``, writes will route to
        the ``'default'`` database. Defaults to ``False``.

    When used as eithe a decorator or a context manager, `in_database`
    requires a single argument, which is the name of the database to
    route queries to, or a configuration dictionary for a database to
    route to.

    Usage as a context manager:

    .. code-block:: python

        from my_django_app.utils import tricky_query

        with in_database('Database_A'):
            results = tricky_query()

    Usage as a decorator:

    .. code-block:: python

        from my_django_app.models import Account

        @in_database('Database_B')
        def lowest_id_account():
            Account.objects.order_by('-id')[0]

    Used with a configuration dictionary:

    .. code-block:: python

        db_config = {'ENGINE': 'django.db.backends.sqlite3',
                     'NAME': 'path/to/mydatabase.db'}
        with in_database(db_config):
            # Run queries
    """
    def __init__(self, database, read=True, write=False):
        self.read = read
        self.write = write
        self.created_db_config = False
        if isinstance(database, str):
            self.database = database
        elif isinstance(database, dict):
            # Note: this invalidates the docs above. Update them
            # eventually.
            self.created_db_config = True
            self.unique_db_id = str(uuid4())
            connections.databases[self.unique_db_id] = database
            self.database = self.unique_db_id
        else:
            msg = ("database must be an identifier for an existing db, "
                   "or a complete configuration.")
            raise ValueError(msg)

    def __enter__(self):
        if self.read:
            setattr(THREAD_LOCAL, 'DB_FOR_READ_OVERRIDE', self.database)
        if self.write:
            setattr(THREAD_LOCAL, 'DB_FOR_WRITE_OVERRIDE', self.database)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        setattr(THREAD_LOCAL, 'DB_FOR_READ_OVERRIDE', None)
        setattr(THREAD_LOCAL, 'DB_FOR_WRITE_OVERRIDE', None)
        if self.created_db_config:
            connections[self.unique_db_id].close()
            del connections.databases[self.unique_db_id]

    def __call__(self, querying_func):
        @wraps(querying_func)
        def inner(*args, **kwargs):
            # Call the function in our context manager
            with self:
                return querying_func(*args, **kwargs)
        return inner
