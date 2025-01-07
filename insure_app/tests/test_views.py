# will run the test for views 

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class RegisterViewTests(TestCase):
    def setUp(self):
        self.register_url = reverse("register")

    def test_registration_success(self):
        response = self.client.post(self.register_url, {
            "username": "newuser",
            "password1": "password123",
            "password2": "password123",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_registration_password_mismatch(self):
        response = self.client.post(self.register_url, {
            "username": "newuser",
            "password1": "password123",
            "password2": "wrongpassword",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())


class LoginViewTests(TestCase):
    def setUp(self):
        self.login_url = reverse("login")
        self.user = User.objects.create_user(username="testuser", password="password123")

    def test_login_success(self):
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "password123",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_failure(self):
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "wrongpassword",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

