from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User, Club, ClubMembership

class ClubMembershipModelTestCase(TestCase):
    def setUp(self):
        self.users = []
        self.users.append(User.objects.create_user(
            email = 'sensei@cobrakai.dojo',
            name = 'Jonny Lawrence',
            personal_statement = 'I\'m gonna kick some ass',
            bio = 'STRIKE FIRST - STRIKE HARD - NO MERCY',
            chess_experience = 'B',
            password = 'NoM1yag1Do!'
        ))

        self.clubs = []
        club = Club(
            name = 'Cobra Kai',
            location = 'LA, California',
            description = 'STRIKE FIRST - STRIKE HARD - NO MERCY \n the dojo of the All-Valley U18 Karate Champion'
        )
        club.save()
        self.clubs.append(club)

        self.club_memberships = []
        club_membership = ClubMembership(
            foreign_user = self.users[0],
            foreign_club = self.clubs[0],
            membership = ClubMembership.UserLevels.OWNER
        )
        club_membership.save()
        self.club_memberships.append(club_membership)

    def _create_second_user(self):
        user = User.objects.create_user(
            name = 'Daniel LaRusso',
            email = 'sensei@miyagi.do',
            personal_statement = 'Kids must know how to protect themselves',
            bio = 'If the opponent insists on war, take away their ability to wage it.',
            chess_experience = 'B',
            password = 'M1yag!Kata'
        )
        self.users.append(user)

    def _create_second_club(self):
        club = Club(
            name = 'Miyagi Do',
            location = 'LA, California',
            description = 'Karate is not about fighting - it is a way of life'
        )
        club.save()
        self.clubs.append(club)

    def _create_extra_membership(self, user_index, club_index, membership_level):
        club_membership = ClubMembership(
            foreign_user = self.users[user_index],
            foreign_club = self.clubs[club_index],
            membership = membership_level
        )
        club_membership.save()
        self.club_memberships.append(club_membership)



    def _assert_membership_is_valid(self, membership_index):
        try:
            self.club_memberships[membership_index].full_clean()
        except(ValidationError):
            self.fail('Test club membership should be valid')

    def _assert_membership_is_invalid(self, membership_index):
        with self.assertRaises(ValidationError):
            self.club_memberships[membership_index].full_clean()



    def test_valid_club_membership(self):
        self._assert_membership_is_valid(0)

    def test_user_can_only_have_one_membership_per_club(self):
        self._create_second_user()
        self._create_second_club()
        self._create_extra_membership(1, 1, ClubMembership.UserLevels.MEMBER)

        self.club_memberships[0].foreign_user = self.club_memberships[1].foreign_user
        self.club_memberships[0].foreign_club = self.club_memberships[1].foreign_club

        self._assert_membership_is_invalid(0)


    def test_user_cannot_be_null(self):
        self.club_memberships[0].foreign_user = None
        self._assert_membership_is_invalid(0)

    def test_membership_is_deleted_when_foreign_user_is_deleted(self):
        self.users[0].delete()
        self.assertEqual(len(ClubMembership.objects.all()), 0)

    def test_user_can_be_a_member_in_multiple_clubs(self):
        self._create_second_club()
        self._create_extra_membership(0, 1, ClubMembership.UserLevels.MEMBER)
        self._assert_membership_is_valid(1)


    def test_club_cannot_be_null(self):
        self.club_memberships[0].foreign_club = None
        self._assert_membership_is_invalid(0)

    def test_membership_is_deleted_when_foreign_club_is_deleted(self):
        self.clubs[0].delete()
        self.assertEqual(len(ClubMembership.objects.all()), 0)

    def test_club_can_have_multiple_members(self):
        self._create_second_user()
        self._create_extra_membership(1, 0, ClubMembership.UserLevels.MEMBER)
        self._assert_membership_is_valid(1)



    def test_membership_must_have_valid_membership_level(self):
        self.club_memberships[0].membership = 3
        self._assert_membership_is_invalid(0)

    def test_membership_level_cannot_be_blank(self):
        self.club_memberships[0].membership = None
        self._assert_membership_is_invalid(0)


    def test_club_can_only_have_one_owner(self):
        self.club_memberships[0].membership = ClubMembership.UserLevels.OWNER
        self.club_memberships[0].save()
        self._create_second_user()
        self._create_extra_membership(1, 0, ClubMembership.UserLevels.OFFICER)
        self.club_memberships[1].membership = ClubMembership.UserLevels.OWNER
        self._assert_membership_is_invalid(1)
