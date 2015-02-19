import os
import sqlite3

from django.db import connections
from django.test import TestCase
from django_dynamic_fixture import G

from dynamic_db_router import DynamicDbRouter, in_database
from .models import TestModel


class TestInDataBaseContextManager(TestCase):
    def test_string_identifier(self):
        G(TestModel, name='Arnold')
        with in_database('default'):
            count = TestModel.objects.count()
        expected = 1
        self.assertEqual(count, expected)

    def test_readonly_connection_writes_to_default(self):
        with in_database('test'):
            G(TestModel, name='Arnold')
            test_count = TestModel.objects.count()
        default_count = TestModel.objects.count()
        self.assertEqual(test_count, 0)
        self.assertEqual(default_count, 1)

    def test_write_connection_writes_to_test(self):
        with in_database('test', write=True):
            G(TestModel, name='Arnold')
            test_count = TestModel.objects.count()
        default_count = TestModel.objects.count()
        self.assertEqual(test_count, 1)
        self.assertEqual(default_count, 0)

    def test_write_only_connection_reads_from_default(self):
        with in_database('test', read=False, write=True):
            G(TestModel, name='Arnold')
            test_count = TestModel.objects.count()
        default_count = TestModel.objects.count()
        self.assertEqual(test_count, 0)
        self.assertEqual(default_count, 0)

    def test_bad_input_value(self):
        with self.assertRaises(ValueError):
            with in_database(2):
                pass


class TestDynamicDatabaseConnection(TestCase):
    def setUp(self):
        # Create a sqlite database with the models that django will
        # expect.
        PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
        self.db_filename = os.path.join(PROJECT_DIR, 'dynamic_test_router.db')
        conn = sqlite3.connect(self.db_filename)
        cur = conn.cursor()
        create_table_query = (
            'CREATE TABLE tests_testmodel('
            '    id PRIMARY KEY, name varchar(32));'
        )
        cur.execute(create_table_query)
        conn.commit()
        conn.close()

        # The database configuration to use with in_database
        self.test_db_config = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': self.db_filename,
        }

    def tearDown(self):
        os.remove(self.db_filename)

    def test_create_db_object(self):
        with in_database(self.test_db_config, write=True):
            G(TestModel, name='Arnold')
            G(TestModel, name='Sue')
            count = TestModel.objects.count()
        expected = 2
        self.assertEqual(count, expected)

    def test_where_db_objects_come_from(self):
        with in_database(self.test_db_config, write=True) as x:
            G(TestModel, name='Sue')
            database_name = TestModel.objects.get(name='Sue')._state.db
        expected_database_name = x.unique_db_id
        self.assertEqual(database_name, expected_database_name)

    def test_cleans_up(self):
        starting_connections = len(connections.databases)
        with in_database(self.test_db_config, write=True):
            G(TestModel, name='Sue')
        ending_connections = len(connections.databases)
        self.assertEqual(starting_connections, ending_connections)


class TestInDatabaseDecorator(TestCase):
    def test_decorator_matches_context_manager(self):
        @in_database('test')
        def test_db_record_count():
            return TestModel.objects.count()

        with in_database('test'):
            G(TestModel, name='Michael Bluth')
            context_count = TestModel.objects.count()
        decorator_count = test_db_record_count()
        self.assertEqual(context_count, decorator_count)


class TestDynamicDbRouterDefaults(TestCase):
    def test_db_for_read(self):
        router = DynamicDbRouter()
        db_for_read = router.db_for_read(None)
        self.assertIn(db_for_read, ['default', None])

    def test_db_for_wrte(self):
        router = DynamicDbRouter()
        db_for_write = router.db_for_write(None)
        self.assertIn(db_for_write, ['default', None])

    def test_allow_relation(self):
        router = DynamicDbRouter()
        allow_relation = router.allow_relation(None, None)
        self.assertEqual(allow_relation, True)

    def test_allow_syncdb(self):
        router = DynamicDbRouter()
        allow_syncdb = router.allow_syncdb(None, None)
        self.assertEqual(allow_syncdb, None)

    def test_allow_migrate(self):
        router = DynamicDbRouter()
        allow_migrate = router.allow_migrate(None, None)
        self.assertEqual(allow_migrate, None)
