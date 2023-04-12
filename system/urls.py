"""system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from clubs import views

apipatterns = [
    path('club/users', views.get_club, name="club"),
    path("club/pending", views.get_club_pending_members, name="pending_applications"),
    path("club/submit", views.post_join_club, name="submit_application"),
    path("club/change_rank", views.post_change_rank, name="change_rank"),
    path("club/tournaments", views.get_club_tournaments, name="club_tournaments"),
    path('applications', views.get_applications, name="applications"),
    path("tournament/toggle", views.post_toggle_tournament, name="toggle_tournament"),
    path('club/tournament/manage_coorganizers', views.ManageTournamentCoorganizers.as_view(), name='manage_tournament_coorganizers')
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('profile/edit', views.edit_profile, name='edit_profile'),
    path('', views.IndexView.as_view(), name="index"),
    path('home/', views.home, name="home"),
    path("clubs/", views.clubs_view, name="clubs"),
    path("club", views.club_profile, name="club_profile"),
    path("club/application", views.get_user_application, name="club_application"),
    path("create_club/", views.create_club, name="create_club"),
    path("create_tournament/", views.create_tournament, name="create_tournament"),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('profile/edit', views.edit_profile, name='edit_profile'),
    path('tournament/', views.get_club_tournament, name='club_tournament'),
    path('tournaments/', views.tournaments_view, name='tournament'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('club/manage_tournament', views.ManageTournamentView.as_view(), name = 'manage_tournament')
]

for url in apipatterns:
    urlpatterns.append(url)
