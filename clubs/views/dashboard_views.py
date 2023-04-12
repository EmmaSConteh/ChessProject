import json
import pytz
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import redirect, render
from clubs.models import User, ClubMembership, Club, Application, Tournament, TournamentOrganizer, TournamentParticipant


def package_members(club_memberships, show_email=False) -> dict:
    package = []
    for cm in club_memberships:
        package.append({
            "name": cm.foreign_user.name,
            "experience": cm.foreign_user.get_chess_experience_display(),
            "bio": cm.foreign_user.bio,
            "gravatar": cm.foreign_user.gravatar(),
            "user_level": cm.get_membership_display()
        })
        if show_email:
            package[-1]["email"] = cm.foreign_user.email
    return package

#Home View where user can see clubs they have a membership with.
#Uses the login_required decorator so only authorised users can access this view.
@login_required
def home(request):
    current_user = request.user
    memberships = ClubMembership.objects.filter(foreign_user=current_user, membership__gte=0)
    return render(request, "home.html", {"club_memberships": memberships})

#View where user can see accepted members of a club.
#Uses the login_required decorator so only authorised users can access this view.
@login_required
def get_club(request):
    if request.method == "GET":
        club_name = None if "name" not in request.GET else request.GET["name"]
        if club_name:
            club_memberships = ClubMembership.objects.filter(foreign_club__name=club_name)
            if not club_memberships.exists():
                return HttpResponse(status=404)
            my_membership = club_memberships.filter(foreign_user=request.user)
            if not my_membership.exists():
                return HttpResponse(status=403)
            is_staff = my_membership.first().membership > ClubMembership.UserLevels.MEMBER
            club = Club.objects.get(name=club_name)
            response = {
                "owner": package_members(club_memberships.filter(membership=ClubMembership.UserLevels.OWNER), is_staff)[0],
                "officers": package_members(club_memberships.filter(membership=ClubMembership.UserLevels.OFFICER), is_staff),
                "members": package_members(club_memberships.filter(membership=ClubMembership.UserLevels.MEMBER), is_staff),
                "is_staff": is_staff,
                "is_owner": my_membership.first().membership == ClubMembership.UserLevels.OWNER,
                "description": club.description,
                "location": club.location
            }
            return HttpResponse(json.dumps(response), content_type="application/json")
    return HttpResponse(status=400)

#View where user can see pending members of a club.
#Uses the login_required decorator so only authorised users can access this view.
@login_required
def get_club_pending_members(request):
    if request.method == "GET":
        club_name = None if "name" not in request.GET else request.GET["name"]
        if club_name:
            my_membership = ClubMembership.objects.filter(foreign_club__name=club_name, foreign_user=request.user)
            if not my_membership.exists():
                return HttpResponse(status=403)
            if my_membership.first().membership <= ClubMembership.UserLevels.MEMBER:
                return HttpResponse(status=403)
            pending_memberships = ClubMembership.objects.filter(foreign_club__name=club_name, membership=ClubMembership.UserLevels.PENDING)
            response = package_members(pending_memberships, True)
            return HttpResponse(json.dumps(response), content_type="application/json")
    return HttpResponse(status=400)

#View where user can see the status of their application to a club.
#Uses the login_required decorator so only authorised users can access this view.
@login_required
def get_applications(request):
    if request.method == "GET":
        memberships = ClubMembership.objects.filter(foreign_user=request.user)
        pending = memberships.filter(membership=ClubMembership.UserLevels.PENDING)
        rejected = memberships.filter(membership=ClubMembership.UserLevels.REJECTED)
        response = {"pending": [], "rejected": []}
        for app in pending:
            response["pending"].append(app.foreign_club.name)
        for app in rejected:
            response["rejected"].append(app.foreign_club.name)
        return HttpResponse(json.dumps(response), content_type="application/json")

