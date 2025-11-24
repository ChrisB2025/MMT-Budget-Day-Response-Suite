# Railway OAuth Quick Start Guide

This is a condensed guide specifically for setting up OAuth on Railway. No local setup needed!

## Overview

Since you're using Railway and don't have local Python setup, all configuration is done through:
1. OAuth provider websites (Google/Discord)
2. Railway dashboard (environment variables)
3. Your deployed app's Django admin panel

## Prerequisites

✅ Your app is deployed on Railway
✅ You know your Railway app URL (e.g., `https://your-app-name.up.railway.app`)
✅ You have admin access to your Django app

---

## Part 1: Set Up Discord OAuth (Recommended to start with this one)

### A. Create Discord Application (5 minutes)

1. Go to: **https://discord.com/developers/applications**
2. Click **"New Application"**
3. Name it (e.g., "MMT Budget Suite") → **Create**
4. Copy the **APPLICATION ID** → Save it as `DISCORD_CLIENT_ID`
5. Click **"Reset Secret"** → Copy it → Save as `DISCORD_CLIENT_SECRET`
6. Go to **"OAuth2"** in left sidebar
7. Under **"Redirects"**, click **"Add Redirect"** and add:
   ```
   https://your-app-name.up.railway.app/accounts/discord/login/callback/
   ```
   ⚠️ Replace `your-app-name.up.railway.app` with your actual Railway domain
8. Click **"Save Changes"**

### B. Add to Railway (2 minutes)

1. Go to **Railway dashboard** → Your project → Your service
2. Click **"Variables"** tab
3. Add two new variables:
   - Name: `DISCORD_OAUTH_CLIENT_ID` → Value: [paste APPLICATION ID]
   - Name: `DISCORD_OAUTH_CLIENT_SECRET` → Value: [paste SECRET]
4. Railway will auto-redeploy (wait 1-2 minutes)

### C. Configure in Django Admin (3 minutes)

1. Go to: `https://your-app-name.up.railway.app/admin/`
2. Log in

**Set up Site:**
- Click **"Sites"** → Edit "example.com"
- Domain: `your-app-name.up.railway.app` (no https://)
- Save

**Add Discord App:**
- Click **"Social applications"** → **"Add social application"**
- Provider: **Discord**
- Name: **Discord**
- Client id: [paste your DISCORD_CLIENT_ID]
- Secret key: [paste your DISCORD_CLIENT_SECRET]
- Sites: Move your Railway site to "Chosen sites" →
- **Save**

### D. Test It! (1 minute)

1. Go to: `https://your-app-name.up.railway.app/users/login/`
2. Click **"Continue with Discord"** (purple button)
3. Authorize → You're logged in! ✅

**[Full Discord Guide →](DISCORD_OAUTH_SETUP.md)**

---

## Part 2: Set Up Google OAuth

### A. Create Google Project (10 minutes)

1. Go to: **https://console.cloud.google.com/**
2. Click project dropdown → **"NEW PROJECT"**
3. Name it → Leave organization as "No organization" → **Create**

**Configure OAuth Consent:**
4. Menu → **APIs & Services** → **OAuth consent screen**
5. Select **"External"** (⚠️ This is the key - allows anyone with Google account!)
6. **Create**

Fill in:
- App name: Your app name
- User support email: Your email
- Developer contact: Your email
- **Save and Continue**

Add Scopes:
- **Add or Remove Scopes**
- Select: `userinfo.email`, `userinfo.profile`, `openid`
- **Update** → **Save and Continue**

Add Test Users (while in testing):
- **Add Users** → Enter your email
- **Save and Continue**

### B. Create Credentials (5 minutes)

1. **Credentials** (left sidebar) → **Create Credentials** → **OAuth client ID**
2. Type: **Web application**
3. Name: "Web client"
4. **Authorized redirect URIs** → **Add URI**:
   ```
   https://your-app-name.up.railway.app/accounts/google/login/callback/
   ```
5. **Create**
6. Copy **Client ID** (ends in `.apps.googleusercontent.com`)
7. Copy **Client Secret**

### C. Add to Railway (2 minutes)

Railway dashboard → Variables:
- `GOOGLE_OAUTH_CLIENT_ID` → [paste Client ID]
- `GOOGLE_OAUTH_CLIENT_SECRET` → [paste Secret]

Wait for redeploy.

### D. Configure in Django Admin (2 minutes)

1. `https://your-app-name.up.railway.app/admin/`
2. **Social applications** → **Add**
   - Provider: **Google**
   - Name: **Google**
   - Client id: [paste Client ID]
   - Secret key: [paste Client Secret]
   - Sites: Select your site →
   - **Save**

### E. Test It!

1. Login page → **"Continue with Google"**
2. Select your Google account
3. **Continue** → Logged in! ✅

**[Full Google Guide →](GOOGLE_OAUTH_SETUP.md)**

---

## Important Notes

### About Google "External" User Type

- ✅ **You CAN use this as an individual!**
- You don't need to be an organization
- "External" = Anyone with a Google account can sign in
- "Internal" = Only for Google Workspace organizations (you can't use this)

### While in Testing Mode

- Google: Only emails you added as "test users" can log in
- To make public: OAuth consent screen → **Publish App**
- For personal/small apps, testing mode is fine - just add users as needed

### Finding Your Railway Domain

Railway Dashboard → Your Project → Settings → Domains

It looks like: `app-name-production-abc123.up.railway.app`

### Common Issues

**"Redirect URI mismatch"**
→ Make sure URI in provider exactly matches Railway domain, including `/accounts/{provider}/login/callback/`

**"SocialApp matching query does not exist"**
→ You didn't configure it in Django admin (Part C)

**Button doesn't appear**
→ Check Railway logs, make sure variables are set, app redeployed

**"Access denied: Error 403" (Google)**
→ Add your email to test users in Google Cloud Console

---

## Checklist

### For Discord:
- [ ] Created Discord app
- [ ] Got APPLICATION ID and SECRET
- [ ] Added redirect URI
- [ ] Added to Railway variables
- [ ] Configured in Django admin (Site + Social App)
- [ ] Tested login

### For Google:
- [ ] Created Google project
- [ ] Selected "External" user type ⭐
- [ ] Configured consent screen
- [ ] Added test users
- [ ] Created OAuth credentials
- [ ] Added to Railway variables
- [ ] Configured in Django admin
- [ ] Tested login

---

## Need More Details?

- **[Discord: Full Step-by-Step Guide](DISCORD_OAUTH_SETUP.md)**
- **[Google: Full Step-by-Step Guide](GOOGLE_OAUTH_SETUP.md)**
- **[General OAuth Info](OAUTH_SETUP.md)**

## Getting Help

1. Check Railway logs for errors
2. Verify environment variables are exactly correct (no extra spaces)
3. Make sure redirect URIs match exactly (case-sensitive, include trailing slash)
4. Ensure Django admin Social Application is configured with correct site

---

**Estimated Total Time:**
- Discord: ~15 minutes
- Google: ~20 minutes
- Both: ~35 minutes

Good luck! 🚀
