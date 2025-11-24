"""
Custom django-allauth adapters for handling social account signup.
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to handle social account data during signup.
    """

    def populate_user(self, request, sociallogin, data):
        """
        Populate user instance with data from social login.
        Automatically set display_name from social account data.
        """
        user = super().populate_user(request, sociallogin, data)

        # Try to get display name from various social account fields
        if not user.display_name:
            # Try name field first (most providers)
            if data.get('name'):
                user.display_name = data.get('name')
            # Try first_name + last_name
            elif user.first_name and user.last_name:
                user.display_name = f"{user.first_name} {user.last_name}"
            # Try first_name only
            elif user.first_name:
                user.display_name = user.first_name
            # Try username from social provider
            elif data.get('username'):
                user.display_name = data.get('username')
            # Fall back to the generated username
            else:
                user.display_name = user.username

        return user

    def save_user(self, request, sociallogin, form=None):
        """
        Save the user after social login.
        """
        user = super().save_user(request, sociallogin, form)

        # Ensure display_name is set
        if not user.display_name:
            extra_data = sociallogin.account.extra_data

            # Google provider
            if sociallogin.account.provider == 'google':
                user.display_name = extra_data.get('name', user.username)

            # Discord provider
            elif sociallogin.account.provider == 'discord':
                # Discord provides username or global_name
                user.display_name = extra_data.get('global_name') or \
                                   extra_data.get('username') or \
                                   user.username

            # Other providers
            else:
                user.display_name = user.username

            user.save()

        return user


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter for account handling.
    """

    def get_login_redirect_url(self, request):
        """
        Redirect to dashboard after login.
        """
        return '/dashboard/'
