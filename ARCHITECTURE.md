# MMT Budget Day Response Suite - Django + HTMX Architecture

## Tech Stack

- **Backend**: Django 5.0 + Python 3.11
- **Frontend**: HTMX + Alpine.js + Tailwind CSS
- **Database**: PostgreSQL 15
- **Real-time**: Django Channels + Redis
- **Task Queue**: Celery + Redis
- **AI**: Anthropic Claude API (Python SDK)
- **Deployment**: Railway
- **Web Server**: Gunicorn + Whitenoise (static files)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                 DJANGO TEMPLATES + HTMX                  │
│  ┌──────────┐  ┌───────────┐  ┌──────────────┐         │
│  │  Bingo   │  │ Fact-Check│  │   Rebuttal   │         │
│  │Template  │  │ Template  │  │   Template   │         │
│  └────┬─────┘  └─────┬─────┘  └──────┬───────┘         │
│       │              │                │                  │
│       │ HTMX requests (hx-get, hx-post, hx-swap)        │
│       │              │                │                  │
└───────┼──────────────┼────────────────┼─────────────────┘
        │              │                │
┌───────▼──────────────▼────────────────▼─────────────────┐
│                    DJANGO BACKEND                        │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ Bingo App   │  │ FactCheck    │  │  Rebuttal App  │ │
│  │ (Views)     │  │    App       │  │    (Views)     │ │
│  └──────┬──────┘  └──────┬───────┘  └────────┬───────┘ │
│         │                │                    │          │
│  ┌──────▼────────────────▼────────────────────▼──────┐  │
│  │         Django Channels (WebSocket)               │  │
│  └──────────────────────┬────────────────────────────┘  │
│                         │                                │
│  ┌──────────────────────▼────────────────────────────┐  │
│  │    Celery Tasks (Claude API, Background Jobs)    │  │
│  └──────────────────────┬────────────────────────────┘  │
│                         │                                │
│  ┌──────────────────────▼────────────────────────────┐  │
│  │              Django ORM (Models)                  │  │
│  └──────────────────────┬────────────────────────────┘  │
└─────────────────────────┼───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                PostgreSQL Database                       │
│  ┌─────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  Users  │  │    Bingo     │  │   Fact-Checks    │   │
│  │  Teams  │  │    Cards     │  │    Rebuttals     │   │
│  └─────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────┘

                   ┌──────────────┐
                   │    Redis     │
                   │ (Channels +  │
                   │   Celery)    │
                   └──────────────┘
