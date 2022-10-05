from django.contrib import admin


def register_proxy_modeladmin(modeladmin, model, name=None):
    """Registers a modeladmin entry using a proxy model class

    This allows multiple modeladmins to be registered to the same
    model class, meaning you can have different modeladmins for the
    same things.

    Based on https://stackoverflow.com/a/2228821/3556110
    """

    class Meta:
        """Define a metaclass used to construct a proxy model"""

        proxy = True
        app_label = model._meta.app_label

    attrs = {"__module__": "", "Meta": Meta}

    newmodel = type(name, (model,), attrs)

    admin.site.register(newmodel, modeladmin)

    return modeladmin
