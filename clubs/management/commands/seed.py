#seeding random fake users and objects of the system into the database
import pytz
import random

from typing import List
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError

from faker import Faker
from faker.providers import internet
from faker.providers import person
from faker.providers import misc

from clubs.models import User, Club, ClubMembership, Tournament, TournamentOrganizer


class Command(BaseCommand):
    help = "Seeds fake data into the database."

    """The database seeder."""
    CHESS_EXPERIENCE = [
        User.ChessExperience.BEGINNER,
        User.ChessExperience.INTERMEDIATE,
        User.ChessExperience.ADVANCED,
        User.ChessExperience.EXPERT
    ]
    PASSWORD = "Password123"

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')
        self.faker.add_provider(internet)
        self.faker.add_provider(person)
        self.faker.add_provider(misc)

    def add_arguments(self, parser):
        parser.add_argument("--users", help="The amount of users to seed.")
        parser.add_argument("--clubs", help="The amount of clubs to seed.")
        parser.add_argument("--count", help="The amount of club memberships per user to seed.")
        parser.add_argument("--tournaments", help="The amount of tournaments to seed.")

    def to_int(self, word) -> int:
        try:
            return int(word)
        except:
            return -1

    def handle(self, *args, **options):
        u_count = max(1, 100 if options["users"] == None else self.to_int(options["users"]))
        c_count = max(1, 10 if options["clubs"] == None else self.to_int(options["clubs"]))
        a_count = max(-1, -1 if options["count"] == None else self.to_int(options["count"])) # -1 for random
        t_count = max(1, 10 if options["tournaments"] == None else self.to_int(options["tournaments"]))
        users = self.seed_users(u_count)
        clubs = self.seed_clubs(c_count)
        self.seed_users_into_clubs(users, clubs, a_count)
        self.seed_club_owners(users, clubs)
        tournaments = self.seed_tournaments(clubs, t_count)

        # Defaults
        j = self.seed_specific("Jebediah Kerman",  "jeb@example.org")
        v = self.seed_specific("Valentina Kerman",  "val@example.org")
        b = self.seed_specific("Billie Kerman",  "billie@example.org")
        try:
            c = Club.objects.create(name="Kerbal Chess Club", location="KCL", description="Default club.")
            self.seed_members(User.objects.first(), c, ClubMembership.UserLevels.OWNER)
            self.seed_members(j, c, ClubMembership.UserLevels.MEMBER)
            self.seed_members(v, c, ClubMembership.UserLevels.MEMBER)
            self.seed_members(b, c, ClubMembership.UserLevels.MEMBER)

            c1 = Club.objects.create(name="Club 1", location="KCL", description="Default club.")
            self.seed_members(User.objects.first(), c1, ClubMembership.UserLevels.OWNER)
            self.seed_members(j, c1, ClubMembership.UserLevels.OFFICER)

            c2 = Club.objects.create(name="Club 2", location="KCL", description="Default club.")
            self.seed_members(v, c2, ClubMembership.UserLevels.OWNER)

            c3 = Club.objects.create(name="Club 3", location="KCL", description="Default club.")
            self.seed_members(User.objects.first(), c3, ClubMembership.UserLevels.OWNER)
            self.seed_members(b, c3, ClubMembership.UserLevels.MEMBER)

        except Exception as e:
            print(e)

    def seed_specific(self, name: str, email: str):
        try:
            user = User.objects.create(
                name=name,
                email=email,
                password = Command.PASSWORD,
                personal_statement="statement",
                bio = "bio",
                chess_experience = random.choice(Command.CHESS_EXPERIENCE)
                )
            return user
        except:
            pass

    def seed_members(self, user, club, level):
        ClubMembership.objects.create(foreign_club=club, foreign_user=user, membership=level)

    #Using the package faker to seed random users into the system.
    def seed_users(self, n: int) -> List[User]:
        users = []
        for i in range(n):
            nameIn = self.faker.name()
            email_address = self.faker.unique.email(safe=False)
            bio_text = self.faker.text()
            if len(bio_text) > 520:
                bio_text = bio_text[0:520]
            ps = self.faker.text()
            if len(ps) > 520:
                ps = ps[0:520]
            chess_exp = random.choice(Command.CHESS_EXPERIENCE)
            print(f"Seeding user: {i+1}/{n}", end='\r')
            try:
                user = User.objects.create_user(
                    name = nameIn,
                    email = email_address,
                    password = Command.PASSWORD,
                    personal_statement = ps,
                    bio = bio_text,
                    chess_experience = chess_exp,
                )
                users.append(user)
            except:
                continue
        print(f"Seeded {len(users)} users.      ")
        return users

    #Using the package faker to seed random clubs into the system.
    def seed_clubs(self, n: int) -> List[Club]:
        clubs = []
        for i in range(n):
            nameIn = self.faker.name() + "'s Chess Club"
            loc = a if len(a := self.faker.address()) <= 180 else a[0:180]
            des = a if len(a := self.faker.text()) <= 200 else a[0:200]
            print(f"Seeding club: {i+1}/{n}", end='\r')
            try:
                club = Club.objects.create(name=nameIn, location=loc, description = des)
                clubs.append(club)
            except:
                continue
        print(f"Seeded {len(clubs)} clubs.      ")
        return clubs

    #Using the package faker to seed users into clubs in the system.
    def seed_users_into_clubs(self, users, clubs, application_count):
        count = 0
        if application_count == -1:
            for user in users:
                start = random.randint(0, len(clubs)-1)
                end = random.randint(start+1, len(clubs))
                for i in range(start, end):
                    new_membership = ClubMembership.objects.create(foreign_user=user, foreign_club=clubs[i], membership=random.randint(0, 3)-2)
                    count += 1
                    print(f"Weaved users into clubs {count} times.", end='\r')
        elif application_count != 0:
            application_count = min(application_count, len(clubs))
            for user in users:
                start = random.randint(0, len(clubs)-application_count)
                end = start + application_count
                for i in range(start, end):
                    new_membership = ClubMembership.objects.create(foreign_user=user, foreign_club=clubs[i], membership=random.randint(0, 3)-2)
                    count += 1
                    print(f"Weaved users into clubs {count} times.", end='\r')
        print(f"Seeded {count} memberships between {len(users)} users and {len(clubs)} clubs.       ")

    #Using the package faker to randomly assign users owner status.
    def seed_club_owners(self, users, clubs):
        for club in clubs:
            members = ClubMembership.objects.filter(foreign_club = club)
            if(members.exists()):
                owner = members[random.randint(0, members.count()-1)]
                owner.membership = ClubMembership.UserLevels.OWNER
                owner.save()
            else:
                owner = ClubMembership.objects.create(foreign_user=users[random.randint(0, len(users)-1)], foreign_club=club, membership=ClubMembership.UserLevels.OWNER)

    #Using the package faker to seed random tournaments into the system.
    def seed_tournaments(self, clubs, n: int) -> List[Tournament]:
        tournaments = []
        for club in clubs:
            owner = ClubMembership.objects.get(foreign_club=club, membership=ClubMembership.UserLevels.OWNER).foreign_user
            for i in range(n):
                tournamentName = self.faker.name() + "'s Tournament"
                des = a if len(a := self.faker.text()) <= 200 else a[0:200]
                date = self.faker.date_time(tzinfo=pytz.UTC)
                print(f"Seeding tournament: {i+1}/{n*len(clubs)}", end='\r')
                try:
                    tournament = Tournament.objects.create(club=club, name=tournamentName, description = des, signup_deadline=date)
                    TournamentOrganizer.objects.create(tournament=tournament, organizer=owner, organizing_role=TournamentOrganizer.OrganizingRoles.ORGANIZER)
                    tournaments.append(tournament)
                except:
                    continue
        print(f"Seeded {len(tournaments)} tournaments.      ")
        return tournaments
