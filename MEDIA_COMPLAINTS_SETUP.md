# Media Complaints Platform - Setup & Usage Guide

## Overview

The **Media Complaints Platform** is a Python/Django port of the [mmt-complainer-bot](https://github.com/ChrisB2025/mmt-complainer-bot), integrated into the MMT Budget Day Response Suite. It enables users to file complaints about economic misinformation in UK media outlets and generates AI-powered complaint letters with MMT perspective.

## What It Does

- **Report Misinformation**: Users can log instances of economic misinformation from TV, radio, print, and online media
- **AI Letter Generation**: Uses Claude AI to generate professional complaint letters with MMT educational content
- **Letter Variation**: Each letter is varied to avoid detection as form letters using different:
  - Rhetorical strategies (correction, training, policy review, investigation, accountability)
  - Tones (professional, academic, passionate)
  - Structure and emphasis
- **Email Integration**: Send complaints directly to media outlets
- **Community Features**: View community complaints, statistics, and track responses
- **Gamification**: Integrated with the existing user stats system

## Key Features Ported from TypeScript

✅ **Media Outlet Database**: Pre-seeded with 19 UK media outlets (BBC, ITV, Sky, Guardian, Times, etc.)
✅ **Incident Tracking**: Hash-based deduplication to track multiple complaints about same incident
✅ **Variation Strategies**: 5 different rhetorical approaches that cycle based on complaint number
✅ **Tone Options**: Professional, academic, or passionate letter styles
✅ **MMT Education**: Letters include MMT talking points to educate journalists
✅ **Response Tracking**: Track when outlets respond to complaints

## Architecture

### Models (`apps/media_complaints/models.py`)

1. **MediaOutlet** - Media organizations (BBC, Guardian, etc.)
   - name, media_type, contact_email, complaints_dept_email
   - regulator (Ofcom, IPSO)
   - Pre-seeded with 19 UK outlets

2. **Complaint** - User-submitted complaint
   - outlet, incident_date, programme_name, presenter_journalist
   - claim_description, context, severity (1-5)
   - preferred_tone, status (draft/pending/generated/sent)
   - incident_hash (for tracking duplicate complaints)
   - complaint_number_for_incident (for variation)

3. **ComplaintLetter** - AI-generated letter
   - subject, body
   - variation_strategy (correction/training/policy/investigation/accountability)
   - tone_used, mmt_points_included
   - sent_at, sent_to_email
   - response tracking

4. **ComplaintStats** - User statistics
   - total_complaints_filed, complaints_sent, responses_received
   - most_active_outlet

### Services (`apps/media_complaints/services.py`)

#### Letter Generation
- `generate_complaint_letter(complaint)` - Main generation function
- Uses Claude API with structured prompt
- Selects variation strategy based on complaint_number_for_incident
- Returns: subject, body, mmt_points, variation_used

#### Variation Strategies
1. **Correction** - Request public correction and clarification
2. **Training** - Request staff training on economic literacy
3. **Policy** - Request editorial policy review
4. **Investigation** - Request internal investigation
5. **Accountability** - Emphasize regulatory standards

#### Tone Profiles
- **Professional**: Formal, measured, business-like
- **Academic**: Scholarly, evidence-focused, pedagogical
- **Passionate**: Assertive, concerned citizen, direct

#### Email Sending
- `send_complaint_email(letter_id)` - Send via Django email backend
- Updates status and tracks sending

### Views (`apps/media_complaints/views.py`)

- `complaints_home` - Dashboard with stats and recent complaints
- `submit_complaint` - Form for filing new complaint
- `view_complaint` - View complaint details and generated letter
- `regenerate_letter` - Regenerate letter with different variation
- `send_letter` - Send letter via email
- `my_complaints` - User's complaint list
- `delete_complaint` - Delete a complaint
- `community_complaints` - Browse all community complaints (filterable)
- `complaint_stats` - Platform-wide statistics

### URLs (`/complaints/`)

```
/complaints/                          → Home dashboard
/complaints/submit/                   → Submit new complaint
/complaints/my-complaints/            → User's complaints list
/complaints/community/                → Browse all complaints
/complaints/stats/                    → Platform statistics
/complaints/<id>/                     → View complaint detail
/complaints/<id>/regenerate/          → Regenerate letter
/complaints/<id>/send/                → Send letter via email
/complaints/<id>/delete/              → Delete complaint
/complaints/<id>/preview/             → Preview letter text
```

## Installation & Setup

### 1. Database Migration

The app has been added to `INSTALLED_APPS`. Run migrations:

```bash
python manage.py migrate
```

### 2. Seed Media Outlets

Populate the database with UK media outlets:

```bash
python manage.py seed_media_outlets
```

This creates 19 media outlets including:
- **TV**: BBC News, ITV News, Sky News, Channel 4 News, etc.
- **Radio**: BBC Radio 4, LBC, Times Radio
- **Print**: The Guardian, The Times, Telegraph, Daily Mail, Financial Times, etc.
- **Online**: The Independent, HuffPost UK, PoliticsHome

### 3. Configure Email (Optional)

To enable sending complaints via email, configure Django's email backend in `settings.py`:

```python
# For development (console backend)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For production (SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'complaints@yourdomain.com'
```

### 4. Environment Variables

Ensure these are set (already configured in the project):

```bash
ANTHROPIC_API_KEY=your_claude_api_key
CLAUDE_MODEL=claude-sonnet-4-20250514
CLAUDE_MAX_TOKENS=4000
```

## Usage Flow

### 1. User Files Complaint

1. Navigate to `/complaints/` or click "Complaints" in nav
2. Click "File Complaint"
3. Fill out form:
   - Select media outlet
   - Enter incident date, programme name
   - Describe the misinformation
   - Choose severity (1-5)
   - Select preferred tone
4. Submit

### 2. Letter Generation

- System generates `incident_hash` from outlet + date + programme
- Counts existing complaints for this incident
- Selects variation strategy (cycles through 5 strategies)
- Calls Claude API with:
  - Incident details
  - Misinformation description
  - Variation strategy
  - Tone preference
  - MMT perspective requirements
- Stores generated letter with metadata

### 3. Review & Send

- User reviews generated letter
- Can regenerate if not satisfied
- Click "Send Letter" to email to outlet
- System tracks sending and updates status

### 4. Community & Stats

- Browse community complaints
- View statistics by outlet, severity
- Track responses from media outlets

## Integration with Existing System

### Gamification (Future Enhancement)

Can integrate with existing factcheck gamification:

```python
# In views.py after sending complaint
from apps.factcheck.services import award_experience_points, award_badge

# Award XP for filing complaint
award_experience_points(request.user, 15, 'complaint_filed')

# Award badges
if user_stats.total_complaints_filed >= 10:
    award_badge(request.user, 'media_watchdog')
```

### Navigation

Already added to `templates/components/header.html`:
```html
<a href="{% url 'media_complaints:home' %}">Complaints</a>
```

## Testing

### Manual Testing Checklist

1. **Create Complaint**
   ```
   - Go to /complaints/submit/
   - Fill out form
   - Submit
   - Verify letter is generated
   ```

2. **Test Variation**
   ```
   - Create multiple complaints for same incident
   - Check that different strategies are used
   - Verify letters have different structure/emphasis
   ```

3. **Test Email**
   ```
   - Configure email backend
   - Send a test complaint
   - Verify email is received (or appears in console)
   ```

4. **Test UI**
   ```
   - Navigate to all pages
   - Check responsive design
   - Test filters on community page
   - Verify stats calculations
   ```

### Testing Letter Generation

```python
# In Django shell (python manage.py shell)
from apps.media_complaints.models import Complaint, MediaOutlet
from apps.media_complaints.services import generate_complaint_letter
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()
outlet = MediaOutlet.objects.first()

# Create test complaint
complaint = Complaint.objects.create(
    user=user,
    outlet=outlet,
    incident_date='2025-11-25',
    programme_name='Test Programme',
    claim_description='Test claim about government debt',
    severity=3,
    preferred_tone='professional'
)

# Generate letter
letter_data = generate_complaint_letter(complaint)
print(letter_data['subject'])
print(letter_data['body'])
```

## Admin Interface

All models are registered in Django admin at `/admin/`:

- **MediaOutlet**: Manage media outlets, add new ones
- **Complaint**: View all complaints, filter by status/outlet
- **ComplaintLetter**: View generated letters, track responses
- **ComplaintStats**: User statistics

## Differences from TypeScript Version

| Feature | TypeScript | Python/Django |
|---------|-----------|---------------|
| **Backend** | Node.js + Express | Django 5.0 |
| **Database** | Prisma ORM | Django ORM |
| **Frontend** | React + Vite | Django Templates + HTMX |
| **AI** | Anthropic SDK | Anthropic SDK (same) |
| **Email** | Nodemailer | Django Email |
| **Auth** | JWT | Django Session Auth |
| **State** | Zustand + React Query | Django Context |

### Key Improvements

1. **Integrated**: Part of larger budget response suite
2. **Unified Auth**: Same user accounts across all features
3. **Gamification Ready**: Can leverage existing XP/badge system
4. **Admin Panel**: Built-in Django admin for management
5. **Template System**: Consistent styling with rest of suite

## Future Enhancements

- [ ] Async letter generation with Celery (like factcheck)
- [ ] WebSocket updates for real-time letter generation status
- [ ] Email parsing to automatically detect responses
- [ ] Analytics dashboard for response rates by outlet
- [ ] Export complaints as CSV for regulatory reporting
- [ ] Batch complaint submission for same incident
- [ ] Template customization per outlet type
- [ ] Integration with factcheck to auto-create complaints from claims
- [ ] API endpoints for mobile app

## Files Created

### Core Files
- `apps/media_complaints/__init__.py`
- `apps/media_complaints/apps.py`
- `apps/media_complaints/models.py` (4 models, 400+ lines)
- `apps/media_complaints/services.py` (Letter generation, 350+ lines)
- `apps/media_complaints/forms.py` (ComplaintForm)
- `apps/media_complaints/views.py` (10 views)
- `apps/media_complaints/urls.py` (10 URL patterns)
- `apps/media_complaints/admin.py` (4 admin classes)

### Management
- `apps/media_complaints/management/commands/seed_media_outlets.py`

### Templates
- `templates/media_complaints/home.html`
- `templates/media_complaints/submit.html`
- `templates/media_complaints/detail.html`
- `templates/media_complaints/my_complaints.html`
- `templates/media_complaints/community.html`
- `templates/media_complaints/stats.html`

### Migrations
- `apps/media_complaints/migrations/0001_initial.py`

### Configuration Changes
- `config/settings/base.py` - Added to INSTALLED_APPS
- `config/urls.py` - Added /complaints/ route
- `templates/components/header.html` - Added nav link

## Support & Documentation

- **Original Bot**: https://github.com/ChrisB2025/mmt-complainer-bot
- **Django Docs**: https://docs.djangoproject.com/
- **Anthropic API**: https://docs.anthropic.com/
- **MMT Resources**: Include in letter generation context

## License

Same as parent project (MMT Budget Day Response Suite)

---

**Status**: ✅ Complete and ready for testing
**Last Updated**: 2025-11-23
**Author**: Claude Code (Anthropic AI Assistant)
