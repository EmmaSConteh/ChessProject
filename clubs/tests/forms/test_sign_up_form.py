""" Unit test of Sign Up form"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password

from clubs.models import User

from django import forms
from clubs.forms import SignUpForm

class SignUpFormTestCase(TestCase):

    def setUp(self):
        self.form_input = {
            'name' : 'Johnny',
            'email' : 'john@example.org',
            'bio' : 'A certain someone playing games',
            'chess_experience': 'A',
            'personal_statement': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut.',
            'new_password' : '123QWErty',
            'password_confirmation': '123QWErty'
        }

    def test_valid_signup_form(self):
        form = SignUpForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = SignUpForm()
        self.assertIn('name', form.fields)
        self.assertIn('bio', form.fields)
        self.assertIn('personal_statement', form.fields)

        self.assertIn('chess_experience', form.fields)
        chess_experience_field = form.fields['chess_experience']
        self.assertTrue(hasattr(chess_experience_field, 'choices'))
        self.assertEqual(chess_experience_field.choices[1:], User.ChessExperience.choices)

        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))

        self.assertIn('new_password', form.fields)
        new_pwd_widget = form.fields['new_password'].widget
        self.assertTrue(isinstance(new_pwd_widget, forms.PasswordInput))

        self.assertIn('password_confirmation', form.fields)
        confirm_pwd_widget = form.fields['password_confirmation'].widget
        self.assertTrue(isinstance(confirm_pwd_widget, forms.PasswordInput))


    def test_form_uses_model_validation(self):
        self.form_input['chess_experience'] = 'wrong input'
        form = SignUpForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_uppercase_character(self):
        self.form_input['new_password'] = 'password123'
        self.form_input['password_confirmation'] = 'password123'
        form = SignUpForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lowercase_character(self):
        self.form_input['new_password'] = 'PASSWORD123'
        self.form_input['password_confirmation'] = 'PASSWORD123'
        form = SignUpForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        self.form_input['new_password'] = 'passwordBLABLA'
        self.form_input['password_confirmation'] = 'passwordBLABLA'
        form = SignUpForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_and_confirmation_must_be_identical(self):
        self.form_input['new_password'] = 'Password123'
        self.form_input['password_confirmation'] = 'Password1234'
        form = SignUpForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = SignUpForm(data = self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count + 1)
        user = User.objects.get(email = 'john@example.org')

        self.assertEqual(user.name, self.form_input['name'])
        self.assertEqual(user.email, self.form_input['email'])
        self.assertEqual(user.bio, self.form_input['bio'])
        self.assertEqual(user.personal_statement, self.form_input['personal_statement'])
        self.assertEqual(user.chess_experience, self.form_input['chess_experience'])
        is_password_correct = check_password(self.form_input['new_password'], user.password)
        self.assertTrue(is_password_correct)
