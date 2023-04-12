import json
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, ClubMembership
from clubs.tests.helpers import LogInTester

class ChangeRankAPI(TestCase):

    def setUp(self):
        self.club = Club.objects.create(name="test",location="london", description="test")
        self.users = []
        for i in range(10):
            self.users.append(User.objects.create_user(
                name=str(i),
                email=str(i)+"@test.org",
                personal_statement="Testing",
                password="Password123",
                bio="Testing"
            ))

        for user in self.users:
            ClubMembership.objects.create(foreign_user=user, foreign_club=self.club, membership=ClubMembership.UserLevels.OFFICER)

        members = ClubMembership.objects.filter(foreign_club=self.club)
        first = members.first()
        first.membership = ClubMembership.UserLevels.OWNER
        first.save()
        last = members.last()
        last.membership = ClubMembership.UserLevels.MEMBER
        last.save()

        reject = User.objects.create_user(name="rejected", email="rejected@r.org", personal_statement="1", password="Password123", bio="1")
        ClubMembership.objects.create(foreign_user=reject, foreign_club=self.club, membership=ClubMembership.UserLevels.REJECTED)

        User.objects.create_user(name="random", email="r@r.org", personal_statement="Testing",password="Password123",bio="Testing")

        self.url = reverse("change_rank")

    def test_invalid_club(self):
        form_input = {"email": "r@r.org", "password": "Password123"}
        response = self.client.post(reverse("log_in"), form_input)
        response = self.client.post(self.url, {"name": "pingo storm", "email": "r@r.org", "promoting": "true"})
        self.assertTrue(response.status_code==403)

    def test_as_not_in_club(self):
        form_input = {"email": "r@r.org", "password": "Password123"}
        response = self.client.post(reverse("log_in"), form_input)
        response = self.client.post(self.url, {"name": "test", "email": "9@test.org", "promoting": "true"})
        self.assertTrue(response.status_code==403)

    def test_as_member(self):
        form_input = {"email": "9@test.org", "password": "Password123"}
        response = self.client.post(reverse("log_in"), form_input)
        response = self.client.post(self.url, {"name": "test", "email": "9@test.org", "promoting": "true"})
        self.assertTrue(response.status_code==403)

    def test_as_officer(self):
        form_input = {"email": "1@test.org", "password": "Password123"}
        response = self.client.post(reverse("log_in"), form_input)
        response = self.client.post(self.url, {"name": "test", "email": "9@test.org", "promoting": "false"})
        self.assertTrue(response.content=="1".encode())
        member = ClubMembership.objects.filter(foreign_user__email="9@test.org")[0]
        self.assertTrue(member.membership==ClubMembership.UserLevels.REJECTED)

    def test_as_owner(self):
        form_input = {"email": "0@test.org", "password": "Password123"}
        response = self.client.post(reverse("log_in"), form_input)
        response = self.client.post(self.url, {"name": "test", "email": "9@test.org", "promoting": "true"})
        self.assertTrue(response.content=="1".encode())
        member = ClubMembership.objects.filter(foreign_user__email="9@test.org")[0]
        self.assertTrue(member.membership==ClubMembership.UserLevels.OFFICER)

    def test_invalid_promotion(self):
        form_input = {"email": "0@test.org", "password": "Password123"}
        response = self.client.post(reverse("log_in"), form_input)
        response = self.client.post(self.url, {"name": "test", "email": "9@test.org", "promoting": "boosted"})
        self.assertTrue(response.status_code==400)

    def test_promote_non_member(self):
        form_input = {"email": "0@test.org", "password": "Password123"}
        response = self.client.post(reverse("log_in"), form_input)
        response = self.client.post(self.url, {"name": "test", "email": "r@r.org", "promoting": "1"})
        self.assertTrue(response.status_code==404)

    def test_promote_owner(self):
        form_input = {"email": "0@test.org", "password": "Password123"}
        response = self.client.post(reverse("log_in"), form_input)
        response = self.client.post(self.url, {"name": "test", "email": "0@test.org", "promoting": "1"})
        self.assertTrue(response.status_code==403)

    def test_demote_rejected(self):
        form_input = {"email": "0@test.org", "password": "Password123"}
        response = self.client.post(reverse("log_in"), form_input)
        response = self.client.post(self.url, {"name": "test", "email": "rejected@r.org", "promoting": "1"})
        self.assertTrue(response.status_code==403)

    def test_transfer_ownership_as_officer(self):
        form_input = {"email": "1@test.org", "password": "Password123"}
        response = self.client.post(reverse("log_in"), form_input)
        response = self.client.post(self.url, {"name": "test", "email": "2@test.org", "promoting": "1"})
        self.assertTrue(response.status_code==403)

    def test_transfer_ownership_as_owner(self):
        form_input = {"email": "0@test.org", "password": "Password123"}
        response = self.client.post(reverse("log_in"), form_input)
        response = self.client.post(self.url, {"name": "test", "email": "2@test.org", "promoting": "1"})
        self.assertTrue(response.content=="1".encode())
        officer = ClubMembership.objects.filter(foreign_user__email="2@test.org")[0]
        me = ClubMembership.objects.filter(foreign_user__email="0@test.org")[0]
        self.assertTrue(officer.membership==ClubMembership.UserLevels.OWNER)
        self.assertTrue(me.membership==ClubMembership.UserLevels.OFFICER)