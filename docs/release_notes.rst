Release Notes
=============

v0.1
----

* This is the initial release of django-dynamic-db-router. It includes
  a core featureset of:

  - A ``in_database`` context-manager and function-decorator to route
    all queries to a database dynamically.
  - Read and write protection controls on ``in_database``.
  - Dynamically load database configurations for the lifetime of the
    context-manager.
  - 100% branch test coverage.
  - Documentation at the package and API level.
