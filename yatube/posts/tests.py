from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse

from .models import Follow, Group, Post, User


class UserTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="test_user", email="connor.s@skynet.com", password="12345"
        )
        self.post = Post.objects.create(
            text="Yes!",
            author=self.user, pub_date='10.02.2020')

    def test_mail(self):
        self.client.post('/auth/signup/', {'username': 'ruby', 'password1': 'ruby228322',
                                           'password2': 'ruby228322', 'email': 'test@test.me'})
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Подтверждение регистрации Yatube')

    def test_user_sign_in(self):
        username = 'ruby'
        self.client.post('/auth/signup/', {'username': username, 'password1': 'ruby228322', 'password2': 'ruby228322'})
        response = self.client.get(reverse('profile', args=[username]))
        self.assertEqual(response.status_code, 200)

    def test_post_accept(self):
        self.client.login(username='test_user', password='12345')
        with open('v.png', 'rb') as fp:
            self.client.post(reverse('new_post'), {'text': 'rubycobra', 'image': fp})
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
        with open('v.png', 'rb') as fp:
            self.client.post(reverse('post_edit', args=['test_user', self.post.pk]), {"text": text, "image": fp})
        response = self.client.get(reverse('profile', args=['test_user']))
        self.assertContains(response, text)
        response = self.client.get(reverse('index'))
        self.assertContains(response, text)
        response = self.client.get(reverse('post', args=['test_user', self.post.pk]))
        self.assertContains(response, text)

    def test_post_with_image_display(self):
        self.client.login(username='test_user', password='12345')
        with open('v.png', 'rb') as fp:
            self.client.post(reverse('new_post'), {'text': 'rubycobra', 'image': fp})
        post_id = Post.objects.get(text='rubycobra').pk
        response = self.client.get(reverse('post', args=['test_user', post_id]))
        self.assertContains(response, '<img ', status_code=200)

    def test_image_display(self):
        self.client.login(username='test_user', password='12345')
        group = Group.objects.create(
            title='Своя игра',
            slug='game',
            description='своя игра'
        )
        with open('v.png', 'rb') as fp:
            self.client.post(reverse('new_post'), {'text': 'rubycobra', 'image': fp})
        response = self.client.get(reverse('index'))
        self.assertContains(response, '<img ', status_code=200)
        response = self.client.get(reverse('profile', args=['test_user']))
        self.assertContains(response, '<img ', status_code=200)

    def post_image_is_valid(self):
        with open('f.txt', 'rb') as fp:
            response = self.client.post(reverse('new_post'), {'text': 'rubycobra', 'image': fp})
        self.assertFormError(response, 'form', 'image', 'Загрузите правильное изображение. Файл, который вы загрузили, '
                                                        'поврежден или не является изображением.')

    def test_follow(self):
        self.client.post('/auth/signup/', {'username': 'ruby', 'password1': 'ruby228322', 'password2': 'ruby228322'})
        self.client.login(username="test_user", password="12345")
        u = User.objects.get(username="test_user")
        self.client.post(reverse('profile_follow', args=['ruby']))
        follow_count = Follow.objects.filter(user=u).count()
        self.assertEqual(follow_count, 1)
        self.client.post(reverse("profile_unfollow", args=['ruby']))
        u = User.objects.get(username="ruby")
        unfollow_count = Follow.objects.filter(author=u).count()
        self.assertEqual(unfollow_count, 0)

    def test_follow_posts(self):
        self.client.post('/auth/signup/', {'username': 'ruby', 'password1': 'ruby228322', 'password2': 'ruby228322'})
        self.client.login(username='ruby', password='ruby228322')
        with open('v.png', 'rb') as fp:
            self.client.post(reverse('new_post'), {'text': 'rubycobra', 'image': fp})
        self.client.post('/auth/signup/', {'username': 'ruby1', 'password1': 'ruby228322', 'password2': 'ruby228322'})
        self.client.login(username="test_user", password="12345")
        self.client.post(reverse('profile_follow', args=['ruby']))
        response = self.client.get(reverse('follow_index'))
        self.assertContains(response, 'rubycobra')
        self.client.login(username='ruby1', password='ruby228322')
        response = self.client.get(reverse('follow_index'))
        self.assertNotContains(response, 'rubycobra')

    def test_comments(self):
        self.client.login(username='test_user', password='12345')
        post_id = Post.objects.get(text='Yes!').pk
        self.client.logout()
        response = self.client.post(reverse('add_comment', args=['test_user', post_id]), {'text': 'Yes!'})
        self.assertRedirects(response, '/auth/login/?next=/test_user/1/comment')
        self.client.login(username='test_user', password='12345')
        self.client.post(reverse('add_comment', args=['test_user', post_id]), {'text': 'Yes!'})
        response = self.client.get(reverse('post', args=['test_user', post_id]))
        self.assertContains(response, 'Yes!')
