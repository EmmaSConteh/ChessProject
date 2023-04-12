from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club
from clubs.forms import EditProfileForm, LogInForm, SignUpForm
from clubs.tests.helpers import LogInTester, reverse_with_next
from django.contrib import messages

class ProfilePage(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            email = 'sensei@cobrakai.dojo',
            name = 'Jonny Lawrence',
            personal_statement = 'I\'m gonna kick some ass',
            chess_experience = 'B',
            password = 'NoM1yag1Do!',
            bio = 'STRIKE FIRST - STRIKE HARD - NO MERCY',
        )
        self.url = reverse('profile')
        self.form_input = {
            'email': 'sensei2@cobrakai.dojo',
            'bio': 'NO MERCY',
            'chess_experience': 'I',
            'personal_statement': 'gonna kick some ass'
        }

    def test_profile_url(self):
        self.assertEqual(self.url,'/profile/')

    def test_profile_uses_correct_template(self):
        login = self.client.login(email='sensei@cobrakai.dojo', password='NoM1yag1Do!')
        response = self.client.get(reverse('profile'))
        self.assertEqual(str(response.context['user']), 'sensei@cobrakai.dojo')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')

    def test_get_profile(self):
        self.client.login(email='sensei@cobrakai.dojo', password='NoM1yag1Do!')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditProfileForm))
        self.assertEqual(form.instance, self.user1)

    def test_get_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_succesful_profile_update(self):
        self.client.login(email='sensei@cobrakai.dojo', password='NoM1yag1Do!')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.email, 'sensei2@cobrakai.dojo')
        self.assertEqual(self.user1.bio, 'NO MERCY')
        self.assertEqual(self.user1.chess_experience, 'I')
        self.assertEqual(self.user1.personal_statement, 'gonna kick some ass')

    def test_unsuccesful_profile_update(self):
        self.client.login(email=self.user1.email, password='NoM1yag1Do!')
        self.form_input['email'] = 'bad_emailexample.org'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditProfileForm))
        self.assertTrue(form.is_bound)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.email, 'sensei@cobrakai.dojo')
        self.assertEqual(self.user1.bio, 'STRIKE FIRST - STRIKE HARD - NO MERCY')
        self.assertEqual(self.user1.chess_experience, 'B')
        self.assertEqual(self.user1.personal_statement, 'I\'m gonna kick some ass')
