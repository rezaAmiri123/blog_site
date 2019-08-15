from django.test import TestCase
from ..models import User, Contact, Profile
from django.utils import timezone
from django.urls import reverse
from ..forms import ProfileEditForm, LoginForm, UserEditForm, UserRegistrationForm


class UserTest(TestCase):

    def get_model_data(self, num=1):
        return {
            'username': 'username_{}'.format(num),
            'email': 'user{}@example.com'.format(num),
            'password': 'p@ssw0rdUser{}'.format(num),
            'first_name': 'first_name_{}'.format(num),
            'last_name': 'last_name_{}'.format(num),
        }

    def setUp(self):
        user1 = self.get_model_data(1)
        User.objects.create(**user1)

    def test_user_create(self):
        user1_data = self.get_model_data(1)
        user1 = User.objects.get(pk=1)
        self.assertTrue(isinstance(user1, User))
        self.assertEqual(user1.id, 1)
        self.assertEqual(user1.username, user1_data['username'])

    # profile is create when a user is creating
    def test_profile(self):
        user1 = User.objects.get(id=1)
        self.assertTrue(isinstance(user1.profile, Profile))
        self.assertEqual(str(user1.profile), 'Profile for user {}'.format(user1.username))
