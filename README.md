# Projet Gestion université ifnti
Application de gestion de l'ifnti

# Preambule
Creation d'une base de donnée avec postgresql:

```bash
$ sudo -i -u postgres
$ psql
# CREATE DATABASE <DB_NAME>;
```


# Installation et lancement de l'application
Pour lancer l'applcation, il faut installer python 3 et Django dans sa drnière version.
```bash
$ python3 -m venv .ifnti_env
$ source ./ifnti_env/bin/activate
$ python3 manage.py migrate
$ python3 manage.py createsuperuser # Après ajouter le "username" du superuser dans la list se trouvant dans le fichier main.factory
$ python3 manage.py shell
>>> import main.factory
>>>
>>>
>>> exit() 
$ python3 manage.py runserver
```

Ensuite l'application est accessible à l'adresse: http://localhost:8000/main
