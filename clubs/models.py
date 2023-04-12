from django.core.exceptions import ValidationError

from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models

from django.contrib.auth.models import BaseUserManager

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin #define users with privilleges

from libgravatar import Gravatar


# A User Manager class required for stable functionality of custom User class
class UserManager(BaseUserManager):
    def _create_user(self, email, name, personal_statement, password, **extra_fields):
        '''Create and save a user with the given email, and
        password.
        '''
        if not email:
            raise ValueError('Users must have an email')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name = name,
            personal_statement = personal_statement,
            **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    #function for creating user of the system
    def create_user(self, email, name, personal_statement, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_admin', False)
        return self._create_user(email, name, personal_statement, password, **extra_fields)

    #function for creating superuser (administrator) of the system.
    def create_superuser(self, email, name, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('chess_experience', 'E')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must have is_staff=True.'
            )
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must have is_superuser=True.'
            )

        ps = 'boss doesn\'t need no personal statement'

        return self._create_user(email = email, name = name, personal_statement = ps, password = password, **extra_fields)


#User model
class User(AbstractBaseUser, PermissionsMixin):

    class ChessExperience(models.TextChoices):
        BEGINNER = 'B'
        INTERMEDIATE = 'I'
        ADVANCED = 'A'
        EXPERT = 'E'

    name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    bio = models.CharField(max_length=520, blank=True)
    personal_statement= models.CharField(max_length=4000, blank=True)
    chess_experience = models.CharField(max_length = 1, choices = ChessExperience.choices, blank = False)

    # Other fields declared in AbstractUser but not in AbstractBaseUser

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default = False)
    date_joined = models.DateTimeField(auto_now = False, auto_now_add = True, blank = False, editable = False)

    # Extra configs for a custom User model inheriting from AbstractBaseUser
    objects = UserManager()
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    # Config to set the fields requested on creating a superuser through manager.py createsuperuser
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

#Club-related models
class Club(models.Model):
    name = models.CharField(unique = True, max_length = 100, blank = False)
    location = models.CharField(unique = False, max_length = 180, blank = False)
    description = models.CharField(max_length = 200, blank = False)

    def __str__(self):
        return self.name


class ClubMembership(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['foreign_user', 'foreign_club'], name = 'unique_member')
        ]

    class UserLevels(models.IntegerChoices):
        REJECTED = -2
        PENDING = -1
        MEMBER = 0
        OFFICER = 1
        OWNER = 2

    foreign_user = models.ForeignKey(User, blank = False, null = False, on_delete = models.CASCADE)
    foreign_club = models.ForeignKey(Club, blank = False, null = False, on_delete = models.CASCADE)
    membership = models.IntegerField(choices = UserLevels.choices, blank = False, default = UserLevels.PENDING)

    def full_clean(self):
        super().full_clean()
        if self.membership == ClubMembership.UserLevels.OWNER:
            if len(ClubMembership.objects.filter(
                foreign_club = self.foreign_club,
                membership = ClubMembership.UserLevels.OWNER
            ).exclude(foreign_user = self.foreign_user)) > 0:
                raise ValidationError(message = 'A club can only have 1 owner')


class Application(models.Model):
    club_membership = models.ForeignKey(ClubMembership, blank = False, null = False, on_delete = models.CASCADE)
    user_personal_statement = models.CharField(max_length =4000, blank = False)


# Tournaments-related models
class Tournament(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['club', 'name'], name = 'unique_tournament_in_club'),
        ]

    club = models.ForeignKey(Club, blank = False, null = False, on_delete = models.CASCADE)
    name = models.CharField(unique = False, max_length = 100, blank = False)
    description = models.CharField(unique = False, max_length = 520, blank = False)
    signup_deadline = models.DateTimeField(blank = False)
    capacity = models.PositiveSmallIntegerField(blank = False, default = 2, validators = [MinValueValidator(2), MaxValueValidator(96)])

    def __str__(self):
        return f'"{self.name}" tournament at "{str(self.club)}"'


class TournamentOrganizer(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['tournament', 'organizer'], name = 'unique_organizer'),
        ]

    class OrganizingRoles(models.IntegerChoices):
        COORGANIZER = 0
        ORGANIZER = 1

    tournament = models.ForeignKey(Tournament, blank = False, null = False, on_delete = models.CASCADE)
    organizer = models.ForeignKey(User, blank = False, null = False, on_delete = models.CASCADE)
    organizing_role = models.IntegerField(choices = OrganizingRoles.choices, blank = False, default = OrganizingRoles.COORGANIZER)


class TournamentParticipant(models.Model):

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['tournament', 'participant'], name = 'unique_participation'),
        ]

    tournament = models.ForeignKey(Tournament, blank = False, null = False, on_delete = models.CASCADE)
    participant = models.ForeignKey(User, blank = False, null = False, on_delete = models.CASCADE)
