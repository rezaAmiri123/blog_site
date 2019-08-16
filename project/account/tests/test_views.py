import base64
import json
from django.test import TestCase, Client
from .. import views
from ..models import Contact
from django.urls import reverse
from selenium import webdriver
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class ViewTest(TestCase):
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
        self.client.login(**data)

    def setUp(self):
        user_data = self.get_user_data()
        User.objects.create_user(**user_data)

    def test_register_user(self):
        path = reverse('register')
        resp = self.client.get(path)
        self.assertContains(resp, 'Email')

        user2_data = self.get_user_data(2)
        user2_data['password2'] = user2_data['password']

        resp = self.client.post(path, user2_data)
        self.assertEqual(resp.status_code, 200)
        user2 = User.objects.filter(username=user2_data['username']).first()
        self.assertEqual(user2.username, user2_data['username'])

    def test_user_valid_edit(self):
        self.login()
        path = reverse('edit')
        resp = self.client.get(path)
        self.assertContains(resp, 'Email')

        user_data = self.get_user_data()
        user1 = User.objects.get(username=user_data['username'])

        self.assertEqual(user1.last_name, user_data['last_name'])
        user_data_changed = self.get_user_data()
        user_data_changed['last_name'] += 'hi'
        resp = self.client.post(path, user_data_changed)

        user1 = User.objects.get(username=user_data['username'])
        self.assertEqual(user1.last_name, user_data_changed['last_name'])

    def test_user_invalid_edit(self):
        user_data = self.get_user_data()
        user1 = User.objects.get(username=user_data['username'])
        self.login()

        path = reverse('edit')
        user_data_changed = self.get_user_data()
        user_data_changed['email'] = 'invalid email'
        resp = self.client.post(path, user_data_changed)
        self.assertContains(resp, 'Error updating your profile')

    def test_user_list(self):
        path = reverse('user_list')
        self.login()
        u = self.get_user_data()
        user = User.objects.get(username=u['username'])
        text = '{} {}'.format(user.first_name, user.last_name)
        resp = self.client.get(path)
        self.assertContains(resp, text)

    def test_user_detail(self):
        self.login()
        u = self.get_user_data()
        user = User.objects.get(username=u['username'])
        text = '{} {}'.format(user.first_name, user.last_name)
        path = reverse('user_detail', args=[user.username])
        resp = self.client.get(path)
        self.assertContains(resp, text)

    def test_user_follow(self):
        self.login()
        path = reverse('user_follow')
        # create user
        u2 = self.get_user_data(2)
        User.objects.create_user(**u2)
        user2 = User.objects.get(username=u2['username'])
        u1 = self.get_user_data()
        user1 = User.objects.get(username=u1['username'])
        # having a test that user1 is following user2
        data = {
            'id': user2.id,
            'action': 'follow'
        }
        resp = self.client.post(path, data=data,
                                format='json',
                                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertContains(resp, 'ok')
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
        resp = self.client.post(path, data=data,
                                format='json',
                                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertContains(resp, 'ok')
        self.assertEqual(user2.followers.count(), 0)
        self.assertEqual(user1.followers.count(), 0)
        self.assertEqual(user2.following.count(), 0)
        self.assertEqual(user1.following.count(), 0)

    def test_user_invalid_follow(self):
        self.login()
        path = reverse('user_follow')
        # create user
        u2 = self.get_user_data(2)
        User.objects.create_user(**u2)
        user2 = User.objects.get(username=u2['username'])
        u1 = self.get_user_data()
        user1 = User.objects.get(username=u1['username'])
        # having a test that user1 is following user2
        data = {
            'id': user2.id + 999999,  # invalid id
            'action': 'follow'
        }
        # this object won't be found in database
        resp = self.client.post(path, data=data,
                                format='json',
                                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertContains(resp, 'ko')

        data = {
            'id': user2.id,
            # 'action': 'follow' # this object must be used in data
        }
        # this object won't be processed
        resp = self.client.post(path, data=data,
                                format='json',
                                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertContains(resp, 'ko')

    def test_authentication_with_email(self):
        u1 = self.get_user_data()
        username = u1['email']
        password = u1['password']
        login = self.client.login(username=username, password=password)
        self.assertTrue(login)
        path = reverse('user_list')
        resp = self.client.get(path)

    def test_authentication_failed_with_email(self):
        u1 = self.get_user_data()
        # with wrong email
        username = u1['email'] + '.wrong'
        password = u1['password']
        login = self.client.login(username=username, password=password)
        self.assertFalse(login)

        # with wrong password
        username = u1['email']
        password = u1['password'] + 'wrong'
        login = self.client.login(username=username, password=password)
        self.assertFalse(login)


"""
class ViewSeleniumTest(TestCase):

    def get_user_data(self, num=1):
        return {
            'username': 'username_{}'.format(num),
            'email': 'user{}@example.com'.format(num),
            'password': 'p@ssw0rdUser{}'.format(num),
            'first_name': 'first_name_{}'.format(num),
            'last_name': 'last_name_{}'.format(num),
        }

    def setUp(self):
        self.driver = webdriver.Firefox()
        self.path = 'http://localhost:8000'
        self.sleep = 1

    def login(self, num=1):
        u = self.get_user_data(num=num)
        path = self.path + reverse('login')
        self.driver.get(path)
        time.sleep(self.sleep)
        self.driver.find_element_by_id('id_username').send_keys(u['username'])
        self.driver.find_element_by_id('id_password').send_keys(u['password'])
        self.driver.find_element_by_tag_name('form').submit()
        time.sleep(self.sleep)
        self.driver.find_element_by_tag_name('body')

    def logout(self):
        path = self.path + reverse('logout')
        self.driver.get(path)
        time.sleep(self.sleep)

    def test_01_register_user(self):
        u = self.get_user_data()
        url = self.path + reverse('register')
        self.driver.get(url=url)
        time.sleep(self.sleep)
        self.driver.find_element_by_id('id_username').send_keys(u['username'])
        self.driver.find_element_by_id('id_first_name').send_keys(u['first_name'])
        # self.driver.find_element_by_id('id_last_name').send_keys(u['last_name'])
        self.driver.find_element_by_id('id_email').send_keys(u['email'])
        self.driver.find_element_by_id('id_password').send_keys(u['password'])
        self.driver.find_element_by_id('id_password2').send_keys(u['password'])
        self.driver.find_element_by_tag_name('form').submit()
        time.sleep(self.sleep)

        # create user 2
        u = self.get_user_data(num=2)
        self.driver.get(url=url)
        time.sleep(self.sleep)
        self.driver.find_element_by_id('id_username').send_keys(u['username'])
        self.driver.find_element_by_id('id_first_name').send_keys(u['first_name'])
        # self.driver.find_element_by_id('id_last_name').send_keys(u['last_name'])
        self.driver.find_element_by_id('id_email').send_keys(u['email'])
        self.driver.find_element_by_id('id_password').send_keys(u['password'])
        self.driver.find_element_by_id('id_password2').send_keys(u['password'])
        self.driver.find_element_by_tag_name('form').submit()
        time.sleep(self.sleep)

        # self.login()
        # self.logout()

    def test_02_edit_profile(self):
        self.login()
        path = self.path + reverse('edit')
        self.driver.get(path)
        time.sleep(self.sleep)
        u = self.get_user_data()
        last_name = self.driver.find_element_by_id('id_last_name').text
        self.assertEqual(last_name, '')
        self.driver.find_element_by_id('id_last_name').send_keys(u['last_name'])
        self.driver.find_element_by_tag_name('form').submit()
        time.sleep(self.sleep)

        self.driver.get(path)
        time.sleep(self.sleep)
        # last_name = self.driver.find_element_by_id('id_last_name').text
        # self.assertEqual(last_name, u['last_name'])
        self.logout()

    def test_03_user_list(self):
        self.login()
        path = self.path + reverse('user_list')
        self.driver.get(path)
        time.sleep(self.sleep)
        u = self.get_user_data()
        user_data = u['first_name'] + ' ' + u['last_name']
        text = self.driver.find_element_by_link_text(user_data).text
        # self.assertEqual(user_data, text + 'hi')
        self.logout()

    def test_04_user_follow(self):
        self.login()



    def test_99_delete_user(self):
        url = self.path + reverse('delete_test_user')
        # insert user num
        url += '?num=1'
        # resp = self.client.get(url)
        self.driver.get(url=url)
        time.sleep(self.sleep)
        # print(resp.status_code)

    def tearDown(self):
        self.driver.quit()

"""
