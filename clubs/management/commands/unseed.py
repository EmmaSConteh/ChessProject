#unseeding any users and objects of the system from the database
from django.core.management.base import BaseCommand, CommandError
from clubs.models import User, Club, ClubMembership

class Command(BaseCommand):
    help = "Removes all non super users from the databse."

    def __init__(self):
        super().__init__()

    def handle(self, *args, **options):
        User.objects.filter(is_staff=False, is_superuser=False).delete()
        Club.objects.all().delete()
        ClubMembership.objects.all().delete()
