Setup instructions:

1. Create a python3 virtual environment (3.9.6)
python -m venv /path/to/make/venv

2. Use that virtual environment (must activate every time you open a new prompt)
Windows: /path/to/venv/Scripts/activate
Linux: . /path/to/venv/Scripts/activate

3. Install requirements (If you add packages with pip, add them to requirements.txt using "pip freeze > requirements.txt")
pip install -r requirements.txt

4. Setup a personal settings.py file:
- create a settingsMyName.py file in fowsim/
- copy the contents from settingsHalo.py to settingsMyName.py
- Feel free to commit your personal settings file, but don't commit settings.py (it's in gitignore)
- Create settings.py file with "from .settingsMyName import *"
- Some edits will be made to your settings file shortly

5. Create a local postgres database and match the name/user/pass/port in your settings file

6. Apply the schema to the database
python manage.py migrate

7. Import card data to the database
python manage.py importjson

8. Download card images (may take a little while and can be done while doing other things)
Create a directory in cardDatabase/static called "cards"
python manage.py downloadCardImages

9. Setup a redis queue (This might not be necessary if you aren't working on the game sim parts yet, so can try skip this)
Update your settings file with the port/address for the redis queue

10. create your own user
python manage.py createsuperuser

11. run the server
python manage.py runserver

You can now access all the pages at localhost e.g. http://127.0.0.1:8000/search/