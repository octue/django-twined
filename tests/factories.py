import factory


class SuperUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "auth.User"  # Equivalent to ``model = myapp.models.User``
        django_get_or_create = ("username",)
        exclude = ("password",)

    username = "super@user.com"
    is_staff = True
    is_active = True
    is_superuser = True
    password = factory.PostGenerationMethodCall("set_password", "password")
