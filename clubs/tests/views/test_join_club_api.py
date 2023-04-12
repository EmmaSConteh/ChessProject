import json
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, ClubMembership
from clubs.tests.helpers import LogInTester

class JoinClubAPI(TestCase):

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

        User.objects.create_user(name="random", email="r@r.org", personal_statement="Testing",password="Password123",bio="Testing")

        self.url = reverse("submit_application")

    def test_invalid_club(self):
        form_input = {"email": "r@r.org", "password": "Password123"}
        response = self.client.post(reverse("log_in"), form_input)
        response = self.client.post(self.url, {"name": "pingo storm"})
        self.assertTrue(response.status_code==404)

    def test_as_not_in_club(self):
        form_input = {"email": "r@r.org", "password": "Password123"}
        response = self.client.post(reverse("log_in"), form_input)
        response = self.client.post(self.url, {"name": "test"})
        self.assertTrue(response.content=="1".encode())

    def test_as_member_of_club(self):
        form_input = {"email": "9@test.org", "password": "Password123"}
        response = self.client.post(reverse("log_in"), form_input)
        response = self.client.post(self.url, {"name": "test"})
        self.assertTrue(response.status_code==403)