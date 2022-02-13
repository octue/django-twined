# Disables for testing:
# pylint: disable=missing-docstring

from django.test import TestCase
from django_twined.models import MyModel


class MyModelTestCase(TestCase):
    """ "Normal" synchronous django tests to ensure your models / rest API / Whatever works correctly"""

    def test_something(self):
        """Test that something happens"""
        MyModel()
