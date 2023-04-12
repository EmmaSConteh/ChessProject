""" Unit tests of Sign up view """

from django.test import TestCase
from django.contrib.auth.hashers import check_password

from django.urls import reverse

from clubs.models import User
from clubs.forms import SignUpForm
from clubs.tests.helpers import LogInTester

class SignUpViewTestCase(TestCase, LogInTester):
    def setUp(self):
        self.url = reverse('sign_up')
        self.form_input = {
            'name' : 'Johnny',
            'email' : 'john@example.org',
            'bio' : 'A certain someone playing games',
            'chess_experience': 'A',
            'personal_statement': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut.',
            'new_password' : '123QWErty',
            'password_confirmation': '123QWErty'
        }

    def test_signup_url(self):
        self.assertEqual(self.url, '/sign_up/')

    def test_get_sign_up(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertFalse(form.is_bound)

    def test_unsuccessfull_signup(self):
        self.form_input['email'] = 'BAD_EMAIL'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_successfull_signup(self):
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow = True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code = 302, target_status_code = 200)
        self.assertTemplateUsed(response, 'home.html')
        user = User.objects.get(email = 'john@example.org')
        self.assertEqual(user.name, self.form_input['name'])
        self.assertEqual(user.email, self.form_input['email'])
        self.assertEqual(user.bio, self.form_input['bio'])
        self.assertEqual(user.personal_statement, self.form_input['personal_statement'])
        self.assertEqual(user.chess_experience, self.form_input['chess_experience'])
        is_password_correct = check_password(self.form_input['new_password'], user.password)
        self.assertTrue(is_password_correct)
        self.assertTrue(self._is_logged_in())

    def test_sign_up_uses_correct_template(self):
        response = self.client.get(reverse('sign_up'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
