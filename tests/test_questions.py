# Disables for testing:
# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=too-many-public-methods

from unittest.mock import patch
from django.test import TestCase
from django_twined.models import Question, ServiceRevision

from tests.server.example.models import QuestionWithValuesDatabaseStorage


class QuestionTestCase(TestCase):
    @patch("django_twined.models.ServiceRevision.ask", return_value=("subscription", "question_uuid"))
    def test_ask_question(self, mock):
        """Ensures that a question can be asked"""
        sr = ServiceRevision.objects.create(name="test-service")
        q = QuestionWithValuesDatabaseStorage.objects.create(service_revision=sr)
        q.input_values = {"question_attribute": "1"}
        q.ask()
        self.assertTrue(mock.called)
        self.assertEqual(mock.call_count, 1)
        self.assertIn("question_id", mock.call_args.kwargs)
        self.assertIn("input_values", mock.call_args.kwargs)
        self.assertIn("input_manifest", mock.call_args.kwargs)
        self.assertIn("question_attribute", mock.call_args.kwargs["input_values"])

    def test_input_values_get_saved(self):
        """Ensures that input values get saved on the mixin.
        I'm testing this because the objects.create() doesn't accept the input_values
        kwarg field inherited from the mixin, so I want to check the mixin works right
        """
        sr = ServiceRevision.objects.create(name="test-service")
        q = QuestionWithValuesDatabaseStorage.objects.create(service_revision=sr)
        q.input_values = {"question_attribute": "1"}
        q.save()

        q_retrieved = QuestionWithValuesDatabaseStorage.objects.first()
        self.assertTrue(hasattr(q_retrieved, "input_values"))

    def test_inherited_object_query(self):
        """Ensures that the base Question model can be used to get subclasses via the InheritanceManager"""
        sr = ServiceRevision.objects.create(name="test-service")
        child_q = QuestionWithValuesDatabaseStorage.objects.create(service_revision=sr)
        raw_q = Question.objects.get(id=child_q.id)
        subclass_q = Question.objects.get_subclass(id=child_q.id)
        self.assertFalse(hasattr(raw_q, "input_values"))
        self.assertTrue(hasattr(subclass_q, "input_values"))
        self.assertTrue(subclass_q.__class__.__name__, "QuestionWithValuesDatabaseStorage")
