import pytz
from django.test import TestCase
from django.urls import reverse
from clubs.forms import CreateTournamentForm
from clubs.tests.helpers import reverse_with_next
from clubs.models import Club, Tournament, User, ClubMembership
from datetime import datetime

class CreateTournamentViewTestCase(TestCase):
    """Tests of the tournament in view """

    def setUp(self):
        self.user1 = User.objects.create_user(
            email = 'sensei@cobrakai.dojo',
            name = 'Jonny Lawrence',
            personal_statement = 'I\'m gonna kick some ass',
            chess_experience = 'B',
            password = 'NoM1yag1Do!',
            bio = 'STRIKE FIRST - STRIKE HARD - NO MERCY',
        )
        self.club = Club.objects.create(name="test",location="london", description="test")
        self.form_input = {
            'club' : self.club.pk,
            'name' : 'Johnnys Tournament2',
            'description': 'This is a test tournament',
            'signup_deadline' : datetime.now(tz=pytz.UTC),
            'capacity': 64
        }
        self.tournament = Tournament.objects.create(
            club = self.club,
            name = 'Johnnys Tournament',
            signup_deadline = datetime.now(tz=pytz.UTC),
            description = 'This is a test tournament',
        )

        self.club_memberships = []
        club_membership = ClubMembership(
            foreign_user = self.user1,
            foreign_club = self.club,
            membership = ClubMembership.UserLevels.OWNER
        )
        club_membership.save()
        self.club_memberships.append(club_membership)

        self.url = reverse('create_tournament')

    def test_tournament_url(self):
        self.assertEqual(self.url, '/create_tournament/')

    def test_create_tournament_uses_correct_template(self):
        login = self.client.login(email='sensei@cobrakai.dojo', password='NoM1yag1Do!')
        response = self.client.get(reverse('create_tournament'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_tournament.html')

    def test_get_tournament_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_creation_tournament(self):
        self.client.login(email=self.user1.email, password="NoM1yag1Do!")
        tournament_count_before = Tournament.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        tournament_count_after = Tournament.objects.count()
        self.assertEqual(tournament_count_after, tournament_count_before+1)
        new_tournament = Tournament.objects.latest('club')
        self.assertEqual(self.tournament.club, new_tournament.club)
        response_url = reverse('create_tournament')
        self.assertTemplateUsed(response, 'create_tournament.html')

    def test_unsuccesful_tournament_creation(self):
        self.client.login(email=self.user1.email, password="NoM1yag1Do!")
        tournament_count_before = Tournament.objects.count()
        self.form_input['club'] = ''
        response = self.client.post(self.url, self.form_input, follow=True)
        tournament_count_after = Tournament.objects.count()
        self.assertEqual(tournament_count_after, tournament_count_before)
        self.assertTemplateUsed(response, 'create_tournament.html')
