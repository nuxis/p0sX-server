from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from pos.models.user import User
from pyGE import GE

class Command(BaseCommand):
    help = 'Import crewmembers from Geekevents'

    def add_arguments(self, parser):
        parser.add_argument('--party', dest='party', nargs=1,
            help='Party on GeekEvents')
        parser.add_argument('--username', dest='username', nargs=1,
            help='GE API username')
        parser.add_argument('--password', dest='password', nargs=1,
            help='GE API password')

    def handle(self, *args, **options):
        party = options['party'][0]
        username = options['username'][0]
        password = options['password'][0]

        ge = GE(
            party=party,
            user=username,
            password=password
        )
        
        crew = ge.get_crew()

        for id, data in crew.items():
            try:
                user = User.objects.get(card=data['user_card'])
            except ObjectDoesNotExist:
                if not data['user_card']:
                    continue
                user = User(
                    card=data['user_card'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    phone=data['phone'],
                    crew=data['crew'],
                    role=data['role'],
                    email=data['email'],
                    max_credit=0
                )
                user.save()
                print('Added new user {} {}'.format(data['first_name'], data['last_name']))

