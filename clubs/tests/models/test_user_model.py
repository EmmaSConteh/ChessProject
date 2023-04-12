""" Unit tests for the User model """
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User
from clubs.models import Club

class UserModelTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email = 'sensei@cobrakai.dojo',
            name = 'Jonny Lawrence',
            personal_statement = 'I\'m gonna kick some ass',
            bio = 'STRIKE FIRST - STRIKE HARD - NO MERCY',
            chess_experience = 'B',
            password = 'NoM1yag1Do!'
        )

    def _create_second_user(self):
        self.user2 = User.objects.create_user(
            name = 'Daniel LaRusso',
            email = 'sensei@miyagi.do',
            personal_statement = 'Kids must know how to protect themselves',
            bio = 'If the opponent insists on war, take away their ability to wage it.',
            chess_experience = 'B',
            password = 'M1yag!Kata'
        )

    def _assert_user_is_valid(self):
        try:
            self.user1.full_clean()
        except(ValidationError):
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user1.full_clean()

    def test_valid_user(self):
        self._assert_user_is_valid();

# Name testing
    def test_name_cannot_be_blank(self):
        self.user1.name = ''
        self._assert_user_is_invalid()

    def test_name_may_already_exist(self):
        self._create_second_user()
        self.user1.name = self.user2.name
        self._assert_user_is_valid()

    def test_name_can_be_50_characters_long(self):
        self.user1.name = 'x' * 50
        self._assert_user_is_valid()

    def test_name_cannot_be_over_50_characters_long(self):
        self.user1.name = 'x' * 51
        self._assert_user_is_invalid()


# Email testing
    def test_email_cannot_be_blank(self):
        self.user1.email = ''
        self._assert_user_is_invalid()

    def test_email_must_be_unique(self):
        self._create_second_user()
        self.user1.email = self.user2.email
        self._assert_user_is_invalid()

    def test_email_must_contain_at_symbol(self):
        self.user1.email = 'senseiatcobrakai.dojo'
        self._assert_user_is_invalid()

    def test_email_must_have_only_1_at_symbol_after_username(self):
        self.user1.email = 'johndoe@@example.org'
        self._assert_user_is_invalid()

    def test_email_must_have_domain_name_followed_by_dot(self):
        self.user1.email = 'johndoe@.org'
        self._assert_user_is_invalid()

    def test_email_must_have_domain_after_the_dot(self):
        self.user1.email = 'johndoe@example.'
        self._assert_user_is_invalid()


# Bio testing
    def test_bio_can_be_blank(self):
        self.user1.bio = ''
        self._assert_user_is_valid()

    def test_bio_may_already_exist(self):
        self._create_second_user()
        self.user1.bio = self.user2.bio
        self._assert_user_is_valid()

    def test_bio_can_be_520_characters_long(self):
        self.user1.bio = 'x' * 520
        self._assert_user_is_valid()

    def test_bio_cannot_be_over_520_characters_long(self):
        self.user1.bio = 'x' * 525
        self._assert_user_is_invalid()


# Personal statement testing
    def test_personal_statement_can_be_blank(self):
        self.user1.personal_statement = ''
        self._assert_user_is_valid()

    def test_personal_statement_may_already_exist(self):
        self._create_second_user()
        self.user1.personal_statement = self.user2.personal_statement
        self._assert_user_is_valid()

    def test_personal_statement_can_be_4000_characters_long(self):
        self.user1.personal_statement = 'x' * 4000
        self._assert_user_is_valid()

    def test_personal_statement_cannot_be_over_4000_characters_long(self):
        self.user1.personal_statement = 'x' * 4001
        self._assert_user_is_invalid()


# Chess Experience testing
    def test_chess_experience_cannot_be_blank(self):
        self.user1.chess_experience = ''
        self._assert_user_is_invalid()

    def test_chess_experience_must_be_one_of_the_available_options(self):
        self.user1.chess_experience = 'X'
        self._assert_user_is_invalid()

    def test_chess_experience_cannot_be_over_1_character_long(self):
        self.user1.chess_experience = 'BI'
        self._assert_user_is_invalid()
