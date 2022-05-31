class CreatableFieldsMixin:
    """A mixin allowing specification of admin fields that are editable on create but not on change."""

    creatable_fields = tuple()

    # def get_fields(self, request, obj=None):
    #     """Override readonly_fields to add creatable_fields in the case of object update, but not in the case of object creation"""
    #     defaults = super().get_fields(request, obj=obj)
    #     return tuple(defaults) + self.creatable_fields

    def get_readonly_fields(self, request, obj=None):
        """Override readonly_fields to add creatable_fields in the case of object update, but not in the case of object creation"""
        defaults = super().get_readonly_fields(request, obj=obj)
        if obj:  # if we are updating an object
            defaults = tuple(defaults) + self.creatable_fields  # make sure defaults is a tuple
        return defaults
