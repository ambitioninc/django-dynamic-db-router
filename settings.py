import os

from django.conf import settings


def configure_settings():
    """
    Configures settings for manage.py and for run_tests.py.
    """
    if not settings.configured:
        # Determine the database settings depending on if a test_db var is set in CI mode or not
        test_db = os.environ.get('DB', 'postgres')
        if test_db == 'postgres':
            db_config_one = {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'USER': 'postgres',
                'NAME': 'dynamic_db_router_one',
            }
            db_config_two = {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'USER': 'postgres',
                'NAME': 'dynamic_db_router_two',
            }
        elif test_db == 'sqlite':
            db_config_one = {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'dynamic_db_router_one',
            }
            db_config_two = {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'dynamic_db_router_two',
            }
        else:
            raise RuntimeError('Unsupported test DB {0}'.format(test_db))

        settings.configure(
            DATABASES={
                'default': db_config_one,
                'test': db_config_two,
            },
            DATABASE_ROUTERS=['dynamic_db_router.DynamicDbRouter'],
            INSTALLED_APPS=(
                'dynamic_db_router',
                'dynamic_db_router.tests',
            ),
            ROOT_URLCONF='dynamic_db_router.urls',
            SILENCED_SYSTEM_CHECKS=["1_7.W001"],
            DEBUG=False,
        )
