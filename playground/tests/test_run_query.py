from django.test import TestCase

from ..views import run_query

# from django.db import connection



class RunQueryTestCase(TestCase):
    def setUp(self):
        self.model_def = """
from django.db import models

class Foo(models.Model):
    from django.db import models
    bar = models.CharField(max_length=255)
"""

    def test_run_query__all(self):
        qs = run_query(self.model_def, 'Foo.objects.all()')
        self.assertEqual(str(qs.query), 'SELECT "playground_foo"."id", "playground_foo"."bar" FROM "playground_foo"')

    def test_run_query__filter(self):
        qs = run_query(self.model_def, 'Foo.objects.filter(bar="bar")')
        self.assertEqual(str(qs.query), 'SELECT "playground_foo"."id", "playground_foo"."bar" FROM "playground_foo" WHERE "playground_foo"."bar" = bar')

    def test_run_query__order_by(self):
        qs = run_query(self.model_def, 'Foo.objects.all().order_by("bar")')
        self.assertEqual(str(qs.query), 'SELECT "playground_foo"."id", "playground_foo"."bar" FROM "playground_foo" ORDER BY "playground_foo"."bar" ASC')

#    def test_run_query__distinct(self):
#        qs = run_query(self.model_def, 'Foo.objects.all().distinct("bar")')
#        self.assertEqual(str(qs.query), 'SELECT DISTINCT "playground_foo"."bar" FROM "playground_foo"')

    def test_run_query__union(self):
        qs = run_query(self.model_def, 'Foo.objects.all().union(Foo.objects.all())')
        self.assertEqual(str(qs.query), 'SELECT "playground_foo"."id", "playground_foo"."bar" FROM "playground_foo" UNION SELECT "playground_foo"."id", "playground_foo"."bar" FROM "playground_foo"')

    def test_run_query__intersection(self):
        qs = run_query(self.model_def, 'Foo.objects.all().intersection(Foo.objects.all())')
        self.assertEqual(str(qs.query), 'SELECT "playground_foo"."id", "playground_foo"."bar" FROM "playground_foo" INTERSECT SELECT "playground_foo"."id", "playground_foo"."bar" FROM "playground_foo"')

    def test_run_query__difference(self):
        qs = run_query(self.model_def, 'Foo.objects.all().difference(Foo.objects.all())')
        self.assertEqual(str(qs.query), 'SELECT "playground_foo"."id", "playground_foo"."bar" FROM "playground_foo" EXCEPT SELECT "playground_foo"."id", "playground_foo"."bar" FROM "playground_foo"')

    def test_run_query__qs_union(self):
        """
        Test the magical secret operator |
        """
        qs = run_query(self.model_def, 'Foo.objects.filter(bar="bar1") | Foo.objects.filter(bar="bar2")')
        self.assertEqual(str(qs.query), 'SELECT "playground_foo"."id", "playground_foo"."bar" FROM "playground_foo" WHERE ("playground_foo"."bar" = bar1 OR "playground_foo"."bar" = bar2)')

    def test_run_query__qs_union_multiple(self):
        qs = run_query(self.model_def, 'Foo.objects.filter(bar="bar1") | Foo.objects.filter(bar="bar2") | Foo.objects.filter(bar="bar3")')
        self.assertEqual(str(qs.query), 'SELECT "playground_foo"."id", "playground_foo"."bar" FROM "playground_foo" WHERE ("playground_foo"."bar" = bar1 OR "playground_foo"."bar" = bar2 OR "playground_foo"."bar" = bar3)')

#    def test_run_query__count(self):
#        qs = run_query(self.model_def, 'Foo.objects.count()')
#        print(qs.query)
#        print(connection.queries)
