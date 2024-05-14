from datetime import date
from django.contrib.auth.models import User

def construire_nom_utilisateur(nom, prenom):
    return (nom+prenom).lower()

def create_auth_user(nom, prenom, email):
    username = construire_nom_utilisateur(nom, prenom)
    username = username.replace(" ", "")
    year = date.today().year
    password = 'ifnti' + str(year) + '!'
    user = User.objects.create_user(username=username, password=password, email=email, last_name=nom, first_name=prenom, is_staff=False)
    return user

def chercher_utilisateur(nom, prenom):
    username = construire_nom_utilisateur(nom, prenom)
    print(username)
    return User.objects.filter(username=username).first()



