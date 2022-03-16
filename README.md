Setup instructions:

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

7. Import card data to the database:
`python manage.py importjson`

8. Setup a redis queue (This might not be necessary if you aren't working on the game sim parts yet, so can try skip this). If you do, add the port and address for the redis queue to your .env file:
```
REDIS_HOST=
REDIS_PORT=
```

9. create your own user:
`python manage.py createsuperuser`

10. run the server:
`python manage.py runserver`

You can now access all the pages at localhost e.g. http://127.0.0.1:8000/search/