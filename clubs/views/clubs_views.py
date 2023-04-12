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
from clubs.forms import LogInForm, SignUpForm, EditProfileForm, PasswordForm, CreateClubForm, CreateTournamentForm
from clubs.models import User, ClubMembership, Club, Application, Tournament, TournamentParticipant
from clubs.helpers import login_prohibited
from django.contrib.auth.forms import UserChangeForm
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView, UpdateView

#View that displays all clubs of the system
#Uses the login_required decorator so only authorised users can access this view.
@login_required
def clubs_view(request):
    clubs = []
    for club in Club.objects.all():
        members = ClubMembership.objects.filter(foreign_club=club)
        status = members.filter(foreign_user=request.user)
        if status.exists():
            status = status[0].membership
        else:
            status = ClubMembership.UserLevels.REJECTED - 1
        print(members.count())
        print(club.name)
        clubs.append({
            "name": club.name,
            "owner": members.filter(membership=ClubMembership.UserLevels.OWNER).first().foreign_user,
            "members": members.count(),
            "status": status
        })
    return render(request, "clubs.html", {"clubs": clubs})

#View where user can create club. Checks the validty of and returns the CreateClubForm form
#Uses the login_required decorator so only authorised users can access this view.
@login_required
def create_club(request):
    if request.method == 'POST':
        form = CreateClubForm(request.POST)
        if form.is_valid():
            club = form.save()
            current_user = request.user
            new_membership = ClubMembership(foreign_user=current_user, foreign_club=club, membership=ClubMembership.UserLevels.OWNER)
            new_membership.save()
            return redirect('home')
    else:
       form = CreateClubForm()
    return render(request, 'create_club.html', {'form': form})

#View where user can join a club. Checks if there is an existing membership.
#Uses the login_required decorator so only authorised users can access this view.
@login_required
def post_join_club(request):
    if request.method == "POST":
        club_name = None if "name" not in request.POST else request.POST["name"]
        if not club_name:
            return HttpResponse(status=404)
        club = Club.objects.filter(name=club_name)
        if not club.exists():
            return HttpResponse(status=404)
        club = club[0]
        membership = ClubMembership.objects.filter(foreign_user=request.user, foreign_club=club)
        if membership.exists():
            return HttpResponse(status=403)
        membership = ClubMembership.objects.create(foreign_user=request.user, foreign_club=club, membership=ClubMembership.UserLevels.PENDING)
        return HttpResponse("1", content_type="text/plain")
    return HttpResponse(status=400)

#View where users can see club profiles. 
#Uses the login_required decorator so only authorised users can access this view.
@login_required
def club_profile(request):
    if request.method == "GET":
        club_name = None if "name" not in request.GET else request.GET["name"]
        if not club_name:
            return redirect("home")
        club = Club.objects.filter(name=club_name)
        if not club.exists():
            return HttpResponse(status=404)
        club = club.first()
        tournaments = []
        for tour in Tournament.objects.filter(club=club):
            tournaments.append({
                "name": tour.name,
                "description": tour.description,
                "members": TournamentParticipant.objects.filter(tournament=tour).count()
            })
        memberships = ClubMembership.objects.filter(foreign_club=club)
        data = {
            "club": club,
            "owner": memberships.filter(membership=ClubMembership.UserLevels.OWNER).first().foreign_user,
            "members": memberships.count(),
            "tournaments": tournaments
        }
        return render(request, "club_profile.html", data)
    return HttpResponse(status=400)
