from django.test import TestCase
from django.contrib.auth import get_user_model
from ..forms import UserRegistrationForm

User = get_user_model()


class FormTest(TestCase):
    def get_model_data(self, num=1):
        return {
            'username': 'username_{}'.format(num),
            'email': 'user{}@example.com'.format(num),
            'password': 'p@ssw0rdUser{}'.format(num),
            'first_name': 'first_name_{}'.format(num),
            'last_name': 'last_name_{}'.format(num),
        }

    def test_valid_register_form(self):
        user1_data = self.get_model_data()
        user1_data['password2'] = user1_data['password']
        form = UserRegistrationForm(data=user1_data)
        self.assertTrue(form.is_valid())

    def test_invalid_register_form(self):
        user1_data = self.get_model_data()
        user1_data['password2'] = user1_data['password'] + 'wrong'
        form = UserRegistrationForm(data=user1_data)
        self.assertFalse(form.is_valid())
