# Projet Gestion université ifnti
Application de gestion de l'ifnti

# Installation et lancement de l'application

Pour lancer l'applcation, il faut installer python 3 et Django dans sa drnière version.

```python
$ python3 -m venv .ifnti_env
$ source ./ifnti_env/bin/activate
```

## Procédure d’exécution du projet

1.  Créer une base de donnée au choix
2. Créer et configurer le fichier .env  comme suit : 

```python
DB_USER=nom_utilisateur
DB_PASSWORD=motdepasse_utilisateur
DB_FIRST_HOST=address_ip de votre machine
DB_SECOND_HOST=127.0.0.1
DB_PORT=5432
DATABASE=nom_de_la_base de donnée crée
SECRET_KEY=_mot_clé au choix
```

3.  Exécuter le fichier requirements.txt

```shell
pip install -r requirements.txt
```

4.  Commenter dans le projet projet_ifnti,  dans le fichier urls.py , dans urlpatterns  tout

```python
urlpatterns = [
path("", view=views.dashboard, name='dashboard'),
path('admin/', admin.site.urls),
path('main/', include('main.urls')),
]
```

6.  Pour la créer des migrations,  de l'utilisateur , lancé le fichier : `init_db.sh`

```txt
Pour ce faire il faut : 
_donner les permissions sur le ficher : sudo chmod 777 init_db.sh

_lancer la commande a la racine du projet : ./init_db.sh
```

**Pour lancer un script** (Script de  création du user `ifnti` avec le mot de passe `ifnti`)

```python
python3 manage.py runscript factory
```


8.  Maintenant lancer le projet

```python
python3 manage.py runserver
```


Ensuite l'application est accessible à l'adresse: `http://localhost:8000/main`


## Comment importer les données

- User
- Personnel 
- Enseigent
- Ue
- Matier
- Evaluation
- Parcours
- Programmes