
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
rm -f db.sqlite3
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runscript factory
python3 manage.py createsuperuser

