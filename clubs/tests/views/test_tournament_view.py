from django.test import TestCase
from django.urls import reverse
from clubs.tests.helpers import reverse_with_next
from clubs.models import User, Tournament

class TournamentViewTestCase(TestCase):
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
        self.url = reverse('tournament')

    def test_tournament_url(self):
        self.assertEqual(self.url, '/tournaments/')

    def test_tournament_uses_correct_template(self):
        login = self.client.login(email='sensei@cobrakai.dojo', password='NoM1yag1Do!')
        response = self.client.get(reverse('tournament'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournaments.html')

    def test_get_tournament_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
