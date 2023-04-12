import json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from clubs.forms import LogInForm, SignUpForm, EditProfileForm, PasswordForm, CreateClubForm, CreateTournamentForm, TournamentOrganizerForm
from clubs.models import User, ClubMembership, Club, Application, Tournament, TournamentOrganizer, TournamentParticipant
from clubs.helpers import login_prohibited
from django.contrib.auth.forms import UserChangeForm
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView, UpdateView

#View where user can see list of all tournaments being held.
#Uses the login_required decorator so only authorised users can access this view.
@login_required
def tournaments_view(request):
    tournaments = []
    for tournament in Tournament.objects.all():
        tournaments.append({
            "name": tournament.name,
            "club": tournament.club,
            "description": tournament.description,
            "signup_deadline" : tournament.signup_deadline,
        })
    return render(request, "tournaments.html", {"tournaments": tournaments})

#View where user can create a tournament. Checks the validy of and then returns the CreateTournamentForm.
#Uses the login_required decorator so only authorised users can access this view.
@login_required
def create_tournament(request):
    data = Tournament.objects.all()
    if request.method == 'POST':
        form = CreateTournamentForm(request.POST, user=request.user)
        if form.is_valid():
            tournament = form.save()
            current_user = request.user
            organizer = TournamentOrganizer.objects.create(
                tournament = tournament,
                organizer = current_user,
                organizing_role = TournamentOrganizer.OrganizingRoles.ORGANIZER
            )
            messages.success(request, 'Tournament created successfully.')
            form = CreateTournamentForm(user = request.user)
        else:
            messages.error(request, 'Invalid form submission.')
            messages.error(request, form.errors)
    else:
        form = CreateTournamentForm(user=request.user)
    return render(request, 'create_tournament.html', {'form': form})


@login_required
def get_club_tournament(request):
    if request.method == "GET":
        tournament_name = None if "tournament" not in request.GET else request.GET["tournament"]
        club_name = None if "club" not in request.GET else request.GET["club"]
        if tournament_name and club_name:
            tournament = Tournament.objects.filter(club__name=club_name, name=tournament_name)
            if not tournament.exists():
                redirect("home")
            tournament = tournament.first()
            # Enter code below here
            return render(request, "tournament_participant.html")
    return redirect("home")

class ManageTournamentView(LoginRequiredMixin, View):
    http_method_names = ['get']

    def get(self, request):
        tournament_name = None if "tournament" not in request.GET else request.GET["tournament"]
        club_name = None if "club" not in request.GET else request.GET["club"]
        if tournament_name and club_name:
            tournament = Tournament.objects.filter(club__name=club_name, name=tournament_name)
            if not tournament.exists():
                redirect("home")
            tournament = tournament.first()
            if TournamentOrganizer.objects.filter(tournament = tournament, organizer = request.user).exists():
                organizers = TournamentOrganizer.objects.filter(tournament = tournament)
                participants = TournamentParticipant.objects.filter(tournament = tournament)
                form = TournamentOrganizerForm(tournament = tournament)
                return render(
                    request,
                    'tournament.html',
                    {'tournament': tournament,
                    'organizers': organizers,
                    'participants': participants,
                    'form': form
                    })
            return redirect('home')
        return redirect('home')

class ManageTournamentCoorganizers(LoginRequiredMixin, View):
    http_method_names = ['post', 'get']

    def get(self, request):
        tournament_name = None if "tournament" not in request.GET else request.GET["tournament"]
        club_name = None if "club" not in request.GET else request.GET["club"]
        if tournament_name and club_name:
            tournament = Tournament.objects.filter(club__name=club_name, name=tournament_name)
            if not tournament.exists():
                return HttpResponse(status = 400)
            tournament = tournament.first()
            if TournamentOrganizer.objects.filter(tournament = tournament, organizer = request.user).exists():
                organizers = TournamentOrganizer.objects.filter(tournament = tournament)
                organizers_list = []
                for o in organizers:
                    organizers_list.append({
                        'name': str(o.organizer.name),
                        'role': o.get_organizing_role_display(),
                        'email': str(o.organizer.email)
                    })

                club_officers = ClubMembership.objects.filter(
                    foreign_club = tournament.club,
                    membership__gte = ClubMembership.UserLevels.OFFICER
                )

                # add the ids of retrieved moderators to a list
                officers_list = []
                for officer in club_officers:
                    officers_list.append(officer.foreign_user.id)

                # retrieve and remove all moderators that are already participating in the tournament
                participating_officers = TournamentParticipant.objects.filter(
                    tournament = tournament,
                    participant_id__in = officers_list
                )
                for po in participating_officers:
                    officers_list.remove(po.participant.id)

                # retrieve and remove all moderators that are already coorganizing the tournament
                organizing_officers = TournamentOrganizer.objects.filter(tournament = tournament)
                for oo in organizing_officers:
                    officers_list.remove(oo.organizer.id)

                available_officers = []
                for o in officers_list:
                    available_officers.append({
                        'id': o,
                        'email': User.objects.get(id = o).email
                    })

                response = {
                    'available_officers': available_officers,
                    'organizers': organizers_list
                }
                return HttpResponse(json.dumps(response), status = 200)
            return HttpResponse(status = 400)
        return HttpResponse(status = 400)

    def post(self, request):
        tournament_name = None if "tournament" not in request.POST else request.POST["tournament"]
        club_name = None if "club" not in request.POST else request.POST["club"]
        # print(request.POST)
        if tournament_name and club_name:
            tournament = Tournament.objects.filter(club__name=club_name, name=tournament_name)
            if not tournament.exists():
                return HttpResponse("tournament does not exist", status = 400, content_type = "text/plain")
            tournament = tournament.first()
            if TournamentOrganizer.objects.filter(tournament = tournament, organizer = request.user, organizing_role = TournamentOrganizer.OrganizingRoles.ORGANIZER).exists():
                post_organizer = request.POST['organizer']
                post_organizer = User.objects.get(email = post_organizer)
                if post_organizer and not TournamentOrganizer.objects.filter(tournament = tournament, organizer = post_organizer).exists():
                    new_organizer = TournamentOrganizer(
                        tournament = tournament,
                        organizer = post_organizer,
                        organizing_role = TournamentOrganizer.OrganizingRoles.COORGANIZER
                    )
                    new_organizer.save()
                    organizers = TournamentOrganizer.objects.filter(tournament = tournament)
                    # response = {'organizers': organizers}
                    return HttpResponse(status = 201)
                return HttpResponse('form invalid', status = 400, content_type = "text/plain")
            return HttpResponse('organizer not found', status = 400, content_type = "text/plain")
        return HttpResponse('tournament and club not provided', status = 400, content_type = "text/plain")
