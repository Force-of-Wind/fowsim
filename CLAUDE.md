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

## Domain Knowledge

### Force of Will Card Game Concepts

**Card Attributes (Colors):**
- Fire (R), Water (U), Wind (G), Light (W), Darkness (B), Void (V)
- Cards can be multi-color or mono-color
- Attribute codes match MTG conventions (R=Red/Fire, U=Blue/Water, etc.)

**Card Types:**
- **Resonators** - Creatures that attack/defend
- **Chants** - Spells (instant-speed via `Spell:Chant-Instant`)
- **Additions** - Enchantments attached to resonators, fields, or rulers
- **Regalia** - Artifacts/equipment
- **Rulers/J-Rulers** - Leader cards (Rulers flip to J-Rulers via Judgment)
- **Magic Stones** - Resource cards (like lands in MTG)
- **Runes/Master Runes** - Special spell type
- **Sub-Rulers** - Secondary ruler cards

**Deck Zones:**
- `Ruler Area` - Ruler and J-Ruler
- `Main Deck` - 40-60 cards (resonators, chants, additions, regalia)
- `Magic Stone Deck` - 10-20 magic stones
- `Side Deck` - 0-15 cards for sideboarding

**Card Identifiers:**
- Format: Usually `SET-NUMBER` (e.g., `EDL-064`, `TSW-109`). Some exceptions such as Pre release and Buy a Box promos.
- J-Ruler sides append `J` (e.g., `TSW-109J`)
- Special characters: `^` (double-sided), `*` (alternative), `J^` (colossal)

**Rarities:** Common (C), Uncommon (U), Rare (R), Super Rare (SR), Ruler (RR), J-Ruler (JR), Marvel Rare (MR), Secret Rare (SEC)

**Sets & Clusters:**
- Cards are grouped into Sets (e.g., `EDL` = "Epic of the Dragon Lord")
- Sets belong to Clusters (e.g., Saga, Hero, Trinity, Duel)
- See `fowsim/constants.py` → `SET_DATA` for full hierarchy

**Banlists:**
- Cards can be banned outright or as combinations
- `CombinationBannedCards` - Two cards banned together (can't use both)
- Bans are format-specific (Wanderer, ABC, etc.)

### Tournament System

**Tournament Phases:** `created` → `registration` → `swiss` → `tops` → `completed`

**Player States:** `requested` → `accepted` → `completed`

**Staff Roles:** Hierarchical permissions via `StaffRole` model
- `can_read` - View tournament data
- `can_write` - Modify tournament data
- `can_delete` - Full control (owner)

**Deck Locking:** Decks can be locked for tournament use (`MODE_TOURNAMENT`)

---

## Common Workflows

### Adding a New View

1. Create file in `cardDatabase/views/` (e.g., `my_feature.py`)
2. Define view function(s) with request parameter
3. Use decorators as needed (`@login_required`, `@desktop_only`, etc.)
4. Add URL pattern in `cardDatabase/urls.py`
5. Create template in `cardDatabase/templates/cardDatabase/html/`
6. Add static files as needed (see below)

```python
# cardDatabase/views/my_feature.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def my_view(request):
    ctx = {"data": some_data}
    return render(request, "cardDatabase/html/my_feature.html", context=ctx)
```

**Static Files Convention:**
- CSS: `cardDatabase/static/css/my_feature.css` (desktop)
- JS: `cardDatabase/static/js/my_feature.js` (desktop)
- Mobile variants (if needed):
  - `cardDatabase/static/css/my_feature_mobile.css`
  - `cardDatabase/static/js/my_feature_mobile.js`
- Plain filename = desktop; `_mobile` suffix = mobile

**JavaScript Convention:**
- Use jQuery for DOM manipulation (not vanilla JS)
- Use `$('#id')` instead of `document.getElementById('id')`
- Use `$('.class')` instead of `document.querySelectorAll('.class')`

**Template Inheritance:**
- `base.html` - Root template (header, nav, jQuery, Bootstrap, dark mode)
- `database_base.html` - Extends base, adds card search section at top

Extend the appropriate base:
```html
{# For pages WITH search section #}
{% extends 'cardDatabase/html/database_base.html' %}

{# For pages WITHOUT search section #}
{% extends 'cardDatabase/html/base.html' %}
```

**Template Blocks:**
- `{% block css %}` - Desktop CSS (call `{{ block.super }}` to keep base styles)
- `{% block mobilecss %}` - Mobile CSS (auto-wrapped in device check)
- `{% block js %}` - JavaScript
- `{% block body %}` - Main content

**Mobile Detection in Templates:**
```html
{% if request.user_agent.is_mobile or request.user_agent.is_tablet %}
    {# Mobile-specific content #}
{% endif %}
```

**JavaScript Global:**
- `FOWDB_IS_MOBILE` - Boolean set by base template for JS mobile detection

### Adding a New Model

1. Create file in `cardDatabase/models/` (e.g., `MyModel.py`)
2. Define model with Meta class and `__str__`
3. Export in `cardDatabase/models/__init__.py`
4. Run `python manage.py makemigrations && python manage.py migrate`

```python
# cardDatabase/models/MyModel.py
from django.db import models

class MyModel(models.Model):
    class Meta:
        app_label = "cardDatabase"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Adding Card Search Functionality

Card search uses `cardDatabase/views/utils/search_context.py`:
- `get_search_form_ctx()` - Base context with form choices
- `basic_search(form)` - Simple name/text search
- `advanced_search(form)` - Multi-field filtering

Query optimization patterns:
```python
# Prefetch related data for card lists
cards = Card.objects.filter(...).prefetch_related(
    "colours", "types", "races", "ability_texts"
).select_related(...)
```

### Tournament Staff Permissions

Use decorators from `fowsim/decorators.py`:

```python
from fowsim.decorators import tournament_owner, tournament_admin, tournament_reader

@tournament_reader  # Can view
def view_tournament(request, tournament_id):
    # request.tournament and request.staff_account are auto-attached
    ...

@tournament_admin  # Can modify
def edit_tournament(request, tournament_id):
    ...

@tournament_owner  # Full control
def delete_tournament(request, tournament_id):
    ...
```

---

## Architecture Decisions

### Why views are split into separate files
- Easier to find and maintain feature-specific code
- Prevents massive views.py files
- Each file handles one cohesive feature

### Why constants.py is so large
- Single source of truth for all game data
- Prevents inconsistencies across codebase
- Easy to update when game rules change
- Contains: card types, rarities, sets, keywords, tournament phases

### Why models use separate files
- Each domain concept is isolated
- Easier to understand relationships
- Import via `__init__.py` for clean API

### Areas to be careful with

**Search Performance:**
- Text search can be slow on large datasets
- Recent commit improved this - check `search_context.py` for optimized patterns
- Use database indexes for frequently filtered fields

**Card Images:**
- Stored in `media/cards/` locally, S3 in production
- Images are optional (`blank=True, null=True`)
- Use `card.card_image` property (handles fallbacks)

**Tournament State:**
- Phase transitions should be validated
- Player registration states are important
- Deck locking prevents edits during tournament

**Constants Imports:**
- Always import as `from fowsim import constants as CONS`
- Don't duplicate constant values

---

## Pull Request Guidelines

Per CONTRIBUTORS.md:
- Branch naming: `issue-number-short-description`
- Keep PRs focused on single issues
- Follow existing code patterns for consistency
- Test your changes manually before submitting
