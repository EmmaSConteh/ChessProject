import json
import pytz
from datetime import datetime, timedelta
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, ClubMembership, Tournament, TournamentOrganizer, TournamentParticipant

class ToggleParticipationAPI(TestCase):

    def setUp(self):
        self.club = Club.objects.create(name="test",location="london", description="test")
        self.valid_user = User.objects.create_user(
                name="valid",
                email="valid@user.org",
                personal_statement="Testing",
                password="Password123",
                bio="Testing")
        self.invalid_user = User.objects.create_user(
                name="invalid",
                email="invalid@user.org",
                personal_statement="Testing",
                password="Password123",
                bio="Testing")
        self.organizer = User.objects.create_user(
                name="organizer",
                email="organizer@user.org",
                personal_statement="Testing",
                password="Password123",
                bio="Testing")
        self.tournament = Tournament.objects.create(
            club=self.club,
            name="tournament",
            description="testing",
            signup_deadline=datetime.now(tz=pytz.UTC) + timedelta(days=1))
        ClubMembership.objects.create(
            foreign_user=self.organizer, 
            foreign_club=self.club, 
            membership=ClubMembership.UserLevels.OWNER)
        ClubMembership.objects.create(
            foreign_user=self.valid_user, 
            foreign_club=self.club, 
            membership=ClubMembership.UserLevels.MEMBER)
        TournamentOrganizer.objects.create(
            tournament=self.tournament, 
            organizer=self.organizer, 
            organizing_role=TournamentOrganizer.OrganizingRoles.ORGANIZER)
        self.url = reverse("toggle_tournament")

    def test_invalid_club(self):
        response = self.client.post(reverse("log_in"), {"email": self.valid_user.email, "password": "Password123"})
        response = self.client.post(self.url, {"tournament": self.tournament.name, "club": "bookie"})
        self.assertTrue(response.status_code==400)

    def test_invalid_tournament(self):
        response = self.client.post(reverse("log_in"), {"email": self.valid_user.email, "password": "Password123"})
        response = self.client.post(self.url, {"tournament": "bookie", "club": self.club.name})
        self.assertTrue(response.status_code==400)

    def test_as_not_in_club(self):
        response = self.client.post(reverse("log_in"), {"email": self.invalid_user.email, "password": "Password123"})
        response = self.client.post(self.url, {"tournament": self.tournament.name, "club": self.club.name})
        self.assertTrue(response.status_code==403)

    def test_as_not_organizer(self):
        response = self.client.post(reverse("log_in"), {"email": self.valid_user.email, "password": "Password123"})
        response = self.client.post(self.url, {"tournament": self.tournament.name, "club": self.club.name})
        self.assertTrue(response.content.decode() == '1')
        response = self.client.post(self.url, {"tournament": self.tournament.name, "club": self.club.name})
        self.assertTrue(response.content.decode() == '0')

    def test_as_organizer(self):
        response = self.client.post(reverse("log_in"), {"email": self.organizer.email, "password": "Password123"})
        response = self.client.post(self.url, {"tournament": self.tournament.name, "club": self.club.name})
        self.assertTrue(response.status_code==403)