import logging
import uuid
from django.apps import apps
from django.conf import settings
from django.db import models
from octue.cloud.pub_sub.service import Service
from octue.resources.service_backends import get_backend


logger = logging.getLogger(__name__)


class AbstractRegisteredService(models.Model):
    """Abstract model to enable registration of available services in the system"""

    __QUESTION_MODEL__ = "django_twined.Question"

    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)

    name = models.SlugField(
        editable=False,
        help_text="Service name (e.g. in cloud run), also used in django settings to define service credentials",
        unique=True,
    )

    # TODO open an endpoint to receive updates of configuration_values, configuration_manifest and twine JSON
    # configuration_values = models.JSONField(default=dict(), help_text="Contents of the configuration_values strand")
    # configuration_manifest = models.JSONField(default=dict(), help_text="Contents of the configuration_manifest strand")

    @classmethod
    def get_question_model(cls):
        """Returns the question model used to store results"""
        return apps.get_model(*cls.__QUESTION_MODEL__.split("."))

    @property
    def topic(self):
        return f"octue.services.{self.id}"

    @property
    def service_settings(self):
        return settings.OCTUE_SERVICES[self.name]

    def ask(self, wait=False, timeout=1000, save_question=True, **kwargs):
        """Ask this service a question
        ```
        RegisteredService.objects.get(name='my-service').ask(input_values={}, input_manifest={})
        ```
        """
        backend = get_backend(self.service_settings["backend"])(
            project_name=self.service_settings["project_id"],
            credentials_environment_variable=self.service_settings["credentials_environment_variable"],
        )

        asker = Service(backend)
        subscription, question_uuid = asker.ask(
            service_id=self.topic,
            **kwargs,
        )

        QuestionModel = self.get_question_model()
        question = QuestionModel(id=question_uuid, registered_service=self, **kwargs)

        if save_question:
            question.save()

        if wait:
            question.update_answer(asker.wait_for_answer(subscription, timeout))
            if save_question:
                question.save()

        return question, subscription

    def __str__(self):
        return f"{str(self.id)[:12]} {self.name}"


class RegisteredService(AbstractRegisteredService):
    pass
