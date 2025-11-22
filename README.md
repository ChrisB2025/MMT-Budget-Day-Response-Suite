# MMT Budget Day Response Suite

A Django + HTMX web application for tracking budget myths, crowdsourcing fact-checks, and generating comprehensive MMT-based rebuttals for UK Budget Day 2025.

## Features

### 🎯 Budget Bingo
- Real-time myth tracking game
- Generate 5x5 bingo cards with common budget myths
- Compete for fastest completion on leaderboard
- WebSocket support for real-time updates

### ✓ Fact-Check Platform
- Submit claims for AI-powered fact-checking
- Claude AI generates MMT-based analysis
- Community upvoting system
- Structured responses with evidence and citations

### 📄 Comprehensive Rebuttal
- AI-generated comprehensive budget analysis
- Download in PDF, Markdown, or HTML
- Includes debunked myths, fiscal analysis, and action points
- Ready for activists, MPs, and media

## Tech Stack

- **Backend**: Django 5.0 + Python 3.11
- **Frontend**: HTMX + Alpine.js + Tailwind CSS
- **Database**: PostgreSQL 15
- **Real-time**: Django Channels + Redis
- **Task Queue**: Celery + Redis
- **AI**: Anthropic Claude API
- **Deployment**: Railway

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Anthropic API key

### Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd MMT-Budget-Day-Response-Suite
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your configuration
```

Required environment variables:
```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgresql://budget_user:budget_pass@localhost:5432/budget_suite
REDIS_URL=redis://localhost:6379/0
ANTHROPIC_API_KEY=your-anthropic-api-key
```

5. **Start PostgreSQL and Redis**
```bash
docker-compose up -d
```

6. **Run migrations**
```bash
python manage.py migrate
```

7. **Create superuser**
```bash
python manage.py createsuperuser
```

8. **Load seed data** (Optional - bingo phrases)
```bash
# Seed data can be added via Django admin
```

9. **Run development server**
```bash
python manage.py runserver
```

10. **Run Celery worker** (in another terminal)
```bash
celery -A config worker -l info
```

11. **Access the application**
- Web: http://localhost:8000
- Admin: http://localhost:8000/admin

## Project Structure

```
budget_response_suite/
├── apps/                    # Django apps
│   ├── users/              # Authentication
│   ├── bingo/              # Bingo game
│   ├── factcheck/          # Fact-checking
│   ├── rebuttal/           # Rebuttal generation
│   └── core/               # Dashboard & shared utilities
├── config/                 # Django settings
├── templates/              # HTML templates
├── manage.py
├── requirements.txt
└── docker-compose.yml
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## Deployment to Railway

1. **Push to GitHub**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Create Railway project**
- Go to https://railway.app
- Create new project from GitHub repo
- Add PostgreSQL service
- Add Redis service

3. **Set environment variables in Railway**
- `DJANGO_SETTINGS_MODULE=config.settings.production`
- `SECRET_KEY=your-production-secret-key`
- `ANTHROPIC_API_KEY=your-api-key`
- `ALLOWED_HOSTS=.railway.app`

4. **Deploy**
- Railway will automatically deploy on push to main

5. **Run migrations**
- Use Railway CLI or web interface

## Version

Current version: 1.0.0 (MVP)
Launch date: November 30, 2025