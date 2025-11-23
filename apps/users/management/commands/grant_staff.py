"""Management command to grant staff permissions to users"""
from django.core.management.base import BaseCommand
from apps.users.models import User


class Command(BaseCommand):
    help = 'Grant staff permissions to a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to grant staff permissions to')

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = User.objects.get(username=username)

            if user.is_staff:
                self.stdout.write(
                    self.style.WARNING(f'User "{username}" is already a staff member')
                )
            else:
                user.is_staff = True
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Successfully granted staff permissions to user "{username}"')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'  User can now access /admin/ and /admin-dashboard/')
                )

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" does not exist')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )
