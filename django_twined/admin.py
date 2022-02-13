from django.contrib import admin

from .models import RegisteredService


class RegisteredServiceAdmin(admin.ModelAdmin):
    search_fields = ["id", "name"]
    list_display = ("id", "name")
    readonly_fields = ("id", "name")


admin.site.register(RegisteredService, RegisteredServiceAdmin)
