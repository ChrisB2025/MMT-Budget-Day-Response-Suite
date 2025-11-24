# OAuth Setup Guide

This guide explains how to set up Google and Discord OAuth for single sign-on (SSO) authentication.

## Quick Links to Detailed Guides

- **[Discord OAuth Setup (Detailed Step-by-Step)](DISCORD_OAUTH_SETUP.md)** ← Start here for Discord
- **[Google OAuth Setup (Detailed Step-by-Step)](GOOGLE_OAUTH_SETUP.md)** ← Start here for Google

## Prerequisites

- Django application deployed (e.g., on Railway)
- Personal Google account (no organization required!)
- Discord account

**Note for Individuals**: You CAN use Google OAuth without being an organization! Just select "External" user type when setting up (see detailed guide).

## Google OAuth Setup

### 1. Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to **APIs & Services** > **Credentials**
4. Click **Create Credentials** > **OAuth 2.0 Client ID**
5. Configure the OAuth consent screen if prompted:
   - User Type: External (for public access) or Internal (for organization only)
   - Fill in required app information
   - Add scopes: `profile` and `email`
6. Select Application type: **Web application**
7. Add authorized redirect URIs:
   ```
   http://localhost:8000/accounts/google/login/callback/
   https://yourdomain.com/accounts/google/login/callback/
   ```
8. Click **Create**
9. Copy the **Client ID** and **Client Secret**

### 2. Add Credentials to Environment

Add to your `.env` file:
```bash
GOOGLE_OAUTH_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret-here
```

## Discord OAuth Setup

### 1. Create Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application**
3. Give your application a name
4. Navigate to **OAuth2** in the sidebar
5. Add redirect URIs:
   ```
   http://localhost:8000/accounts/discord/login/callback/
   https://yourdomain.com/accounts/discord/login/callback/
   ```
6. Copy the **Client ID** and **Client Secret** from the OAuth2 page

### 2. Add Credentials to Environment

Add to your `.env` file:
```bash
DISCORD_OAUTH_CLIENT_ID=your-discord-client-id-here
DISCORD_OAUTH_CLIENT_SECRET=your-discord-client-secret-here
```

## Run Migrations

After setting up the credentials, run migrations to create the necessary database tables:

```bash
python manage.py migrate
```

## Configure Social Applications (Admin Panel)

After running migrations, you need to configure the social applications in Django admin:

1. Run the development server: `python manage.py runserver`
2. Log in to Django admin: `http://localhost:8000/admin/`
3. Navigate to **Sites** and ensure there's a site with domain `localhost:8000` (for development) or your production domain
4. Navigate to **Social Applications** and add applications for Google and Discord:

### Google Configuration:
- Provider: Google
- Name: Google
- Client id: (from .env)
- Secret key: (from .env)
- Sites: Select your site

### Discord Configuration:
- Provider: Discord
- Name: Discord
- Client id: (from .env)
- Secret key: (from .env)
- Sites: Select your site

## Testing

1. Visit `http://localhost:8000/users/login/`
2. You should see "Continue with Google" and "Continue with Discord" buttons
3. Click either button to test the OAuth flow
4. After successful authentication, you'll be redirected to the dashboard

## Troubleshooting

### Redirect URI Mismatch
- Ensure the redirect URIs in Google/Discord match exactly with your application URLs
- Common format: `http://localhost:8000/accounts/{provider}/login/callback/`

### Missing Site Configuration
- Check that `SITE_ID = 1` is set in settings
- Verify a site exists in Django admin with the correct domain

### OAuth Errors
- Check that credentials are correctly set in `.env`
- Verify the `.env` file is being loaded by Django
- Check Django logs for detailed error messages

### User Creation Issues
- Ensure `SOCIALACCOUNT_AUTO_SIGNUP = True` in settings
- Check that email addresses from OAuth providers are unique

## Security Notes

- Never commit `.env` file to version control
- Use different OAuth credentials for development and production
- Enable HTTPS in production (required by most OAuth providers)
- Regularly rotate OAuth secrets
- Review OAuth scopes to request only necessary permissions

## Additional Configuration

### Custom User Model
The application uses a custom User model with additional fields:
- `display_name`: Display name for the user
- `team`: Optional team assignment
- `points`: Gamification points

When users sign in via OAuth, a username will be generated automatically if not provided.

### Email Verification
Currently set to `optional`. To require email verification:
```python
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
```

### Profile Information
Users can update their profile at `/users/profile/` to add display name and other information.
