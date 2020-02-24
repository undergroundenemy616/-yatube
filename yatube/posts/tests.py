from django.test import TestCase, Client
from .models import User, Post
from django.urls import reverse
from django.core import mail


class UserTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="test_user", email="connor.s@skynet.com", password="12345"
        )
        self.post = Post.objects.create(
            text="You're talking about things I haven't done yet in the past tense. It's driving me crazy!",
            author=self.user, pub_date='10.02.2020')

    def test_mail(self):
        # Не понял, что конкретно хотят
        pass

    def test_user_sign_in(self):
        username = 'ruby'
        self.client.post('/auth/signup/', {'username': username, 'password1': 'ruby228322', 'password2': 'ruby228322'})
        response = self.client.get(reverse('profile', args=[username]))
        self.assertEqual(response.status_code, 200)

    def test_post_accept(self):
        self.client.login(username='test_user', password='12345')
        self.client.post(reverse('new_post'), {'text': 'rubycobra'})
        post_id = Post.objects.get(text='rubycobra').pk
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'rubycobra')
        response = self.client.get(reverse('profile', args=['test_user']))
        self.assertContains(response, 'rubycobra')
        response = self.client.get(reverse('post', args=['test_user', post_id]))
        self.assertContains(response, 'rubycobra')

    def test_post_redirect(self):
        response = self.client.get(reverse('new_post'))
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_post_edit(self):
        self.client.login(username="test_user", password="12345")
        text = "YES"
        self.client.post(reverse('post_edit', args=['test_user', self.post.pk]), {"text": text})
        response = self.client.get(reverse('profile', args=['test_user']))
        self.assertContains(response, text)
        response = self.client.get(reverse('index'))
        self.assertContains(response, text)
        response = self.client.get(reverse('post', args=['test_user', self.post.pk]))
        self.assertContains(response, text)