```

## Django Project Structure

```
budget_response_suite/           # Django project root
├── manage.py
├── requirements.txt
├── runtime.txt                  # Python version for Railway
├── Procfile                     # Railway/Heroku process file
├── railway.json
├── .env.example
├── .gitignore
│
├── config/                      # Project settings
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py              # Base settings
│   │   ├── development.py       # Local dev settings
│   │   └── production.py        # Production settings
│   ├── urls.py                  # Root URL configuration
│   ├── asgi.py                  # ASGI for Django Channels
│   ├── wsgi.py                  # WSGI for Gunicorn
│   └── celery.py                # Celery configuration
│
├── apps/                        # Django apps
│   ├── __init__.py
│   │
│   ├── users/                   # User authentication & profiles
│   │   ├── __init__.py
│   │   ├── models.py            # User, Team models
│   │   ├── views.py             # Login, register, profile
│   │   ├── forms.py             # Auth forms
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── templates/users/
│   │       ├── login.html
│   │       ├── register.html
│   │       └── profile.html
│   │
│   ├── bingo/                   # Bingo game
│   │   ├── __init__.py
│   │   ├── models.py            # BingoPhrase, BingoCard, BingoSquare
│   │   ├── views.py             # Card generation, marking, leaderboard
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── services.py          # Business logic
│   │   ├── consumers.py         # WebSocket consumer
│   │   └── templates/bingo/
│   │       ├── card.html
│   │       ├── square.html      # HTMX partial
│   │       ├── leaderboard.html
│   │       └── stats.html
│   │
│   ├── factcheck/               # Fact-checking system
│   │   ├── __init__.py
│   │   ├── models.py            # FactCheckRequest, FactCheckResponse
│   │   ├── views.py             # Submit, queue, detail
│   │   ├── forms.py             # Submission form
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── tasks.py             # Celery task for Claude API
│   │   ├── services.py          # Claude integration
│   │   └── templates/factcheck/
│   │       ├── submit.html
│   │       ├── queue.html
│   │       ├── detail.html
│   │       └── response_card.html  # HTMX partial
│   │
│   ├── rebuttal/                # Rebuttal generation
│   │   ├── __init__.py
│   │   ├── models.py            # Rebuttal, RebuttalSection
│   │   ├── views.py             # Generate, view, download
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── tasks.py             # Celery task for generation
│   │   ├── services.py          # Claude integration
│   │   ├── exporters.py         # PDF/Markdown export
│   │   └── templates/rebuttal/
│   │       ├── latest.html
│   │       ├── detail.html
│   │       └── section.html     # HTMX partial
│   │
│   └── core/                    # Shared utilities
│       ├── __init__.py
│       ├── models.py            # UserAction, Achievement
│       ├── views.py             # Dashboard, stats
│       ├── urls.py
│       ├── admin.py
│       ├── middleware.py        # Custom middleware
│       ├── templatetags/
│       │   ├── __init__.py
│       │   └── htmx_tags.py     # Custom template tags
│       └── templates/core/
│           ├── dashboard.html
│           ├── stats.html
│           └── activity_feed.html
│
├── templates/                   # Global templates
│   ├── base.html                # Base template with HTMX
│   ├── components/
│   │   ├── header.html
│   │   ├── footer.html
│   │   ├── nav.html
│   │   └── toast.html           # Toast notifications
│   └── errors/
│       ├── 404.html
│       └── 500.html
│
├── static/                      # Static files
│   ├── css/
│   │   ├── input.css            # Tailwind input
│   │   └── output.css           # Tailwind compiled
│   ├── js/
│   │   ├── htmx.min.js
│   │   ├── alpine.min.js
│   │   └── app.js               # Custom JS
│   └── images/
│       └── logo.png
│
└── staticfiles/                 # Collected static (production)
```

## Database Models (Django ORM)

### User & Team Models

```python
# apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Extended user model"""
    display_name = models.CharField(max_length=100, blank=True)
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True)
    points = models.IntegerField(default=0)

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['team']),
        ]

class Team(models.Model):
    """Team for competition"""
    name = models.CharField(max_length=100)
    total_points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'teams'
```

### Bingo Models

```python
# apps/bingo/models.py
from django.db import models
from django.conf import settings

class BingoPhrase(models.Model):
    """Library of bingo phrases"""
    DIFFICULTY_CHOICES = [
        ('classic', 'Classic'),
        ('advanced', 'Advanced'),
        ('technical', 'Technical'),
    ]

    phrase_text = models.CharField(max_length=200)
    category = models.CharField(max_length=50, blank=True)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bingo_phrases'
        indexes = [
            models.Index(fields=['difficulty_level']),
        ]

