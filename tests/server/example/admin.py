from django.contrib import admin
from django.db.models import JSONField
from django_twined.admin import QuestionAdmin, ServiceUsageEventAdmin
from jsoneditor.forms import JSONEditor

from .models import ConcreteSynchronisedDatastore, QuestionWithValuesDatabaseStorage


@admin.register(ConcreteSynchronisedDatastore)
class ConcreteSynchronisedDatastoreAdmin(admin.ModelAdmin):
    """Defines an admin panel for the concrete synchronised datastore"""

    search_fields = ["id", "a_string_tag", "a_decimal_tag"]
    list_display = ("id", "a_string_tag", "a_decimal_tag")


@admin.register(QuestionWithValuesDatabaseStorage)
class QuestionWithValuesDatabaseStorageAdmin(QuestionAdmin):
    pass


class CustomServiceUsageEventAdmin(ServiceUsageEventAdmin):
    """Defines an admin panel for Service Usage Events"""

    readonly_fields = ("data", "publish_time", "kind", "question", "service_revision")
    date_hierarchy = "publish_time"

    formfield_overrides = {
        JSONField: {"widget": JSONEditor},
    }

    # list_display = ("service_revision__name", "service_revision__tag", "kind", "publish_time", "question")
    # list_filter = ("service_revision__name", "service_revision__tag", "kind", "publish_time", "question")

    @admin.display(ordering="registered_service__name")
    def registered_service_name(self, obj):
        """Retrieve the name of the related registered service object"""
        return obj.registered_service.name

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("question").prefetch_related("registered_service")
