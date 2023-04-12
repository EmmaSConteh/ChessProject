from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from clubs.models import User
from clubs.forms import PasswordForm, LogInForm

class PasswordFormTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            email = 'sensei@cobrakai.dojo',
            name = 'Jonny Lawrence',
            personal_statement = 'I\'m gonna kick some ass',
            chess_experience = 'B',
            password = 'NoM1yag1Do!',
            bio = 'STRIKE FIRST - STRIKE HARD - NO MERCY',
        )
        self.form_input = {
            'password': 'NoM1yag1Do!',
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123',
        }

    def test_form_has_necessary_fields(self):
        form = PasswordForm(user=self.user1)
        self.assertIn('password', form.fields)
        self.assertIn('new_password', form.fields)
        self.assertIn('password_confirmation', form.fields)

    def test_password_uses_correct_template(self):
        login = self.client.login(email='sensei@cobrakai.dojo' , password='NoM1yag1Do!')
        response = self.client.get(reverse('password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')

    def test_valid_form(self):
        form = PasswordForm(user=self.user1, data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_password_must_contain_uppercase_character(self):
        self.form_input['new_password'] = 'password123'
        self.form_input['password_confirmation'] = 'password123'
        form = PasswordForm(user=self.user1, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lowercase_character(self):
        self.form_input['new_password'] = 'PASSWORD123'
        self.form_input['password_confirmation'] = 'PASSWORD123'
        form = PasswordForm(user=self.user1, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        self.form_input['new_password'] = 'PasswordABC'
        self.form_input['password_confirmation'] = 'PasswordABC'
        form = PasswordForm(user=self.user1, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_new_password_and_password_confirmation_are_identical(self):
        self.form_input['password_confirmation'] = 'WrongPassword123'
        form = PasswordForm(user=self.user1, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_be_valid(self):
        self.form_input['password'] = 'WrongPassword123'
        form = PasswordForm(user=self.user1, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_contain_user(self):
        form = PasswordForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_save_form_changes_password(self):
        form = PasswordForm(user=self.user1, data=self.form_input)
        form.full_clean()
        form.save()
        self.user1.refresh_from_db()
        self.assertFalse(check_password('NoM1yag1Do!', self.user1.password))
        self.assertTrue(check_password('NewPassword123', self.user1.password))