class BingoCard(models.Model):
    """Generated bingo card"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=20)
    completed = models.BooleanField(default=False)
    completion_time = models.DateTimeField(null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bingo_cards'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['completed']),
        ]

class BingoSquare(models.Model):
    """Individual square on a card"""
    card = models.ForeignKey(BingoCard, on_delete=models.CASCADE, related_name='squares')
    phrase = models.ForeignKey(BingoPhrase, on_delete=models.CASCADE)
    position = models.IntegerField()  # 0-24
    marked = models.BooleanField(default=False)
    marked_at = models.DateTimeField(null=True, blank=True)
    auto_detected = models.BooleanField(default=False)

    class Meta:
        db_table = 'bingo_squares'
        unique_together = [['card', 'position']]
        indexes = [
            models.Index(fields=['card']),
            models.Index(fields=['marked']),
        ]
```

### Fact-Check Models

```python
# apps/factcheck/models.py
from django.db import models
from django.conf import settings

class FactCheckRequest(models.Model):
    """User-submitted claim for fact-checking"""
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('processing', 'Processing'),
        ('reviewed', 'Reviewed'),
        ('published', 'Published'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    claim_text = models.TextField()
    context = models.TextField(blank=True)
    timestamp_in_speech = models.CharField(max_length=20, blank=True)
    severity = models.IntegerField()  # 1-10
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    upvotes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fact_check_requests'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]

class FactCheckResponse(models.Model):
    """AI-generated fact-check response"""
    request = models.OneToOneField(FactCheckRequest, on_delete=models.CASCADE, related_name='response')
    the_claim = models.TextField()
    the_problem = models.TextField()
    the_reality = models.TextField()
    the_evidence = models.TextField(blank=True)
    mmt_perspective = models.TextField(blank=True)
    citations = models.JSONField(default=list)
    generated_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'fact_check_responses'
```

### Rebuttal Models

```python
# apps/rebuttal/models.py
from django.db import models

class Rebuttal(models.Model):
    """Generated comprehensive rebuttal"""
    title = models.CharField(max_length=255)
    version = models.CharField(max_length=10, default='1.0')
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rebuttals'
        indexes = [
            models.Index(fields=['version']),
            models.Index(fields=['published']),
        ]

class RebuttalSection(models.Model):
    """Section within a rebuttal"""
    rebuttal = models.ForeignKey(Rebuttal, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    content = models.TextField()
    section_order = models.IntegerField()

    class Meta:
        db_table = 'rebuttal_sections'
        ordering = ['section_order']
```

## HTMX Integration Patterns

### Bingo Square Marking

```html
<!-- apps/bingo/templates/bingo/square.html -->
<div
    id="square-{{ square.id }}"
    class="bingo-square {% if square.marked %}marked{% endif %}"
    hx-post="{% url 'bingo:mark_square' square.id %}"
    hx-trigger="click"
    hx-swap="outerHTML"
    hx-target="#square-{{ square.id }}"
>
    <p>{{ square.phrase.phrase_text }}</p>
    {% if square.marked %}
    <span class="checkmark">✓</span>
    {% endif %}
</div>
```

### Fact-Check Submission

```html
<!-- apps/factcheck/templates/factcheck/submit.html -->
<form
    hx-post="{% url 'factcheck:submit' %}"
    hx-target="#factcheck-queue"
    hx-swap="afterbegin"
    hx-on="htmx:afterRequest: this.reset()"
>
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Submit Fact-Check</button>
</form>
```

### Real-time Leaderboard

```html
<!-- apps/bingo/templates/bingo/leaderboard.html -->
<div
    id="leaderboard"
    hx-get="{% url 'bingo:leaderboard' %}"
    hx-trigger="every 5s"
    hx-swap="innerHTML"
>
    <!-- Leaderboard content -->
</div>
```

## Django Channels (WebSocket)

### Routing

```python
# config/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from apps.bingo import routing as bingo_routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            bingo_routing.websocket_urlpatterns
        )
    ),
})
```

### Consumer

```python
# apps/bingo/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class BingoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'bingo_updates'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def square_marked(self, event):
        await self.send(text_data=json.dumps({
            'type': 'square_marked',
            'square_id': event['square_id'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp']
        }))
```

## Celery Tasks

### Fact-Check Generation

```python
# apps/factcheck/tasks.py
from celery import shared_task
from apps.factcheck.services import generate_fact_check_with_claude
from apps.factcheck.models import FactCheckRequest

@shared_task
def process_fact_check(request_id):
    """Generate AI fact-check response"""
    request = FactCheckRequest.objects.get(id=request_id)
    request.status = 'processing'
    request.save()

    try:
        response = generate_fact_check_with_claude(
            claim=request.claim_text,
            context=request.context,
            severity=request.severity
        )
        request.status = 'reviewed'
        request.save()
        return response
    except Exception as e:
        request.status = 'submitted'
        request.save()
        raise e
```

## Views (Django)

### HTMX-aware Views

```python
# apps/bingo/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from apps.bingo.models import BingoCard, BingoSquare
from apps.bingo.services import check_bingo_completion

@login_required
def mark_square(request, square_id):
    """Mark a bingo square (HTMX endpoint)"""
    square = get_object_or_404(BingoSquare, id=square_id, card__user=request.user)

    if not square.marked:
        square.marked = True
        square.marked_at = timezone.now()
        square.save()

        # Check for completion
        card = square.card
        if check_bingo_completion(card):
            card.completed = True
            card.completion_time = timezone.now()
            card.save()

            # Broadcast via channels
            # ... channel layer code ...

    # Return updated square HTML for HTMX swap
    return render(request, 'bingo/square.html', {'square': square})
```

## URL Routing

```python
# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('users/', include('apps.users.urls')),
    path('bingo/', include('apps.bingo.urls')),
    path('factcheck/', include('apps.factcheck.urls')),
    path('rebuttal/', include('apps.rebuttal.urls')),
]
```

## Base Template

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}MMT Budget Response Suite{% endblock %}</title>

    <!-- Tailwind CSS -->
    <link href="{% static 'css/output.css' %}" rel="stylesheet">

    <!-- HTMX -->
    <script src="{% static 'js/htmx.min.js' %}"></script>

    <!-- Alpine.js (for UI interactions) -->
    <script defer src="{% static 'js/alpine.min.js' %}"></script>

    {% block extra_head %}{% endblock %}
</head>
<body class="bg-gray-50">
    {% include 'components/header.html' %}

    <main class="container mx-auto px-4 py-8">
        {% block content %}{% endblock %}
    </main>

    {% include 'components/footer.html' %}

    <!-- Toast notifications -->
    <div id="toast-container" class="fixed top-4 right-4 z-50"></div>

    <script src="{% static 'js/app.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

## Deployment Configuration

### requirements.txt

```
Django==5.0
psycopg2-binary==2.9.9
gunicorn==21.2.0
whitenoise==6.6.0
django-environ==0.11.2
channels==4.0.0
channels-redis==4.1.0
redis==5.0.1
celery==5.3.4
anthropic==0.8.1
Pillow==10.1.0
reportlab==4.0.7
markdown==3.5.1
```

### Procfile

```
web: gunicorn config.wsgi:application
worker: celery -A config worker --loglevel=info
```

### railway.json

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

## Environment Variables

```env
# Django
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=.railway.app,yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/budget_suite

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Claude API
ANTHROPIC_API_KEY=your-api-key
CLAUDE_MODEL=claude-sonnet-4-20250514
CLAUDE_MAX_TOKENS=4000

# Channels
CHANNEL_LAYERS_BACKEND=channels_redis.core.RedisChannelLayer
```

## Development Workflow

1. **Start PostgreSQL**: `docker-compose up -d postgres`
2. **Start Redis**: `docker-compose up -d redis`
3. **Run migrations**: `python manage.py migrate`
4. **Create superuser**: `python manage.py createsuperuser`
5. **Load seed data**: `python manage.py loaddata bingo_phrases`
6. **Run dev server**: `python manage.py runserver`
7. **Run Celery worker**: `celery -A config worker -l info`
8. **Compile Tailwind**: `npx tailwindcss -i static/css/input.css -o static/css/output.css --watch`

## Key Advantages of Django + HTMX

1. **Simpler Stack**: No separate frontend build process
2. **Django Admin**: Built-in admin panel for content management
3. **Django ORM**: Powerful database abstraction
4. **Template Reusability**: Django's template inheritance
5. **HTMX Simplicity**: No complex state management
6. **SEO-friendly**: Server-rendered HTML
7. **Rapid Development**: Django's batteries-included approach
8. **Security**: Django's built-in CSRF, XSS protection
9. **Django Channels**: WebSocket support with same stack
10. **Celery Integration**: Well-established async task processing

This architecture maintains all the functionality of the original spec while leveraging Django's strengths and HTMX's simplicity for a more maintainable, rapid development experience.
