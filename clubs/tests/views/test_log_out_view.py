"""Tests of the log out view """
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club
from clubs.tests.helpers import LogInTester

class LogOutViewTestCase(TestCase, LogInTester):
    """Tests of the log out view """

    def setUp(self):
        self.url = reverse('log_out')
        self.user1 = User.objects.create_user(
            email = 'sensei@cobrakai.dojo',
            name = 'Jonny Lawrence',
            personal_statement = 'I\'m gonna kick some ass',
            chess_experience = 'B',
            password = 'NoM1yag1Do!',
            bio = 'STRIKE FIRST - STRIKE HARD - NO MERCY',
        )

    def test_log_out_url(self):
        self.assertEqual(self.url, '/log_out/')

    def test_get_log_out(self):
        self.client.login(email='sensei@cobrakai.dojo', password='NoM1yag1Do!')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        response_url = reverse('index')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertFalse(self._is_logged_in())

    def test_log_out_uses_correct_template(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_get_log_out_without_being_logged_in(self):
        response = self.client.get(self.url, follow=True)
        response_url = reverse('index')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertFalse(self._is_logged_in())
