""" Unit test of Edit Profile form"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from clubs.models import User
from django import forms
from clubs.forms import EditProfileForm

class EditProfileFormTestCase(TestCase):

    def setUp(self):
        self.form_input = {
            'email' : 'john@example.org',
            'bio' : 'A certain someone playing games',
            'chess_experience': 'A',
            'personal_statement': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut.',
        }

    def test_valid_edit_profile_form(self):
        form = EditProfileForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = EditProfileForm()
        self.assertIn('email', form.fields)
        self.assertIn('bio', form.fields)
        self.assertIn('chess_experience', form.fields)
        self.assertIn('personal_statement', form.fields)

        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))

        self.assertIn('bio', form.fields)
        bio_field = form.fields['bio']
        self.assertTrue(isinstance(bio_field, forms.CharField))

        self.assertIn('chess_experience', form.fields)
        chess_experience_field = form.fields['chess_experience']
        self.assertTrue(hasattr(chess_experience_field, 'choices'))
        self.assertEqual(chess_experience_field.choices[1:], User.ChessExperience.choices)

        self.assertIn('personal_statement', form.fields)
        personal_statement_field = form.fields['personal_statement']
        self.assertTrue(isinstance(personal_statement_field, forms.CharField))

    def test_form_rejects_blank_email(self):
        self.form_input['email']= ''
        form = EditProfileForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_chess_experience(self):
        self.form_input['chess_experience']= ''
        form = EditProfileForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['chess_experience'] = 'wrong input'
        form = EditProfileForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = EditProfileForm(data = self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count + 1)
        user = User.objects.get(email = 'john@example.org')

        self.assertEqual(user.email, self.form_input['email'])
        self.assertEqual(user.bio, self.form_input['bio'])
        self.assertEqual(user.personal_statement, self.form_input['personal_statement'])
        self.assertEqual(user.chess_experience, self.form_input['chess_experience'])
