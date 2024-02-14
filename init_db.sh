
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
rm -f db.sqlite3
python manage.py makemigrations
python manage.py migrate
python3 manage.py runscript factory
python manage.py createsuperuser

