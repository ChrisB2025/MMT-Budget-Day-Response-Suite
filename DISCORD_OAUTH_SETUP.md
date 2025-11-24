# Discord OAuth Setup - Step-by-Step Guide

This guide provides detailed instructions for setting up Discord OAuth authentication for your application.

## Step 1: Access Discord Developer Portal

1. Open your web browser and go to: **https://discord.com/developers/applications**
2. Log in with your Discord account if you haven't already
3. You'll see the "Applications" page

## Step 2: Create a New Application

1. Click the **"New Application"** button (top right corner, blue button)
2. A dialog box will appear asking for an application name
3. Enter a name for your application (e.g., "MMT Budget Response Suite")
4. Check the box to agree to Discord's Developer Terms of Service and Developer Policy
5. Click **"Create"**

## Step 3: Get Your Application Credentials

After creating the application, you'll be on the "General Information" page:

1. You'll see **"APPLICATION ID"** near the top
   - This is your `DISCORD_OAUTH_CLIENT_ID`
   - Click the **"Copy"** button next to it to copy it
   - Save this somewhere safe (you'll need it later)

2. Scroll down slightly to find **"CLIENT SECRET"**
   - Click **"Reset Secret"** button (if you don't see a secret already)
   - A confirmation dialog will appear - click **"Yes, do it!"**
   - The secret will be displayed - it looks like a long random string
   - Click the **"Copy"** button to copy it
   - **IMPORTANT**: Save this immediately! You won't be able to see it again
   - This is your `DISCORD_OAUTH_CLIENT_SECRET`

## Step 4: Configure OAuth2 Settings

1. In the left sidebar, click on **"OAuth2"**
2. You'll see an "OAuth2" section with several options

### Add Redirect URIs:

1. Scroll down to the **"Redirects"** section
2. Click the **"Add Redirect"** button
3. For local development, add:
   ```
   http://localhost:8000/accounts/discord/login/callback/
   ```
4. Click **"Add Redirect"** again to add another redirect
5. For your Railway production URL, add (replace with your actual Railway domain):
   ```
   https://your-app-name.up.railway.app/accounts/discord/login/callback/
   ```

   **How to find your Railway domain:**
   - Go to your Railway dashboard
   - Click on your project
   - Look for the domain under "Settings" → "Domains"
   - It will look like: `your-app-name.up.railway.app`

6. Click **"Save Changes"** at the bottom of the page (green button)

## Step 5: Add Credentials to Railway

Now you need to add your Discord credentials to Railway as environment variables:

1. Go to your **Railway dashboard**: https://railway.app/dashboard
2. Click on your project (MMT Budget Response Suite)
3. Click on your service/deployment
4. Go to the **"Variables"** tab
5. Click **"+ New Variable"** and add each of these:

   **First Variable:**
   - Variable Name: `DISCORD_OAUTH_CLIENT_ID`
   - Variable Value: [Paste the APPLICATION ID you copied in Step 3]

   **Second Variable:**
   - Variable Name: `DISCORD_OAUTH_CLIENT_SECRET`
   - Variable Value: [Paste the CLIENT SECRET you copied in Step 3]

6. Click **"Add"** or **"Save"** after adding each variable
7. Railway will automatically redeploy your application with the new variables

## Step 6: Configure in Django Admin (After Deployment)

After your Railway app redeploys with the new environment variables:

1. Go to your Railway app URL: `https://your-app-name.up.railway.app/admin/`
2. Log in with your admin credentials
   - If you don't have an admin account, use the `/users/setup-admin/` endpoint to create one

3. **Configure the Site:**
   - Look for **"Sites"** in the Django admin
   - Click on it
   - You should see "example.com" - click to edit it
   - Change the **Domain name** to your Railway domain (e.g., `your-app-name.up.railway.app`)
   - Change the **Display name** to your app name (e.g., "MMT Budget Response Suite")
   - Click **"Save"**

4. **Add Discord Social Application:**
   - In Django admin, look for **"Social applications"** (under "Social Accounts")
   - Click **"Add social application"** (top right)
   - Fill in the form:
     - **Provider**: Select "Discord" from dropdown
     - **Name**: Enter "Discord" (or any name you prefer)
     - **Client id**: Paste your `APPLICATION ID` from Discord
     - **Secret key**: Paste your `CLIENT SECRET` from Discord
     - **Key**: Leave this empty
     - **Sites**:
       - You'll see two boxes: "Available sites" and "Chosen sites"
       - Find your site in "Available sites" (it should show your Railway domain)
       - Click on it, then click the arrow (→) to move it to "Chosen sites"
   - Click **"Save"**

## Step 7: Test Discord Login

1. Log out of your app if you're logged in
2. Go to the login page: `https://your-app-name.up.railway.app/users/login/`
3. You should see a **"Continue with Discord"** button (purple button)
4. Click it
5. You'll be redirected to Discord's authorization page
6. Discord will ask you to authorize the application
7. Click **"Authorize"**
8. You'll be redirected back to your app and logged in automatically

## Troubleshooting

### Error: "Redirect URI Mismatch"
- **Cause**: The redirect URI in your Discord app doesn't match exactly
- **Solution**:
  - Make sure the URL in Discord Developer Portal exactly matches: `https://your-actual-domain.up.railway.app/accounts/discord/login/callback/`
  - Note the trailing slash `/` - it's required!
  - The URL is case-sensitive
  - Make sure you're using `https://` for production (Railway), not `http://`

### Error: "SocialApp matching query does not exist"
- **Cause**: You haven't configured the Social Application in Django admin yet
- **Solution**: Follow Step 6 above to add the Discord social application

### Error: "Invalid client_id"
- **Cause**: The client ID in Railway environment variables doesn't match Discord
- **Solution**:
  - Double-check you copied the APPLICATION ID correctly
  - Make sure there are no extra spaces
  - Verify the environment variable name is exactly `DISCORD_OAUTH_CLIENT_ID`

### Error: "Invalid client_secret"
- **Cause**: The client secret is incorrect
- **Solution**:
  - Go back to Discord Developer Portal
  - Click "Reset Secret" to generate a new one
  - Update the `DISCORD_OAUTH_CLIENT_SECRET` in Railway
  - Update the secret in Django admin Social Application

### Button doesn't appear on login page
- **Cause**: Template might not be loaded correctly
- **Solution**:
  - Check Railway logs for any errors
  - Make sure django-allauth is installed (check requirements.txt)
  - Verify the app redeployed successfully after adding environment variables

## Security Notes

- **Never** commit your Client Secret to Git
- Use different Discord applications for development and production
- Regularly rotate your client secret (every 3-6 months)
- If your secret is compromised, reset it immediately in Discord Developer Portal and update it in Railway

## Getting Help

If you encounter issues:
1. Check Railway logs for error messages
2. Verify all environment variables are set correctly
3. Ensure your redirect URIs exactly match (including trailing slash)
4. Make sure the Social Application is configured in Django admin with the correct site

## Additional Discord Settings (Optional)

### Add an App Icon
1. In Discord Developer Portal, go to "General Information"
2. Click on the icon placeholder
3. Upload your app logo (recommended: 512x512 PNG)

### Add a Description
1. In "General Information"
2. Fill in the "Description" field
3. This will be shown to users when they authorize your app

### Set App Visibility
1. In "General Information"
2. Toggle "Public Bot" if you want others to see your app
3. For private apps, keep it off
