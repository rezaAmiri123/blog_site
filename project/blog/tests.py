from django.test import TestCase
from .models import User, Post, Comment


class ModelTest(TestCase):
    def setUp(self):
        User.objects.create(username='user_1', password='password_1', email='user_1@example.com')

    def get_model_date_post(self, num=1):
        post = {
            'title': 'post title {}'.format(num),
            'body': 'post body text {}'.format(num),

        }
        return post

    def get_model_data_comment(self, num=1):
        comment = {
            'name': 'comment name {}'.format(num),
            'email': 'comment{}@example.com'.format(num),
            'body': 'comment body {}'.format(num),
        }
        return comment

    def test_post_model(self):
        user = User.objects.first()
        post = self.get_model_date_post()
        post['author'] = user
        Post.objects.create(**post)
        recv_post = Post.objects.get(title=self.get_model_date_post()['title'])

        self.assertEqual(recv_post.author, user)
        self.assertEqual(recv_post.body, self.get_model_date_post()['body'])

    def test_comment_model(self):
        user = User.objects.first()
        post = self.get_model_date_post()
        post['author'] = user
        Post.objects.create(**post)
        recv_post = Post.objects.get(title=self.get_model_date_post()['title'])

        comment = self.get_model_data_comment()
        comment['post'] = recv_post
        Comment.objects.create(**comment)
        recv_comment = Comment.objects.get(name=self.get_model_data_comment()['name'])

        self.assertEqual(recv_comment.post, recv_post)
        self.assertEqual(recv_comment.body, self.get_model_data_comment()['body'])

