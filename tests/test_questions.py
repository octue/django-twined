# Disables for testing:
# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=too-many-public-methods
import os
from unittest import skipIf
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django_twined.models import Question, ServiceRevision

from tests.server.example.models import QuestionWithValuesDatabaseStorage

from .factories import SuperUserFactory


SKIP_INTEGRATION_TESTS = not os.environ.get("RUN_INTEGRATION_TESTS", False)


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

    def test_question_duplicates_only_relevant_fields(self):
        """Ensures that duplication functionality works on a subclass of Question"""
        sr = ServiceRevision.objects.create(name="test-service")
        original = QuestionWithValuesDatabaseStorage.objects.create(
            service_revision=sr, apple_name="greenround", banana_name="yellowbend"
        )
        duplicate = original.get_duplicate()
        self.assertEqual(duplicate.apple_name, "greenround")
        self.assertEqual(duplicate.banana_name, "chiquita")

    @skipIf(
        SKIP_INTEGRATION_TESTS,
        "Skipping integration test - Accessing the admin requires staticfiles storage from django-gcp to have valid store and credentials",
    )
    def test_admin_duplicate(self):
        """Ensures that duplication in the admin creates a new question"""
        sr = ServiceRevision.objects.create(name="test-service")
        original = QuestionWithValuesDatabaseStorage.objects.create(
            service_revision=sr, apple_name="greenround", banana_name="yellowbend"
        )
        self.assertEqual(QuestionWithValuesDatabaseStorage.objects.count(), 1)
        duplicate_url = (
            reverse(f"admin:{original._meta.app_label}_{original._meta.model_name}_change", args=[original.id])
            + "?duplicate=True"
        )
        user = SuperUserFactory()
        self.client.login(username=user.username, password="password")
        response = self.client.get(duplicate_url, follow=True)
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertTrue(response.redirect_chain[0][0].startswith("/admin/example/questionwithvaluesdatabasestorage/"))
        self.assertEqual(QuestionWithValuesDatabaseStorage.objects.count(), 2)