#View where owners can promote and demote members of their club.
#Uses the login_required decorator so only authorised users can access this view.
@login_required
def post_change_rank(request):
    if request.method == "POST":
        user_email = None if "email" not in request.POST else request.POST["email"]
        club_name = None if "name" not in request.POST else request.POST["name"]
        is_promoting = None if "promoting" not in request.POST else request.POST["promoting"]

        if user_email and club_name and is_promoting:
            if is_promoting == "true" or is_promoting == "1":
                promotion_direction = 1
            elif is_promoting == "false" or is_promoting == "0":
                promotion_direction = -1
            else:
                return HttpResponse(status=400)

            # Check if the sender is a user
            my_membership = ClubMembership.objects.filter(foreign_club__name=club_name, foreign_user=request.user)
            if not my_membership.exists():
                return HttpResponse(status=403)

            # Check if the user is above a member
            my_membership = my_membership.first()
            if my_membership.membership < ClubMembership.UserLevels.OFFICER:
                return HttpResponse(status=403)

            # Check if the target user exists
            membership = ClubMembership.objects.filter(foreign_club__name=club_name, foreign_user__email=user_email)
            if not membership.exists():
                return HttpResponse(status=404)
            membership = membership.first()
            new_rank = membership.membership + promotion_direction

            # Check if the target is pending, a member or an officer
            if membership.membership < ClubMembership.UserLevels.PENDING or membership.membership > ClubMembership.UserLevels.OFFICER:
                return HttpResponse(status=403)

            # Replace pending rank with an instant rejection
            if new_rank == ClubMembership.UserLevels.PENDING:
                new_rank -= 1
            membership.membership = new_rank

            if new_rank >= ClubMembership.UserLevels.OFFICER:
                # Check if an owner
                if my_membership.membership == ClubMembership.UserLevels.OFFICER:
                    return HttpResponse(status=403)

                # Demote the current owner
                if new_rank == ClubMembership.UserLevels.OWNER:
                    my_membership.membership -= 1
                    my_membership.save()

            membership.save()
            return HttpResponse("1", content_type="text/plain")

    return HttpResponse(status=400)

#View where user can see the details of their application.
#Uses the login_required decorator so only authorised users can access this view.
@login_required
def get_club_tournaments(request):
    if request.method == "GET":
        club_name = None if "name" not in request.GET else request.GET["name"]
        if club_name:
            tournaments = Tournament.objects.filter(club__name=club_name)
            response = []
            for tour in tournaments:
                participants = TournamentParticipant.objects.filter(tournament=tour)
                response.append({
                    "name": tour.name,
                    "description": tour.description,
                    "signup_deadline": tour.signup_deadline.strftime("%m/%d/%Y %H:%M"),
                    "organizer": TournamentOrganizer.objects.get(tournament=tour, organizing_role=TournamentOrganizer.OrganizingRoles.ORGANIZER).organizer.name,
                    "participants": participants.count(),
                    "participating": participants.filter(participant=request.user).exists(),
                    "limit": tour.capacity,
                    "is_coorganizer": TournamentOrganizer.objects.filter(tournament = tour, organizer = request.user).exists(),
                })
            response.reverse()
            return HttpResponse(json.dumps(response), content_type="application/json")
    return HttpResponse(status=400)


@login_required
def post_toggle_tournament(request):
    if request.method == "POST":
        tournament_name = None if "tournament" not in request.POST else request.POST["tournament"]
        club_name = None if "club" not in request.POST else request.POST["club"]
        if tournament_name and club_name:
            tournament = Tournament.objects.filter(club__name=club_name, name=tournament_name)
            if not tournament.exists():
                return HttpResponse(status=400)
            tournament = tournament.first()

            membership = ClubMembership.objects.filter(foreign_club__name=club_name, foreign_user=request.user)
            if not membership.exists():
                return HttpResponse(status=403)
            membership = membership.first()
            if membership.membership < ClubMembership.UserLevels.MEMBER:
                return HttpResponse(status=403)

            organizer = TournamentOrganizer.objects.filter(tournament=tournament, organizer=request.user)
            if organizer.exists():
                return HttpResponse(status=403)

            if datetime.now(tz=pytz.UTC) > tournament.signup_deadline:
                return HttpResponse(status=403)

            participants = TournamentParticipant.objects.filter(tournament=tournament)
            if participants.count() >= tournament.capacity:
                return HttpResponse(status=403)

            participation = participants.filter(participant=request.user)
            if participation.exists():
                participation.first().delete()
                return HttpResponse("0", content_type="text/plain")
            else:
                TournamentParticipant.objects.create(tournament=tournament, participant=request.user)
                return HttpResponse("1", content_type="text/plain")

    return HttpResponse(status=400)
