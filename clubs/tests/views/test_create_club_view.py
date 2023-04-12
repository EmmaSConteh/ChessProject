from django.test import TestCase
from clubs.models import Club, User, ClubMembership
from django.urls import reverse
from clubs.forms import CreateClubForm

class CreateClubTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email = 'sensei@cobrakai.dojo',
            name = 'Jonny Lawrence',
            personal_statement = 'I\'m gonna kick some ass',
            bio = 'STRIKE FIRST - STRIKE HARD - NO MERCY',
            chess_experience = 'B',
            password = 'Password123'
        )

        self.url = reverse('create_club')
        self.form_input = {
            'name' : 'Example Club',
            'location' : 'Example location',
            'description' : 'Example description'
        }

    def _create_another_club(self):
        self.club = Club(
            name = 'Cobra Kai',
            location = 'LA, California',
            description = 'STRIKE FIRST - STRIKE HARD - NO MERCY \n the dojo of the All-Valley U18 Karate Champion'
        )
        self.club.save()

        club_membership = ClubMembership(
            foreign_user = self.user,
            foreign_club = self.club,
            membership = ClubMembership.UserLevels.OWNER
        )
        club_membership.save()

    def test_create_club_url(self):
        self.assertEqual(self.url, '/create_club/')

    def test_post_create_club_redirects_when_not_logged_in(self):
        club_count_before = Club.objects.count()
        redirect_url = reverse('log_in') + '?next=' + self.url
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        club_count_after = Club.objects.count()
        self.assertEqual(club_count_after, club_count_before)

    def test_get_create_club_redirects_when_not_logged_in(self):
        club_count_before = Club.objects.count()
        redirect_url = reverse('log_in') + '?next=' + self.url
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        club_count_after = Club.objects.count()
        self.assertEqual(club_count_after, club_count_before)

    def test_get_create_club_uses_correct_template(self):
        self.client.login(email = self.user.email, password = 'Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_club.html')

    def test_get_create_club_uses_correct_form(self):
        self.client.login(email = self.user.email, password = 'Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateClubForm))
        self.assertFalse(form.is_bound)

    def test_successfull_create_club(self):
        self.client.login(email = self.user.email, password = 'Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input, follow = True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count + 1)

        club = Club.objects.get(name = self.form_input['name'])
        self.assertEqual(club.name, self.form_input['name'])
        self.assertEqual(club.location, self.form_input['location'])
        self.assertEqual(club.description, self.form_input['description'])

        try:
            membership = ClubMembership.objects.get(foreign_user = self.user, foreign_club = club)
        except ClubMembership.DoesNotExist:
            self.fail('Owner membership for the new club was not created.')
        self.assertEqual(membership.membership, ClubMembership.UserLevels.OWNER)

        response_url = reverse('home')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'home.html')

    def test_unsuccessful_create_club(self):
        self._create_another_club()

        self.client.login(email = self.user.email, password = 'Password123')
        before_count = Club.objects.count()
        self.form_input['name'] = self.club.name
        response = self.client.post(self.url, self.form_input, follow = True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateClubForm))
        self.assertTrue(form.is_bound)
