from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club
from clubs.forms import EditProfileForm, LogInForm, SignUpForm
from clubs.tests.helpers import LogInTester, reverse_with_next
from django.contrib import messages

class EditProfilePage(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            email = 'sensei@cobrakai.dojo',
            name = 'Jonny Lawrence',
            personal_statement = 'I\'m gonna kick some ass',
            chess_experience = 'B',
            password = 'NoM1yag1Do!',
            bio = 'STRIKE FIRST - STRIKE HARD - NO MERCY',
        )
        self.url = reverse('edit_profile')
        self.form_input = {
            'email': 'sensei2@cobrakai.dojo',
            'bio': 'NO MERCY',
            'chess_experience': 'I',
            'personal_statement': 'gonna kick some ass'
        }

    def test_edit_profile_url(self):
        self.assertEqual(self.url,'/profile/edit')

    def test_edit_profile_uses_correct_template(self):
        login = self.client.login(email='sensei@cobrakai.dojo', password='NoM1yag1Do!')
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(str(response.context['user']), 'sensei@cobrakai.dojo')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')

    def test_edit_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
