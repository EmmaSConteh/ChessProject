from django.core.exceptions import ValidationError
from django.test import TestCase
# from clubs.models import User
from clubs.models import Club

class ClubModelTestCase(TestCase):
    def setUp(self):
        self.club1 = Club(
            name = 'My super chess club',
            location = 'The Multiverse',
            description = 'We welcome everyone, no matter the universe'
        )
        self.club1.save()

    def _assert_club_is_valid(self):
        try:
            self.club1.full_clean()
        except(ValidationError):
            self.fail('Test club should be valid')

    def _assert_club_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.club1.full_clean()

    def test_valid_club(self):
        self._assert_club_is_valid()


# Name testing
    def test_name_cannot_be_blank(self):
        self.club1.name = ''
        self._assert_club_is_invalid()

    def test_name_must_be_unique(self):
        club = Club(
            name = 'My other chess club',
            location = 'The Multiverse',
            description = 'We welcome everyone, no matter the universe'
        )
        club.save()
        self.club1.name = club.name
        self._assert_club_is_invalid()

    def test_name_can_be_100_characters_long(self):
        self.club1.name = 'x' * 100
        self._assert_club_is_valid()

    def test_name_cannot_be_over_100_characters_long(self):
        self.club1.name = 'x' * 101
        self._assert_club_is_invalid()

# Location testing
    def test_location_cannot_be_blank(self):
        self.club1.location = ''
        self._assert_club_is_invalid()

    def test_name_can_be_180_characters_long(self):
        self.club1.location = 'x' * 180
        self._assert_club_is_valid()

    def test_name_cannot_be_over_180_characters_long(self):
        self.club1.location = 'x' * 181
        self._assert_club_is_invalid()

# Description testing
    def test_description_cannot_be_blank(self):
        self.club1.description = ''
        self._assert_club_is_invalid()

    def test_description_can_be_200_characters_long(self):
        self.club1.description = 'x' * 200
        self._assert_club_is_valid()

    def test_name_cannot_be_over_200_characters_long(self):
        self.club1.description = 'x' * 201
        self._assert_club_is_invalid()
