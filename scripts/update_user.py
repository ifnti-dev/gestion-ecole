import random

from main.models import Etudiant

def run():
    etudiants = Etudiant.objects.all()
    for etudiant in etudiants:
        #print(etudiant.id)
        etudiant.user.username = etudiant.id 
        etudiant.user.save()
