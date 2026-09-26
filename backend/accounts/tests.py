from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from organizations.models import Organization

User = get_user_model()

class AccountsAuthTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.org = Organization.objects.create(name="Acme Analytics")
        self.user = User.objects.create_user(
            email="analyst@acme.com",
            name="Alice Analyst",
            password="SecurePassword123!",
            organization=self.org,
            role="owner"
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, "analyst@acme.com")
        self.assertEqual(self.user.organization.name, "Acme Analytics")
        self.assertTrue(self.user.check_password("SecurePassword123!"))

    def test_login_api(self):
        response = self.client.post("/api/auth/login/", {
            "email": "analyst@acme.com",
            "password": "SecurePassword123!"
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])

    def test_register_api(self):
        response = self.client.post("/api/auth/register/", {
            "name": "Bob Builder",
            "email": "bob@builder.io",
            "password": "BuilderSecret2026!",
            "organization_name": "Builder Org"
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], "bob@builder.io")
