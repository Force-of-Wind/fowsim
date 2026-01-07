# Force of Wind Simulator - Claude Code Guidelines

## Project Overview

Force of Wind Simulator is a Django-based web application for the Force of Wind Trading Card Game (FOWTCG). It provides card database browsing, deck building, tournament management, and pack opening simulation.

**Stack:** Django 5.1.6, Python 3.13, PostgreSQL, Bootstrap, AWS S3 (production)

## Project Structure

```
fowsim/
├── fowsim/           # Django project configuration
│   ├── settings.py   # Django settings (env-based config)
│   ├── constants.py  # All game constants, choices, enums
│   ├── decorators.py # Custom view decorators
│   └── urls.py       # Root URL configuration
├── cardDatabase/     # Main application
│   ├── models/       # Data models (one file per domain)
│   ├── views/        # Feature-organized views
│   │   ├── admin/    # Admin-only views
│   │   ├── bot/      # API endpoints for bots
│   │   ├── post/     # Form submission handlers
│   │   ├── tournament/ # Tournament management
│   │   └── utils/    # Shared view utilities
│   ├── templates/    # Django HTML templates
│   ├── static/       # CSS, JS, images
│   └── forms.py      # Form definitions
├── media/            # User uploads, card images
└── nginx/            # Production nginx config
```

**Note:** The `game/` directory is legacy/unused - ignore it.

## Code Conventions

### Python Style
- Use Ruff for linting and formatting
- Line length: 120 characters
- Use double quotes for strings
- Use f-strings for string formatting
- Sort imports with isort (via Ruff)

### Django Patterns

**Models:**
- One model per file in `cardDatabase/models/`
- Export all models in `models/__init__.py`
- Always add `__str__` methods
- Use `related_name` on ForeignKey fields
- Define `Meta` class with ordering, verbose_name

**Views:**
- Organize by feature in separate files, not monolithic views.py
- Use custom decorators from `fowsim/decorators.py`:
  - `@site_admins` - Restrict to site administrators
  - `@desktop_only` / `@mobile_only` - Device-specific views
  - `@tournament_owner`, `@tournament_admin`, `@tournament_reader` - Tournament permissions
- Use `get_object_or_404` instead of manual exception handling
- Implement pagination for list views (see `fowsim/constants.py` for page sizes)

**Forms:**
- Define in `cardDatabase/forms.py`
- Use ModelForm when possible
- Dynamic choices load from database (Formats, Races, Keywords)

**Constants:**
- All game constants live in `fowsim/constants.py`
- Card types, rarities, colors, divinities, tournament phases, etc.
- Import from there, don't hardcode values

**Templates:**
- Use template inheritance (base templates exist)
- Responsive design: mobile and desktop variants in static/css/
- CSRF protection required on all forms

### Database
- Use Django ORM exclusively (no raw SQL)
- Always create migrations for model changes
- Use `select_related()` and `prefetch_related()` for query optimization
- Database config via environment variables (DATABASE_URL or DB_*)

### Security
- Store secrets in environment variables (.env file locally)
- Never commit credentials
- Validate and sanitize all user input
- Use Django's built-in CSRF protection

## Testing

Use pytest with pytest-django:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cardDatabase

# Run specific test file
pytest cardDatabase/tests/test_models.py

# Run tests matching pattern
pytest -k "test_deck"
```

**Test file organization:**
- Place tests in `cardDatabase/tests/` directory
- Name files `test_*.py`
- Use pytest fixtures for common setup
- Test both success and error cases

## Common Commands

```bash
# Development server
python manage.py runserver

# Migrations
python manage.py makemigrations
python manage.py migrate

# Import card data
python manage.py importjson
python manage.py importBanlist
python manage.py downloadCardImages

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell
```

## Environment Variables

Required in `.env`:
- `SECRET_KEY` - Django secret key
- `DEBUG` - Set to True for development
- `DATABASE_URL` or individual `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` - For email features (optional locally)

## Management Commands

Custom commands in `cardDatabase/management/commands/`:
- `importjson` - Import card data from JSON
- `importBanlist` - Import banlist data
- `downloadCardImages` - Fetch card images from source
- `assign_existing_card_images` - Link images to cards
- `exportJson` - Export data to JSON
- `dailyDeckMetricCalculations` - Calculate deck statistics
- `incrementalCardImport` / `incrementalCardImportLocal` - Incremental sync

## Key Models

- **Card** - Core card entity with all game attributes
- **DeckList** - User-created decks with sharing capabilities
- **DeckListCard** - Cards within decks (through table with position/quantity)
- **Format** - Game formats with associated card sets
- **BannedCard** / **CombinationBannedCards** - Format-specific bans
- **Tournament** - Event with registration, phases, staff roles
- **TournamentPlayer** - Player participation with deck and standing
- **Metrics** - Popularity tracking for cards/attributes over time
- **Profile** - Extended user info (admin/judge flags)

## Pull Request Guidelines

Per CONTRIBUTORS.md:
- Branch naming: `issue-number-short-description`
- Keep PRs focused on single issues
- Follow existing code patterns for consistency
- Test your changes manually before submitting
