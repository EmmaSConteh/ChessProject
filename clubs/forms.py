"""Forms for the microblogs app."""
from django import forms
from django.contrib.auth import authenticate
from .models import User, Club, Tournament, ClubMembership, TournamentOrganizer, TournamentParticipant
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserChangeForm
from django.contrib.admin import widgets

import operator
from django.db.models import Q
from functools import reduce

#form enabling registered users to log in
class LogInForm(forms.Form):

    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        #Returns authenticate user if possible

        user = None
        if self.is_valid():
            email = self.cleaned_data.get('email')
            password = self.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
        return user

class CreateClubForm(forms.ModelForm):
    #Form allowing to create new clubs
    class Meta:
        model = Club
        fields =['name','location','description']
        widgets = {'description': forms.Textarea()}


class CreateTournamentForm(forms.ModelForm):
    #Form allowing new tournaments
    class Meta:
        model = Tournament
        fields =['club', 'name', 'description', 'signup_deadline', 'capacity']
        widgets = {'description': forms.Textarea()}

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        cm = ClubMembership.objects.filter(foreign_user = user, membership__gte = ClubMembership.UserLevels.OFFICER)
        list = []
        for clubs in cm:
            list.append(clubs.foreign_club.id)

        self.fields['club'].queryset = Club.objects.filter(id__in=list)


    def clean(self):
        super().clean()

    def save(self):
        super().save(commit = False)
        tournament = Tournament(
            club = self.cleaned_data.get('club'),
            name = self.cleaned_data.get('name'),
            signup_deadline = self.cleaned_data.get('signup_deadline'),
            description = self.cleaned_data.get('description'),
            capacity = self.cleaned_data.get('capacity')
        )
        tournament.save()
        return tournament

class SignUpForm(forms.ModelForm):
    #Form enabling unregistered users to sign up.

    class Meta:
        """Form options."""
        model = User
        fields = ['name', 'email', 'bio', 'chess_experience', 'personal_statement']
        widgets = {'bio': forms.Textarea()}

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        #Clean the data and generate messages for any errors.

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

    def save(self):
        #Create a new user.

        super().save(commit=False)
        user = User.objects.create_user(
            name=self.cleaned_data.get('name'),
            email=self.cleaned_data.get('email'),
            bio=self.cleaned_data.get('bio'),
            password=self.cleaned_data.get('new_password'),
            chess_experience=self.cleaned_data.get('chess_experience'),
            personal_statement=self.cleaned_data.get('personal_statement'),
        )
        return user

class EditProfileForm(forms.ModelForm):
    template_name='/something/else'

    class Meta:
        model = User
        fields = (
            'email',
            'bio',
            'chess_experience',
            'personal_statement',
        )

class NewPasswordMixin(forms.Form):
    #Form mixing for new_password and password_confirmation fields.

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        #Form mixing for new_password and password_confirmation fields.

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    #Form enabling users to change their password.

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        #Construct new form instance with a user instance.

        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        #Clean the data and generate messages for any errors.

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(email=self.user.email, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        #Save the user's new password.

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class TournamentOrganizerForm(forms.ModelForm):
    class Meta:
        model = TournamentOrganizer
        fields = ['organizer']
        labels = {'organizer': 'Add Co-organizers'}

    def __init__(self, *args, **kwargs):
        tournament = kwargs.pop('tournament')
        # print('here')
        super().__init__(*args, **kwargs)
        # print('after')

        # get officers and owner of the club where the tournament is held
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

        self.fields['organizer'].queryset = User.objects.filter(id__in = officers_list)

        self.tournament = tournament
        self.organizing_role = TournamentOrganizer.OrganizingRoles.COORGANIZER

    def is_valid(self):
        valid = super().is_valid()
        # print('finished super: ' + str(valid))
        if not valid:
            # print('printing errors now')
            print(self.errors)
            print(self.non_field_errors)
        try:
            self.tournament.full_clean()
        except ValidationError:
            valid = False

        choices = []
        for choice in TournamentOrganizer.OrganizingRoles.choices:
            choices.append(choice[0])

        if not self.organizing_role in choices:
            valid = False

        # print('passed all')
        return valid

    def save(self):
        super().save(commit = False)
        tournament_organizer = TournamentOrganizer(
            tournament = self.tournament,
            organizer = self.cleaned_data['organizer'],
            organizing_role = self.organizing_role
        )
        tournament_organizer.save()
        return tournament_organizer
