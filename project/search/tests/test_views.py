from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from blog.models import Post


User = get_user_model()
#from django.contrib.auth.models import User


class ViewTestCase(TestCase):
    def get_user_data(self, num=1):
        return {
            'username': 'username_{}'.format(num),
            'email': 'user{}@example.com'.format(num),
            'password': 'p@ssw0rdUser{}'.format(num),
            'first_name': 'first_name_{}'.format(num),
            'last_name': 'last_name_{}'.format(num),
        }

    def get_post_date(self, num=1, author=None):
        data = {
            'title': 'title_{}'.format(num),
            'slug': 'title_{}'.format(num),
            'body': 'body_{}'.format(num),
            'status': 'published',
        }
        if author:
            data['author'] = author
        return data

    def create_posts(self, author=None, num=1):
        for i in range(num):
            post_data = self.get_post_date(num=i, author=author)
            Post.objects.create(**post_data)

    def setUp(self):
        user_data = self.get_user_data()
        User.objects.create_user(**user_data)
        user_data = self.get_user_data(num=2)
        User.objects.create_user(**user_data)

    def test_post_list(self):
        u1 = self.get_user_data(1)
        u2 = self.get_user_data(2)
        user1 = User.objects.get(username=u1['username'])
        user2 = User.objects.get(username=u2['username'])
        # Create five post by user1
        self.create_posts(author=user1, num=5)
        # Create six post by user2
        self.create_posts(author=user2, num=6)

        path = reverse('search:list')
        resp = self.client.get(path)
        self.assertEqual(resp.status_code, 200)







