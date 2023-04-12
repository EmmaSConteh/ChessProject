from django.test import TestCase
from clubs.models import Club
from django import forms
from clubs.forms import CreateClubForm

class CreateClubTestCase(TestCase):
    def setUp(self):
        self.form_input = {
        'name' : 'Example Club',
        'location' : 'Example location',
        'description' : 'Example description'
        }

    def test_club_form_has_necessary_fields(self):
        form = CreateClubForm()
        self.assertIn('name', form.fields)
        self.assertIn('location', form.fields)
        self.assertIn('description', form.fields)

        description_field = form.fields['description']
        self.assertTrue(isinstance(description_field.widget, forms.Textarea))

    def test_valid_create_club_form(self):
        form = CreateClubForm(data = self.form_input)
        self.assertTrue(form.is_valid())



    def test_form_rejects_blank_name(self):
        self.form_input['name'] = ''
        form = CreateClubForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_invalid_name(self):
        self.form_input['name'] = 'x' * 101
        form = CreateClubForm(data = self.form_input)
        self.assertFalse(form.is_valid())



    def test_form_rejects_blank_location(self):
        self.form_input['location'] = ''
        form = CreateClubForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_invalid_location(self):
        self.form_input['location'] = 'x' * 181
        form = CreateClubForm(data = self.form_input)
        self.assertFalse(form.is_valid())



    def test_form_rejects_blank_description(self):
        self.form_input['description'] = ''
        form = CreateClubForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_description(self):
        self.form_input['description'] = 'x' * 201
        form = CreateClubForm(data = self.form_input)
        self.assertFalse(form.is_valid())


    def test_form_uses_model_validation(self):
        form = CreateClubForm(data = self.form_input)
        form.save()
        club = Club.objects.get(name = self.form_input['name'])
        form = CreateClubForm(data = self.form_input)
        self.assertFalse(form.is_valid())



    def test_form_must_save_correctly(self):
        form = CreateClubForm(data = self.form_input)
        before_count = Club.objects.count()
        form.save()
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count+1)
        club = Club.objects.get(name = 'Example Club')
        self.assertEqual(club.name, self.form_input['name'])
        self.assertEqual(club.location, self.form_input['location'])
        self.assertEqual(club.description, self.form_input['description'])
