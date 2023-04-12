import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import redirect, render
from clubs.models import User, ClubMembership, Club, Application, Tournament, TournamentOrganizer, TournamentParticipant


@login_required
def get_user_application(request):
    if request.method == "GET":
        user_email = None if "email" not in request.GET else request.GET["email"]
        club_name = None if "name" not in request.GET else request.GET["name"]
        if not (user_email and club_name):
            return HttpResponse(status=400)
        my_membership = ClubMembership.objects.filter(foreign_user=request.user, foreign_club__name=club_name)
        if not my_membership.exists():
            return HttpResponse(status=403)
        if my_membership.first().membership <= ClubMembership.UserLevels.MEMBER:
            return HttpResponse(status=403)
        membership = ClubMembership.objects.filter(foreign_user__email=user_email, foreign_club__name=club_name)
        if not membership.exists():
            return HttpResponse(status=404)
        return render(request, "application.html", {"membership": membership.first()})
    return HttpResponse(status=400)