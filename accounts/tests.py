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

        response = self.client.post(self.url, invalid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserViewTestCase(APITestCase):
    def setUp(self):
        self.email = 'test@example.com'
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(
            email=self.email,
            username=self.username,
            password=self.password
        )
        self.access_token = str(AccessToken.for_user(self.user))
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.access_token
        )
        self.url = reverse('user-account')  # Assuming a named URL for user account

    def test_user_view_get(self):
        """
        Test retrieving the user account details
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_view_put(self):
        """
        Test updating the user account details
        """
        updated_user_data = {
            'user': {
                'email': 'updated@example.com',
                'bio': 'Updated bio',
                'image': 'http://example.com/updated-image.jpg',
            }
        }

        response = self.client.put(self.url, updated_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


        self.assertEqual(response.status_code, status.HTTP_200_OK)  
    
    def test_user_view_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'invalidtoken')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        
class ProfileDetailViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpassword'
        )
        self.access_token = str(AccessToken.for_user(self.user))
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.access_token
        )
        self.url = reverse('profile-detail', kwargs={'username': self.user.username})

    def test_profile_detail_view_get(self):
        """
        Test retrieving profile details
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_detail_view_follow(self):
        """
        Test following a user
        """
        second_user = User.objects.create_user(
            email='test2@gmail.com',
            username='test2user',
            password='password'
        )
        follow_url = reverse('profile-follow', kwargs={'username': second_user.username})

        response = self.client.post(follow_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_detail_view_unfollow(self):
        """
        Test unfollowing a user
        """
        second_user = User.objects.create_user(
            email='test2@gmail.com',
            username='test2user',
            password='password'
        )
        second_user.followers.add(self.user)  # Assume the existence of a 'followers' ManyToMany field
        unfollow_url = reverse('profile-follow', kwargs={'username': second_user.username})

        response = self.client.delete(unfollow_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
