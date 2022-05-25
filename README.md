# Running the Server Locally

1. Create a python3 virtual environment (3.9.6):
`python -m venv /path/to/make/venv`

2. Use that virtual environment (must activate every time you open a new prompt)
    - Windows: `/path/to/venv/Scripts/activate` 
    - Linux/MacOS: `. /path/to/venv/bin/activate`

3. Install requirements (If you add packages with pip, add them to requirements.txt using "pip freeze > requirements.txt"). If running on linux or mac, remove the line for Twisted from the requirements.txt file (dont commit this change)
> pip install -r requirements.txt

4. Install PostgreSQL and set up a local database.

5. Create a .env file in the root directory of the repository and populate it with the following, filling in as necessary with information from your Postgres install. Set `DJANGO_SECRET_KEY` as anything, since it doesn't matter for local development, but if you want to generate one properly execute the python code below the example .env file:
```
DJANGO_SECRET_KEY=
DB_USER=
DB_NAME=
DB_PASS=
DB_HOST=
DB_PORT=
```

```sh
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

6. Apply the schema to the database:
`python manage.py migrate`

7. Create a superuser account to use on your local development server:
`python manage.py createsuperuser`

8. Run the server:
`python manage.py runserver`

You can now access all the pages at localhost e.g. http://127.0.0.1:8000/search/

# Docker Setup

1. Edit `docker-compose.yml` to setup the database

2. Ensure `.env` is setup.
```
DJANGO_SECRET_KEY=(Run the command above to get this)
DB_USER=fowsim
DB_NAME=fowsim
DB_PASS=CHANGEME
DB_HOST=db
DB_PORT=5432
```

3. Run `docker-compose up -d --build`

4. Setup database running this command:
`docker-compose exec web python manage.py migrate --noinput`

5. Create the superuser:
`docker-compose exec web python manage.py createsuperuser`

6. Head to `http://localhost:1337` to enjoy the docker setup :D

# How to Contribute
Join us on [Discord](https://discord.com/invite/8S5XW6pUEF) and let us know about your interest in helping develop Force of Wind!

For approved contributors, see [here](/CONTRIBUTORS.md) for info on specific info on how to contribute.
