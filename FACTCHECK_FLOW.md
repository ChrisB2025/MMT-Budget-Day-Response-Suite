# Fact-Check Submission Flow

## What Happens When You Submit a Fact-Check?

### 1. **User Submits Claim**
- User fills out form at `/factcheck/submit/`
- Provides: claim text, optional context, timestamp, severity rating (1-10)

### 2. **Server Receives Submission** (apps/factcheck/views.py:95-136)
```
POST /factcheck/submit/
↓
Save FactCheckRequest to database
  - Status: 'submitted'
  - User, claim_text, severity, etc.
```

### 3. **Gamification (if tables exist)** (apps/factcheck/views.py:90-96)
- Award 10 XP to user
- Update hot streak counter (consecutive submissions within 5 min)
- Check and award badges:
  - First Claim
  - Hot Streak (5, 10)
  - Prolific Checker (50, 100 claims)
  - etc.

### 4. **AI Processing Triggered** (apps/factcheck/views.py:108-118)

**Async (Celery available):**
```
process_fact_check.delay(fact_check.id)
↓
Celery task runs in background
↓
Calls Claude API with structured prompt
↓
Generates fact-check response
```

**Sync (Celery not available - FALLBACK):**
```
process_fact_check(fact_check.id)  # Runs immediately
↓
Calls Claude API directly
↓
Generates fact-check response
```

### 5. **AI Processing Details** (apps/factcheck/tasks.py:9-60)

```python
# Update status
request.status = 'processing'

# Call Claude API (apps/factcheck/services.py:31-92)
fact_check_data = generate_fact_check_with_claude(
    claim=claim_text,
    context=context,
    severity=severity
)

# Claude returns structured JSON with:
{
    "the_claim": "Restated claim",
    "the_problem": "What is misleading",
    "the_reality": "What is actually true",
    "the_evidence": "Supporting data/citations",
    "mmt_perspective": "MMT analysis",
    "citations": [{"title": "...", "url": "..."}]
}

# Create FactCheckResponse
response = FactCheckResponse.objects.create(
    request=request,
    the_claim=...,
    the_problem=...,
    # etc.
)

# Update status
request.status = 'reviewed'
```

### 6. **User Gets Response**
- Redirected to `/factcheck/<id>/` (detail page)
- Can see AI-generated fact-check
- Can upvote, comment, share to Twitter
- Claim appears in queue for others to see

## System Flow Diagram

```
User Form
    ↓
[Submit] → Save to DB → Award XP/Badges
    ↓
    ├─→ Celery Available?
    │   YES → Queue async task → Claude API → Save Response
    │   NO  → Process immediately → Claude API → Save Response
    ↓
Detail Page (fact-check visible to all)
    ↓
Queue/Feed/Leaderboard (community features)
```

## Current Status (Before Migrations)

✅ **Working:**
- Form submission
- Database save
- Basic success messages
- Redirect to detail page

⏳ **Pending (after migrations):**
- XP awards
- Badge system
- User profiles
- Leaderboard
- Hot streaks
- Claim of the Day
- Comments

## To Enable Full Features

Run on your server:
```bash
python manage.py makemigrations factcheck
python manage.py migrate
```

This creates tables for:
- UserProfile
- UserBadge
- UserFollow
- ClaimComment
- ClaimOfTheDay
- ClaimOfTheMinute
