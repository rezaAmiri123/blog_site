from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from account.api import views
from ..models import Profile, Contact
from django.contrib.auth import get_user_model

User = get_user_model()


class UserTestCaseAPI(APITestCase):
    def get_user_data(self, num=1):
        return {
            'username': 'username_{}'.format(num),
            'email': 'user{}@example.com'.format(num),
            'password': 'p@ssw0rdUser{}'.format(num),
            'first_name': 'first_name_{}'.format(num),
            'last_name': 'last_name_{}'.format(num),
        }

    def login(self, user=None):
        if not user:
            user = self.get_user_data()
        data = {
            'username': user['username'],
            'password': user['password'],
        }
        return self.client.login(**data)

    def setUp(self):
        user_data = self.get_user_data()
        User.objects.create_user(**user_data)

    def test_register_valid(self):
        u2 = self.get_user_data(2)
        path = reverse('api_register_user')
        resp = self.client.post(path, data=u2, format='json')
        self.assertEqual(resp.status_code, 201)

    def test_register_invalid(self):
        u2 = self.get_user_data(2)
        path = reverse('api_register_user')
        del u2['password']
        resp = self.client.post(path, data=u2, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_list(self):
        self.login()
        u1 = self.get_user_data()
        path = reverse('api_list_user')
        resp = self.client.get(path)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['results'][0]['username'], u1['username'])

    def test_user_detail(self):
        self.login()
        u1 = self.get_user_data()
        path = reverse('api_retrieve_update_user', args=[1])
        resp = self.client.get(path)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['username'], u1['username'])
        u1['first_name'] += '_changed'
        resp = self.client.patch(path,
                                 data={'first_name': u1['first_name']},
                                 format='json')
        self.assertEqual(resp.data['first_name'], u1['first_name'])
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_user_follow(self):
        self.login()
        u1 = self.get_user_data()
        u2 = self.get_user_data(2)
        User.objects.create_user(**u2)
        user2 = User.objects.get(username=u2['username'])

        path = reverse('api_user_follow')
        data = {
            'id': user2.id,
            'action': 'follow'
        }
        # user1 is following user2
        resp = self.client.post(path, data, format='json')
        self.assertEqual(resp.status_code, 200)
        user1 = User.objects.get(username=u1['username'])
        self.assertEqual(user2.followers.count(), 1)
        self.assertEqual(user1.followers.count(), 0)
        self.assertEqual(user2.following.count(), 0)
        self.assertEqual(user1.following.count(), 1)

        follow_data = Contact.objects.get(user_from=user1,
                                          user_to=user2)
        text = '{} follow {}'.format(user1.username, user2.username)
        self.assertEqual(follow_data.__str__(), text)

        # having a test that user1 is unfollowing user2
        data = {
            'id': user2.id,
            'action': 'unfollow'
        }
        resp = self.client.post(path, data, format='json')

        self.assertContains(resp, 'ok')
        self.assertEqual(user2.followers.count(), 0)
        self.assertEqual(user1.followers.count(), 0)
        self.assertEqual(user2.following.count(), 0)
        self.assertEqual(user1.following.count(), 0)

    def test_user_follow_invalid(self):
        self.login()
        u1 = self.get_user_data()
        u2 = self.get_user_data(2)
        User.objects.create_user(**u2)
        user2 = User.objects.get(username=u2['username'])

        path = reverse('api_user_follow')
        data = {
            'id': user2.id + 999999, # invalid user
            'action': 'follow'
        }
        # this object won't be found in database
        resp = self.client.post(path, data, format='json')
        self.assertEqual(resp.data['status'], 'ko')

        data = {
            'id': user2.id,
            # 'action': 'follow' # this object must be used in data
        }
        # this object won't be processed
        resp = self.client.post(path, data=data, format='json')
        self.assertEqual(resp.data['status'], 'ko')


