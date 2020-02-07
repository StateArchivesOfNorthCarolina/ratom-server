from django.urls import reverse
from rest_framework.test import APITestCase


class ProtectedRouteTestCase(APITestCase):
    """
    Requests to views decorated with @permission_classes([IsAuthenticated])
    should return 401s if unauthenticated
    """

    def setUp(self):
        self.no_credentials_msg = "Authentication credentials were not provided."
        self.bad_credentials_msg = "Token is invalid or expired"

    def test_user_detail_without_credentials(self):
        """
        user_detail view returns 401 to unauthenticated request
        with '...credentials were not provided' message.
        """
        response = self.client.get(reverse("user_detail"))
        self.assertEqual(response.status_code, 401)
        self.assertIn(self.no_credentials_msg, str(response.content))

    def test_user_detail_bad_credentials(self):
        """
        user_detail view returns 401 to unauthenticated request
        with 'Token is invalid or expired' message.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Bearer fake.auth.token")
        response = self.client.get(reverse("user_detail"))
        self.assertEqual(response.status_code, 401)
        self.assertIn(self.bad_credentials_msg, str(response.content))

    def test_account_list_without_credentials(self):
        """
        account_list view retuns 401 to requests without Auth headers
        with '...credentials were not provided' message.
        """
        response = self.client.get(reverse("account_list"))
        self.assertEqual(response.status_code, 401)
        self.assertIn(self.no_credentials_msg, str(response.content))

    def test_account_list_bad_credentials(self):
        """
        account_list view returns 401 to requests with bad token
        with 'Token is invalid or expired' message.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Bearer fake.auth.token")
        response = self.client.get(reverse("account_list"))
        self.assertEqual(response.status_code, 401)
        self.assertIn(self.bad_credentials_msg, str(response.content))

    def test_account_detail_without_credentials(self):
        """
        account_detail view retuns 401 to requests without Auth headers
        with '...credentials were not provided' message.
        """
        response = self.client.get(reverse("account_detail", kwargs={"pk": "1"}))
        self.assertEqual(response.status_code, 401)
        self.assertIn(self.no_credentials_msg, str(response.content))

    def test_account_detail_bad_credentials(self):
        """
        account_detail view returns 401 to requests with bad token
        with 'Token is invalid or expired' message.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Bearer fake.auth.token")
        response = self.client.get(reverse("account_detail", kwargs={"pk": "1"}))
        self.assertEqual(response.status_code, 401)
        self.assertIn(self.bad_credentials_msg, str(response.content))

    def test_search_messages_without_credentials(self):
        """
        search_messages view retuns 401 to requests without Auth headers
        with '...credentials were not provided' message.
        """
        response = self.client.get(reverse("search_messages"))
        self.assertEqual(response.status_code, 401)
        self.assertIn(self.no_credentials_msg, str(response.content))

    def test_search_messages_bad_credentials(self):
        """
        search_messages view returns 401 to requests with bad token
        with 'Token is invalid or expired' message.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Bearer fake.auth.token")
        response = self.client.get(reverse("search_messages"))
        self.assertEqual(response.status_code, 401)
        self.assertIn(self.bad_credentials_msg, str(response.content))

    def test_message_detail_without_credentials(self):
        """
        message_detail view retuns 401 to requests without Auth headers
        with '...credentials were not provided' message.
        """
        response = self.client.get(reverse("message_detail", kwargs={"pk": "1"}))
        self.assertEqual(response.status_code, 401)
        self.assertIn(self.no_credentials_msg, str(response.content))

    def test_message_detail_bad_credentials(self):
        """
        message_detail view returns 401 to requests with bad token
        with 'Token is invalid or expired' message.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Bearer fake.auth.token")
        response = self.client.get(reverse("message_detail", kwargs={"pk": "1"}))
        self.assertEqual(response.status_code, 401)
        self.assertIn(self.bad_credentials_msg, str(response.content))

    def test_message_search_bad_credentials(self):
        """
        message_search view returns 401 when bad token is provided
        with 'Token is invalid or expired' message.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Bearer fake.auth.token")
        response = self.client.get(reverse("search_messages"))
        self.assertEqual(response.status_code, 401)
        self.assertIn(self.bad_credentials_msg, str(response.content))
