import pytz
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import Tournament
from clubs.models import Club
from datetime import datetime

class TournamentModelTestCase(TestCase):

    def setUp(self):
        self.club = Club.objects.create(name="test",location="london", description="test")
        self.tournament = Tournament.objects.create(
            club = self.club,
            name = 'Johnnys Tournament',
            signup_deadline = datetime.now(tz=pytz.UTC),
            description = 'This is a test tournament',
            capacity = 6,
        )

    def _assert_tournament_is_valid(self):
        try:
            self.tournament.full_clean()
        except(ValidationError):
            self.fail('Test tournament should be valid')

    def _assert_tournament_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.tournament.full_clean()


    def test_valid_tournament(self):
        self._assert_tournament_is_valid()

    def test_name_cannot_be_blank(self):
        self.tournament.name = ''
        self._assert_tournament_is_invalid()

    def test_name_must_be_unique(self):
        tournament1 = Tournament(
            club = self.club,
            name = 'Johnnys second Tournament',
            signup_deadline = datetime.now(tz=pytz.UTC),
            description = 'This is a test tournament',
            capacity = 6
        )
        tournament1.save()
        self.tournament.name = tournament1.name
        self._assert_tournament_is_invalid()

    def test_name_can_be_100_characters_long(self):
        self.tournament.name = 'x' * 100
        self._assert_tournament_is_valid()

    def test_name_cannot_be_over_100_characters_long(self):
        self.tournament.name = 'x' * 101
        self._assert_tournament_is_invalid()

    def test_description_cannot_be_blank(self):
        self.tournament.description = ''
        self._assert_tournament_is_invalid()

    def test_description_can_be_200_characters_long(self):
        self.tournament.description = 'x' * 520
        self._assert_tournament_is_valid()

    def test_name_cannot_be_over_200_characters_long(self):
        self.tournament.description = 'x' * 521
        self._assert_tournament_is_invalid()

    def test_club_cannot_be_blank(self):
        self.tournament.club = None
        self._assert_tournament_is_invalid()

    def test_signup_deadline_cannot_be_blank(self):
        self.tournament.signup_deadline = ''
        self._assert_tournament_is_invalid()

    def test_capacity_deadline_cannot_be_blank(self):
        self.tournament.capacity = ''
        self._assert_tournament_is_invalid()
