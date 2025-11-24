# Google OAuth Setup - Step-by-Step Guide

This guide provides detailed instructions for setting up Google OAuth authentication for your application **as an individual** (you don't need to be an organization).

## Step 1: Access Google Cloud Console

1. Open your web browser and go to: **https://console.cloud.google.com/**
2. Log in with your personal Google account
3. Accept the Terms of Service if prompted

## Step 2: Create a New Project

1. At the top of the page, click on the project dropdown (it might say "Select a project")
2. In the dialog that appears, click **"NEW PROJECT"** (top right)
3. Enter a project name (e.g., "MMT Budget Response Suite")
4. Leave the organization field as "No organization" (this is fine for individuals!)
5. Click **"Create"**
6. Wait a few seconds for the project to be created
7. Make sure your new project is selected (check the project name at the top)

## Step 3: Configure OAuth Consent Screen

**IMPORTANT**: Choose "External" - this allows ANY Google user to sign in (perfect for individuals!)

1. In the left sidebar, click on **"APIs & Services"**
   - If you don't see the sidebar, click the ☰ (hamburger menu) in the top left
2. Click **"OAuth consent screen"** in the submenu
3. You'll see two options:

   ### Choose User Type:
   - ⚪ **Internal** - Only for Google Workspace organizations (you can't use this as an individual)
   - 🔵 **External** - For anyone with a Google account ← **SELECT THIS ONE**

4. Click **"External"**, then click **"Create"**

### Configure the Consent Screen:

You'll now go through a multi-step form:

#### **Step 1: OAuth consent screen**

Fill in the required fields:

1. **App name**: Enter your app name (e.g., "MMT Budget Response Suite")
2. **User support email**: Select your email from the dropdown
3. **App logo**: (Optional) You can upload a logo later
4. **App domain** section: (Optional for testing, you can skip for now)
5. **Authorized domains**: (Optional for testing)
6. **Developer contact information**: Enter your email address
7. Click **"Save and Continue"**

#### **Step 2: Scopes**

1. Click **"Add or Remove Scopes"**
2. In the dialog, scroll down or search for:
   - ☑️ `.../auth/userinfo.email` - View your email address
   - ☑️ `.../auth/userinfo.profile` - See your personal info
   - ☑️ `openid` - Associate you with your personal info on Google
3. These should show as "Non-sensitive" scopes
4. Click **"Update"** at the bottom
5. Click **"Save and Continue"**

#### **Step 3: Test users** (Important!)

Since you selected "External" and your app is in testing mode:

1. Click **"Add Users"**
2. Enter your email address (and any other emails you want to test with)
3. Click **"Add"**
4. Click **"Save and Continue"**

**Note**: While in "Testing" mode, only these test users can log in. This is fine for development. To make it public later, you'll need to publish the app (we'll cover this later).

#### **Step 4: Summary**

1. Review your settings
2. Click **"Back to Dashboard"**

## Step 4: Create OAuth Credentials

1. In the left sidebar, click **"Credentials"**
2. At the top, click **"+ Create Credentials"**
3. Select **"OAuth client ID"** from the dropdown

### Configure OAuth Client:

1. **Application type**: Select **"Web application"**
2. **Name**: Enter a name (e.g., "Web client for MMT Budget")

3. **Authorized JavaScript origins**: (Optional, can skip)

4. **Authorized redirect URIs**:
   - Click **"+ Add URI"**
   - For local development, add:
     ```
     http://localhost:8000/accounts/google/login/callback/
     ```
   - Click **"+ Add URI"** again
   - For your Railway production URL, add (replace with your actual domain):
     ```
     https://your-app-name.up.railway.app/accounts/google/login/callback/
     ```

   **How to find your Railway domain:**
   - Go to Railway dashboard → Your project → Settings → Domains
   - Copy the domain (e.g., `your-app-name.up.railway.app`)

5. Click **"Create"**

### Save Your Credentials:

A dialog will appear with your credentials:

1. **Your Client ID**: A long string ending in `.apps.googleusercontent.com`
   - Click **"Copy"** and save this - this is your `GOOGLE_OAUTH_CLIENT_ID`

2. **Your Client Secret**: A shorter random string
   - Click **"Copy"** and save this - this is your `GOOGLE_OAUTH_CLIENT_SECRET`

3. Click **"OK"**

**IMPORTANT**: Save both of these somewhere safe! You can always view them again on the Credentials page, but save them now.

## Step 5: Add Credentials to Railway

1. Go to **Railway dashboard**: https://railway.app/dashboard
2. Click on your project
3. Click on your service/deployment
4. Go to the **"Variables"** tab
5. Click **"+ New Variable"** and add:

   **First Variable:**
   - Variable Name: `GOOGLE_OAUTH_CLIENT_ID`
   - Variable Value: [Paste your Client ID from Step 4]

   **Second Variable:**
   - Variable Name: `GOOGLE_OAUTH_CLIENT_SECRET`
   - Variable Value: [Paste your Client Secret from Step 4]

6. Railway will automatically redeploy your app

## Step 6: Configure in Django Admin

After Railway redeploys:

1. Go to: `https://your-app-name.up.railway.app/admin/`
2. Log in with admin credentials

### Configure Site:

1. Click on **"Sites"**
2. Click on "example.com" to edit
3. Change:
   - **Domain name**: Your Railway domain (e.g., `your-app-name.up.railway.app`)
   - **Display name**: Your app name
4. Click **"Save"**

### Add Google Social Application:

1. Find **"Social applications"** (under "Social Accounts")
2. Click **"Add social application"**
3. Fill in:
   - **Provider**: Select "Google"
   - **Name**: "Google"
   - **Client id**: Paste your Client ID (ends in `.apps.googleusercontent.com`)
   - **Secret key**: Paste your Client Secret
   - **Key**: Leave empty
   - **Sites**: Move your Railway site from "Available sites" to "Chosen sites"
4. Click **"Save"**

## Step 7: Test Google Login

1. Go to: `https://your-app-name.up.railway.app/users/login/`
2. Click **"Continue with Google"** button
3. Select your Google account
4. You'll see the consent screen - click **"Continue"**
5. You should be redirected back and logged in!

## Publishing Your App (Optional - For Public Access)

While in "Testing" mode, only test users can log in. To allow anyone to log in:

1. Go to Google Cloud Console → OAuth consent screen
2. Click **"Publish App"**
3. Click **"Confirm"**

**Note**: For testing/development, you don't need to publish. Just add test users as needed.

For production apps with many users, Google may require app verification. This process can take several days and requires:
- A homepage URL
- Privacy policy
- Terms of service

## Troubleshooting

### Error: "Access blocked: This app's request is invalid"
- **Cause**: Redirect URI mismatch
- **Solution**:
  - Ensure the URI in Google Cloud Console exactly matches
  - Include the trailing slash: `/accounts/google/login/callback/`
  - Use `https://` for production, not `http://`

### Error: "Access blocked: Authorization Error - Error 403: access_denied"
- **Cause**: Your email is not in the test users list
- **Solution**:
  - Go to OAuth consent screen → Test users
  - Add your email address
  - Try again

### Error: "The OAuth client was deleted"
- **Cause**: Project or credentials were deleted
- **Solution**: Create new credentials (Step 4)

### Error: "redirect_uri_mismatch"
- **Cause**: The redirect URI doesn't match exactly
- **Solution**:
  - Check Google Cloud Console → Credentials → Your OAuth client
  - Verify the URI: `https://your-domain.up.railway.app/accounts/google/login/callback/`
  - Make sure there are no typos and the trailing slash is present

### "SocialApp matching query does not exist"
- **Cause**: Not configured in Django admin
- **Solution**: Complete Step 6

### Can't see the Google login button
- **Cause**: Template not loaded or app not redeployed
- **Solution**:
  - Check Railway deployment logs
  - Verify environment variables are set
  - Make sure the latest code is deployed

## Quota and Limits

Google OAuth has generous free tier limits:
- **10,000** requests per day (OAuth)
- **50** requests per user per day

For most applications, this is more than enough.

## Security Best Practices

- Never commit credentials to Git (already configured in .gitignore)
- Use different projects for development and production
- Regularly review authorized users in Google Cloud Console
- If credentials are compromised, delete them and create new ones immediately
- Enable 2-factor authentication on your Google account

## Need Help?

- **Google Cloud Console**: https://console.cloud.google.com/
- **OAuth Playground** (for testing): https://developers.google.com/oauthplayground/
- Check Railway logs for detailed error messages
- Verify all redirect URIs match exactly (case-sensitive, include trailing slash)

## Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [django-allauth Google Provider Docs](https://django-allauth.readthedocs.io/en/latest/providers.html#google)
