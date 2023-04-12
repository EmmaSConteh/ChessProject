"""Tests for the password view."""
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from django.shortcuts import redirect
from clubs.forms import PasswordForm, LogInForm
from clubs.models import User
from clubs.tests.helpers import reverse_with_next


class PasswordViewTest(TestCase):
    """Test suite for the password view."""

    def setUp(self):
        self.user1 = User.objects.create_user(
            email = 'sensei@cobrakai.dojo',
            name = 'Jonny Lawrence',
            personal_statement = 'I\'m gonna kick some ass',
            chess_experience = 'B',
            password = 'NoM1yag1Do!',
            bio = 'STRIKE FIRST - STRIKE HARD - NO MERCY',
        )
        self.url = reverse('password')
        self.form_input = {
            'password': 'NoM1yag1Do!',
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123',
        }

    def test_password_url(self):
        self.assertEqual(self.url, '/password/')

    def test_get_password(self):
        login = self.client.login(email=self.user1.email, password='NoM1yag1Do!')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordForm))

    def test_get_password_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_succesful_password_change(self):
        self.client.login(email=self.user1.email, password='NoM1yag1Do!')
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'profile.html')
        self.user1.refresh_from_db()
        is_password_correct = check_password('NewPassword123', self.user1.password)
        self.assertTrue(is_password_correct)

    def test_password_change_unsuccesful_without_correct_old_password(self):
        self.client.login(email=self.user1.email, password='NoM1yag1Do!')
        self.form_input['password'] = 'WrongPassword123'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordForm))
        self.user1.refresh_from_db()
        is_password_correct = check_password('NoM1yag1Do!', self.user1.password)
        self.assertTrue(is_password_correct)

    def test_password_change_unsuccesful_without_password_confirmation(self):
        self.client.login(email=self.user1.email, password='NoM1yag1Do!')
        self.form_input['password_confirmation'] = 'WrongPassword123'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordForm))
        self.user1.refresh_from_db()
        is_password_correct = check_password('NoM1yag1Do!', self.user1.password)
        self.assertTrue(is_password_correct)
