from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from django.urls import reverse 
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

class AccountRegistrationTestCase(APITestCase):
    def test_account_registration(self):
        """
        Test successful account registration
        """
        url = reverse('account-register')  # Assuming you have a named URL pattern
        user_data = {
            'user': {
                'email': 'test@example.com',
                'password': 'testpassword',
                'username': 'testuser',
            }
        }

        response = self.client.post(url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_account_registration_invalid_data(self):
        """
        Test registration with invalid data
        """
        url = reverse('account-register')
        invalid_user_data = {
            'user': {}
        }

        response = self.client.post(url, invalid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AccountLoginTestCase(APITestCase):
    def setUp(self):
        self.email = 'test@example.com'
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(
            email=self.email,
            username=self.username,
            password=self.password
        )
        self.url = reverse('account-login')  # Assuming a named URL pattern for login

    def tearDown(self):
        self.user.delete()

    def test_account_login(self):
        """
        Test successful login with valid credentials
        """
        user_data = {
            'user': {
                'email': self.email,
                'password': self.password,
            }
        }

        response = self.client.post(self.url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_account_login_invalid_data(self):
        """
        Test login with invalid data
        """
        invalid_user_data = {
            'user': {}
        }

        response = self.client.post(self.url, invalid
