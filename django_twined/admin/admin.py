from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django_twined.models import Question, ServiceRevision, ServiceUsageEvent

from .fieldsets import question_basic_fieldset
from .mixins import CreatableFieldsMixin


class QuestionAdmin(admin.ModelAdmin):
    """Subclass this QuestionAdmin to get started administering your question subclasses"""

    change_form_template = "django_twined/question_changeform.html"
    search_fields = ["id", "service_revision__name"]
    list_display = ("id", "asked", "answered", "service_revision")
    list_filter = (
        "asked",
        "service_revision__namespace",
        "service_revision__name",
        "service_revision__tag",
    )
    actions = ["_launch_ask_question"]
    date_hierarchy = "asked"
    readonly_fields = ("id", "asked", "answered")
    fieldsets = (
        question_basic_fieldset,
        # question_db_input_values_fieldset,
        # question_db_output_values_fieldset,
    )

    def ask_question(self, obj):
        """Override this to ask a question using an async task queue or other method. This will ask the question directly."""
        obj.ask()

    def _launch_ask_question(self, request, queryset):
        """Handler method to ask multiple question(s)"""

        ask_count = 0
        for obj in queryset.select_subclasses():
            if obj.asked is not None:
                self.message_user(request, f"{obj!r} already asked - you can't re-ask questions")
            else:
                self.ask_question(obj)
                ask_count += 1

        if ask_count == 1:
            message = "1 question was asked"
        else:
            message = f"{ask_count} questions were asked"
        self.message_user(request, message)

    _launch_ask_question.short_description = "Ask question(s)"

    def _question_is_not_asked(self, obj=None):
        """Return true if question is unasked, otherwise false"""
        if (obj is not None) and (obj.asked is not None):
            return False
        return True

    def has_change_permission(self, request, obj=None):
        """Prevent people from changing questions after they've been asked"""
        return self._question_is_not_asked(obj)

    def has_delete_permission(self, request, obj=None):
        """Prevent people from deleting questions after they've been asked"""
        return self._question_is_not_asked(obj)

    def has_duplicate_permission(self, request, obj=None):
        """Override to prevent people from duplicating questions.
        Defaults to the same as has_add_permission
        """
        return self.has_add_permission(request)

    def render_change_form(self, request, context, *args, obj=None, **kwargs):
        """Override the change form to show question ask options"""

        # If the URL was hit with a ?duplicate=True parameter, then duplicate the object and redirect to edit the new one
        duplicate = request.GET.get("duplicate", False)
        if duplicate:
            duplicate = obj.get_duplicate()
            self.message_user(request, "Duplicated question to new ID, editing the new one")

            return redirect(
                reverse(f"admin:{duplicate._meta.app_label}_{duplicate._meta.model_name}_change", args=[duplicate.id])
            )

        context.update(
            {
                "has_duplicate_permission": self.has_duplicate_permission(request, obj),
                "show_delete": obj is not None and obj.asked is None,
                "show_duplicate": obj is not None and self.has_duplicate_permission(request, obj),
                "show_save": obj is None or obj.asked is None,
                "show_save_and_add_another": False,
                "show_save_and_ask": obj is None or obj.asked is None,
                "show_save_and_continue": False,
            }
        )
        return super().render_change_form(request, context, *args, obj=obj, **kwargs)

    def response_add(self, request, obj, *args, **kwargs):
        """Save the new object then ask the question"""
        response = super().response_add(request, obj, *args, **kwargs)
        if "_save_and_ask" in request.POST:
            self.ask_question(obj.as_subclass())
            self.message_user(request, "1 question was added and asked")
        return response

    def response_change(self, request, obj):
        """Save any edits then ask the question"""
        response = super().response_change(request, obj)
        if "_save_and_ask" in request.POST:
            self.ask_question(obj.as_subclass())
            self.message_user(request, "1 question was saved and asked")
        return response


class ServiceRevisionAdmin(CreatableFieldsMixin, admin.ModelAdmin):
    """Admin panel definition for Service Revisions"""

    search_fields = ["namespace", "name", "tag"]
    list_display = ("namespace", "name", "tag", "created")
    list_filter = ("name", "tag")
    creatable_fields = ("namespace", "name", "tag", "project_name")


class ServiceUsageEventAdmin(admin.ModelAdmin):
    """Admin panel definition for Service Usage Events"""

    search_fields = ["id", "kind", "service_revision__name", "question__id"]
    list_display = ("id", "kind", "publish_time", "service_revision", "question_id")
    date_hierarchy = "publish_time"
    readonly_fields = ("id", "kind", "publish_time", "service_revision", "question")

    def has_add_permission(self, *args, **kwargs):
        """Prevent anyone from editing the event stream"""
        return False

    def has_change_permission(self, *args, **kwargs):
        """Prevent anyone from editing the event stream"""
        return False

    def has_delete_permission(self, *args, **kwargs):
        """Prevent anyone from editing the event stream"""
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("question").prefetch_related("service_revision")

    # TODO consider the additional display options
    #   from jsoneditor.forms import JSONEditor
    #
    #   formfield_overrides = {
    #       JSONField: {"widget": JSONEditor},
    #   }
    #
    #   list_display = ("service_revision__name", "service_revision__tag", "kind", "publish_time", "question")
    #   list_filter = ("service_revision__name", "service_revision__tag", "kind", "publish_time", "question")
    #
    #   @admin.display(ordering="service_revision__name")
    #   def service_revision__name(self, obj):
    #       """Retrieve the name of the related service_revision object"""
    #       return obj.service_revision.name


admin.site.register(Question, QuestionAdmin)
admin.site.register(ServiceRevision, ServiceRevisionAdmin)
admin.site.register(ServiceUsageEvent, ServiceUsageEventAdmin)
