from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from django.urls import reverse 
from rest_framework import status
from rest_framework_simplejwt.tokens import  AccessToken

# from accounts.models import User
User = get_user_model()


class AccountRegistrationTestCase(APITestCase):
    def test_account_registration(self):
        url = '/api/users'
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
        url = '/api/users'
        invalid_user_data = {
            'user': { }
        }

        response = self.client.post(url, invalid_user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_account_registration(self):
        # First registration
        url = '/api/users'
        user_data = {
            'user': {
                'email': 'test@example.com',
                'password': 'testpassword',
                'username': 'testuser',
            }
        }

        response = self.client.post(url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Duplicate registration
        duplicate_response = self.client.post(url, user_data, format='json')
        self.assertEqual(duplicate_response.status_code, status.HTTP_400_BAD_REQUEST)

   
    

    def test_account_login_invalid_password(self):
        user_data = {
            'user': {
                'email': self.email,
                'password': 'wrongpassword',
            }
        }

        response = self.client.post(self.url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_account_login_invalid_email(self):
        user_data = {
            'user': {
                'email': 'invalid@example.com',
                'password': self.password,
            }
        }

        response = self.client.post(self.url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout(self):
        logout_url = '/api/users/logout'
        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    
        
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
            HTTP_AUTHORIZATION='Token ' + self.access_token
        )
        self.url = reverse('user-account')
        

    def test_user_view_get(self):
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  
        
        
    def test_user_view_put(self):
        updated_email = 'updated@example.com'
        updated_bio = 'Updated bio'
        updated_image = 'http://example.com/updated-image.jpg'
        user_data = {
            'user': {
                'email': updated_email,
                'bio': updated_bio,
                'image': updated_image,
            }
        }

        response = self.client.put(self.url, user_data, format='json')

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
            HTTP_AUTHORIZATION='Token ' + self.access_token
        )
        self.url = f'/api/profiles/{self.user.username}'

    def test_profile_detail_view_get(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK) 
        
    
    def test_profile_detail_view_follow(self):
        second_user = User.objects.create_user(
            email='test2@gmail.com',
            username='test2user',
            password='password'
        )
        follow_url = f'/api/profiles/{second_user.username}/follow'

        response = self.client.post(follow_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_detail_view_unfollow(self):
        second_user = User.objects.create_user(
            email='test2@gmail.com',
            username='test2user',
            password='password'
        )
        second_user.followers.add(self.user)
        unfollow_url = f'/api/profiles/{second_user.username}/follow'

        response = self.client.delete(unfollow_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
     def test_profile_detail_view_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'invalidtoken')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_profile_detail_view_no_token(self):
        self.client.credentials()  # Unset the token
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_follow_invalid_token(self):
        second_user = User.objects.create_user(
            email='test2@gmail.com',
            username='test2user',
            password='password'
        )
        follow_url = f'/api/profiles/{second_user.username}/follow'
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'invalidtoken')
        response = self.client.post(follow_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)