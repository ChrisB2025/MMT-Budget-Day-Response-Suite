"""Management command to grant superuser permissions to users"""
from django.core.management.base import BaseCommand
from apps.users.models import User


class Command(BaseCommand):
    help = 'Grant superuser (admin) permissions to a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to grant superuser permissions to')

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = User.objects.get(username=username)

            if user.is_superuser and user.is_staff:
                self.stdout.write(
                    self.style.WARNING(f'User "{username}" is already a superuser')
                )
            else:
                user.is_staff = True
                user.is_superuser = True
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Successfully granted superuser permissions to user "{username}"')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'  User now has FULL admin access to:')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'    - Django Admin (/admin/)')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'    - Admin Dashboard (/admin-dashboard/)')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'    - All database models and permissions')
                )

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" does not exist')
            )

            # List available users
            all_users = User.objects.all().values_list('username', 'email', flat=False)
            if all_users:
                self.stdout.write(self.style.WARNING('\nAvailable users:'))
                for u in all_users:
                    self.stdout.write(f'  - Username: {u[0]}, Email: {u[1]}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )
