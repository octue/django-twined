# Disables for testing:
# pylint: disable=missing-docstring

from django.test import TestCase

from tests.test_server.models import ConcreteSynchronisedDatastore


class MyModelTestCase(TestCase):
    """ "Normal" synchronous django tests to ensure your models / rest API / Whatever works correctly"""

    def test_something(self):
        """Test that something happens"""
        ConcreteSynchronisedDatastore()
