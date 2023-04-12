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
from clubs.models import User, ClubMembership, Club, Application, Tournament
from clubs.helpers import login_prohibited
from django.contrib.auth.forms import UserChangeForm
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView, UpdateView
from clubs.views.mixins import LoginProhibitedMixin

class IndexView(LoginProhibitedMixin, View):
    redirect_when_logged_in_url = reverse_lazy('home')

    http_method_names = ['get']

    def get(self, request):
        return render(request, 'index.html')


def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse('profile'))
    else:
        form = EditProfileForm(instance=request.user)
    args = {'form': form}
    return render(request, 'edit_profile.html', args)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """View to update logged-in user's profile."""

    model = EditProfileForm
    template_name = "profile.html"
    form_class = EditProfileForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


class PasswordView(LoginRequiredMixin, FormView):
    """View that handles password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('profile')

@login_required
def profile(request):
    # try:
    #user = User.objects.get(id=user_id)
    email = request.user.email
    chess_experience = request.user.chess_experience
    bio = request.user.bio
    personal_statement = request.user.personal_statement
    # except ObjectDoesNotExist:
    #   return redirect('log_in')
    # else:
    return render(request, 'profile.html',{
    #'Name': user,
        'Email': email,
        'Experience': chess_experience,
        'Biography':bio,
        'Personal Statement':personal_statement})
