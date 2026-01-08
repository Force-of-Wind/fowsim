---
description: Start the Django development server with migrations
---

# Run Development Server

Start the local development server after ensuring migrations are applied.

## Steps

1. Apply any pending migrations
2. Start the development server on localhost:8000

## Commands

```bash
python manage.py migrate
python manage.py runserver
```

## Notes

- Ensure your `.env` file is configured with database credentials
- The server runs at http://127.0.0.1:8000/ by default
- Press Ctrl+C to stop the server
