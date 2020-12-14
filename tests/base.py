import json
import os
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from utils import ensure_in_list


# Test cases are not run over SSL so we must temporarily allow OAuthlib to work over an insecure connection
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"


class AssertationMixin:
    """ Mixin used to add custom self.assertSomething methods to the test cases
    """

    def assertStatusCode(self, response, allowable_status_codes):
        allowable_values = ensure_in_list(allowable_status_codes)
        if response.status_code not in allowable_values:
            print("Failed response was:\n", response)
            print("Response contained the following json:\n", response.json())
            raise self.failureException(
                "Response status code {code} ({reason}) not in list of allowable codes {lst}".format(
                    code=response.status_code, reason=response.reason_phrase, lst=allowable_values
                )
            )

    def assertIsJson(self, response):
        self.assertEqual(response["Content-Type"], "application/json")

    def checkJson(self, response):
        self.assertIsJson(response)
        return json.loads(response.content.decode("utf-8"))


class AuthenticationMixin:
    """ Mixin used to add a range of different authentication methods to the test classes
    """

    def authenticateUsingJwt(self, username="testuser", password="password"):
        """ Adds client credentials using the jwt auth token process, given an email and password
        :param email: email of the user to get the token for
        :param password: password of the user
        :return: none
        """
        # Login as the user using JWT authentication
        payload = {"username": username, "password": password}
        response = self.client.post(
            self.token_obtain_endpoint, data=json.dumps(payload).encode("utf-8"), content_type="application/json"
        )
        self.assertStatusCode(response, 200)
        self.assertIsJson(response)
        self.assertTrue("access" in response.json().keys())
        self.assertTrue("refresh" in response.json().keys())

        # Attach credentials to client to access protected resource
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + response.json()["access"])

        # Return headers
        headers = {"HTTP_AUTHORIZATION": "JWT " + response.json()["access"]}
        return headers

    def authenticateUsingSession(self, username="testuser", password="password"):
        """ Logs in a client using session based authentication
        :param username:
        :param password:
        :return:
        """
        resp = self.client.login(username=username, password=password)
        if not resp:
            raise Exception("unable to log in")
        return resp

    def authenticateUsingToken(self, key=None):
        """ Adds client credentials for either the default test user or using your own key
        :param key: key of an auth token, usually from Token.objects.create(user=a_user_object).key
        :return: none
        """
        if key is None:
            if not hasattr(self, "token") or self.token is None:
                raise Exception(
                    "Call make_test_user in your setup, to store an auth token on self, or pass user.token.key to authenticateToken()"
                )
            key = self.token.key
        self.client.credentials(HTTP_AUTHORIZATION="Token " + key)

    def login(self, username="testuser", password="password"):
        """ Logs in our default test user, or another user specifed by user and password.
        This is a shortcut to session based authentication.
        """
        return self.authenticateUsingSession(username=username, password=password)

    def logout(self):
        """ Logs out the current user
        This is a shortcut to logout the currently authenticated test client
        """
        self.client.logout()


class BaseTestCase(TestCase, AuthenticationMixin, AssertationMixin):
    """A base test case for testing, inherited by all test classes
    """

    def setUp(self):

        # Run the superclass setup (for the db and app context)
        super().setUp()

        # Make a test user, allowing the login and authenticate methods to work
        # The default test user is a superuser; therefore has all the requisite privileges so they don't need to be
        # manually added in unit test cases (NB don't use the default test user for permissions checking)
        self.make_test_user()

        # Set the endpoints for Json Web Tokens
        self.token_obtain_endpoint = reverse("api:auth-token-obtain")
        self.token_refresh_endpoint = reverse("api:auth-token-refresh")
        self.token_verify_endpoint = reverse("api:auth-token-verify")
        self.token_test_endpoint = reverse("api:auth-token-test")

        # Set the path to the test data directory
        self.path = str(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", ""))


class BaseApiTestCase(APITestCase, AuthenticationMixin, AssertationMixin):
    """A base test case for testing a REST api, inherited by all test classes
    """

    def setUp(self):

        # Run the superclass setup (for the db and app context)
        super().setUp()

        # Make a test user, allowing the login and authenticate methods to work
        # The default test user is a superuser; therefore has all the requisite privileges so they don't need to be
        # manually added in unit test cases (NB don't use the default test user for permissions checking)
        self.make_test_user()

        # Set the endpoints for Json Web Tokens
        self.token_obtain_endpoint = reverse("api:auth-token-obtain")
        self.token_refresh_endpoint = reverse("api:auth-token-refresh")
        self.token_verify_endpoint = reverse("api:auth-token-verify")
        self.token_test_endpoint = reverse("api:auth-token-test")

        # Set the path to the test data directory
        self.path = str(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", ""))


# Settings dict to remove permissioning and object level filtering from the API. Useful for testing functionality
# without integrating permissions into test cases
REST_FRAMEWORK_ALLOW_ANY = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": (),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 100,
}
