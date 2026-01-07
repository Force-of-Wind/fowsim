---
description: Build and run the application with Docker
---

# Docker Commands

Manage the application using Docker and docker-compose.

## Development

```bash
# Build and start all containers
docker-compose up --build

# Start in detached mode (background)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all containers
docker-compose down

# Stop and remove volumes (reset database)
docker-compose down -v
```

## Individual Services

```bash
# Rebuild just the web service
docker-compose build web

# Restart a specific service
docker-compose restart web

# Execute command in running container
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

# Open shell in container
docker-compose exec web /bin/sh
```

## Database Operations

```bash
# Run migrations in container
docker-compose exec web python manage.py migrate

# Import card data
docker-compose exec web python manage.py importjson

# Create database backup
docker-compose exec db pg_dump -U postgres fowsim > backup.sql
```

## Notes

- The app runs on port 1337 via nginx
- PostgreSQL data persists in a Docker volume
- Environment variables loaded from `.env` file
- First run requires migrations and possibly card import
