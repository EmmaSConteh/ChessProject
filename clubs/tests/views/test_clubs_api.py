import json
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, ClubMembership
from clubs.tests.helpers import LogInTester

class ClubAPI(TestCase):

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

        User.objects.create_user(name="random", email="r@r.com", personal_statement="Testing",password="Password123",bio="Testing")

        self.url = reverse("club")

    def test_invalid_club(self):
        form_input = {"email": "r@r.com", "password": "Password123"}
        response = self.client.post(reverse("log_in"), form_input)
        response = self.client.get(self.url, {"name": "pingo storm"})
        self.assertTrue(response.status_code==404)

    def test_as_not_in_club(self):
        form_input = {"email": "r@r.com", "password": "Password123"}
        response = self.client.post(reverse("log_in"), form_input)
        response = self.client.get(self.url, {"name": "test"})
        self.assertTrue(response.status_code==403)

    def test_as_member(self):
        form_input = {"email": "9@test.org", "password": "Password123"}
        response = self.client.post(reverse("log_in"), form_input)
        response = self.client.get(self.url, {"name": "test"})
        data = json.loads(response.content)
        members = data["members"] + data["officers"] + [data["owner"]]
        for user in members:
            # Check if the user exists
            userFilter = User.objects.filter(name=user["name"])
            self.assertTrue(userFilter.exists())

            # Get the user
            userObject = userFilter[0]

            # Check if the data is correct
            self.assertTrue("email" not in user)
            self.assertEqual(userObject.bio, user["bio"])
            self.assertEqual(userObject.chess_experience, user["experience"])
            self.assertEqual(userObject.gravatar(), user["gravatar"])
        self.assertTrue(len(members) == len(self.users))
        self.assertFalse(data["is_staff"])
        self.assertFalse(data["is_owner"])
        self.assertEqual(self.club.description, data["description"])
        self.assertEqual(self.club.location, data["location"])

    def test_as_officer(self):
        form_input = {"email": "1@test.org", "password": "Password123"}
        response = self.client.post(reverse("log_in"), form_input)
        response = self.client.get(self.url, {"name": "test"})
        data = json.loads(response.content)
        members = data["members"] + data["officers"] + [data["owner"]]
        for user in members:
            # Check if the user exists
            userFilter = User.objects.filter(email=user["email"])
            self.assertTrue(userFilter.exists())

            # Get the user
            userObject = userFilter[0]

            # Check if the data is correct
            self.assertEqual(userObject.email, user["email"])
            self.assertEqual(userObject.bio, user["bio"])
            self.assertEqual(userObject.chess_experience, user["experience"])
            self.assertEqual(userObject.gravatar(), user["gravatar"])
        self.assertTrue(len(members) == len(self.users))
        self.assertTrue(data["is_staff"])
        self.assertFalse(data["is_owner"])
        self.assertEqual(self.club.description, data["description"])
        self.assertEqual(self.club.location, data["location"])

    def test_as_owner(self):
        form_input = {"email": "0@test.org", "password": "Password123"}
        response = self.client.post(reverse("log_in"), form_input)
        response = self.client.get(self.url, {"name": "test"})
        data = json.loads(response.content)
        members = data["members"] + data["officers"] + [data["owner"]]
        for user in members:
            # Check if the user exists
            userFilter = User.objects.filter(email=user["email"])
            self.assertTrue(userFilter.exists())

            # Get the user
            userObject = userFilter[0]

            # Check if the data is correct
            self.assertEqual(userObject.email, user["email"])
            self.assertEqual(userObject.bio, user["bio"])
            self.assertEqual(userObject.chess_experience, user["experience"])
            self.assertEqual(userObject.gravatar(), user["gravatar"])            
        self.assertTrue(len(members) == len(self.users))
        self.assertTrue(data["is_staff"])
        self.assertTrue(data["is_owner"])
        self.assertEqual(self.club.description, data["description"])
        self.assertEqual(self.club.location, data["location"])
