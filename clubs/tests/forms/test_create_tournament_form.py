""" Unit test of Create Tournament form"""
import pytz
from django.test import TestCase
from clubs.forms import CreateTournamentForm
from clubs.models import Club, Tournament, User, ClubMembership
from datetime import datetime

class CreateTournamentFormTestCase(TestCase):

    def setUp(self):
        self.club = Club.objects.create(name="test",location="london", description="test")
        self.form_input = {
            'club' : self.club,
            'name' : 'Johnnys Tournament',
            'description': 'This is a test tournament',
            'signup_deadline' : datetime.now(tz=pytz.UTC),
            'capacity': 64
        }

        self.user = User.objects.create_user(
            email = 'sensei@cobrakai.dojo',
            name = 'Jonny Lawrence',
            personal_statement = 'I\'m gonna kick some ass',
            bio = 'STRIKE FIRST - STRIKE HARD - NO MERCY',
            chess_experience = 'B',
            password = 'NoM1yag1Do!'
        )

        self.club_memberships = []
        club_membership = ClubMembership(
            foreign_user = self.user,
            foreign_club = self.club,
            membership = ClubMembership.UserLevels.OWNER
        )
        club_membership.save()
        self.club_memberships.append(club_membership)


    def test_valid_create_tournament_form(self):
        form = CreateTournamentForm(data = self.form_input, user = self.user)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = CreateTournamentForm(user = self.user)
        self.assertIn('club', form.fields)
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('signup_deadline', form.fields)

    def test_form_rejects_blank_club(self):
        self.form_input['club']= ''
        form = CreateTournamentForm(data=self.form_input, user = self.user)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_name(self):
        self.form_input['name']= ''
        form = CreateTournamentForm(data=self.form_input, user = self.user)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_description(self):
        self.form_input['description']= ''
        form = CreateTournamentForm(data=self.form_input, user = self.user)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_sign_up_deadline(self):
        self.form_input['signup_deadline']= ''
        form = CreateTournamentForm(data=self.form_input, user = self.user)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = CreateTournamentForm(data = self.form_input, user = self.user)
        before_count = Tournament.objects.count()
        form.save()
        after_count = Tournament.objects.count()
        self.assertEqual(after_count, before_count + 1)
        tournament = Tournament.objects.get(name = 'Johnnys Tournament')
        self.assertEqual(tournament.name, self.form_input['name'])
        self.assertEqual(tournament.club, self.form_input['club'])
        self.assertEqual(tournament.description, self.form_input['description'])
        self.assertEqual(tournament.signup_deadline, self.form_input['signup_deadline'])
        self.assertEqual(tournament.capacity, self.form_input['capacity'])
