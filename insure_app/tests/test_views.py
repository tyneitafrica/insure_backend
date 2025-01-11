# will run the test for views 

from django.test import TestCase
from django.urls import reverse
from insure.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.conf import settings

class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("signup user")
        self.valid_api_key = settings.API_KEY
        print(self.valid_api_key)


        self.valid_user_data = {
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "strongpassword",
        }

        self.invalid_user_data = {
            "email": "",
            "first_name": "",
            "last_name": "",
            "password": "",
        }

        self.headers = {"x-api-key": self.valid_api_key}
        print(self.headers)

    def test_register_user_with_valid_data(self):
        response = self.client.post(
            self.register_url, data=self.valid_user_data, **self.headers
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role"], "APPLICANT")
        self.assertEqual(response.data["email"], self.valid_user_data["email"])
        self.assertIn("id", response.data)

    # def test_register_user_missing_api_key(self):
    #     response = self.client.post(self.register_url, data=self.valid_user_data)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.assertIn("error", response.data)

    # def test_register_user_with_invalid_data(self):
    #     response = self.client.post(
    #         self.register_url, data=self.invalid_user_data, **self.headers
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn("error", response.data)

    # def test_user_default_role_is_applicant(self):
    #     response = self.client.post(
    #         self.register_url, data=self.valid_user_data, **self.headers
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(response.data["role"], "applicant")

    # def test_register_user_with_invalid_api_key(self):
    #     headers = {"x-api-key": "invalid_key"}
    #     response = self.client.post(
    #         self.register_url, data=self.valid_user_data, **headers
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.assertIn("Invalid API key", response.data["error"])


