import random
from faker import Faker
from main.models import Etudiant, Personnel, Enseignant, Comptable, Programme,  Tuteur, Ue, Matiere, Evaluation, Competence, Semestre, Domaine, Parcours, AnneeUniversitaire, Note
from cahier_de_texte.models import Seance
from django.contrib.auth.models import User 

def run():
    users = User.objects.exclude(username__in=["malia", "amk", "walid", 'kaiser'])
    for user in users:
        user.delete()
    
    clean_data_base()

    

def clean_data_base():
    print("Drop all object ..... 7")
    Programme.objects.all().delete()
    print("Drop all object ..... 7")
    Seance.objects.all().delete()
    print("Drop all object ..... 1")
    Personnel.objects.all().delete()
    print("Drop all object ..... 2")
    Enseignant.objects.all().delete()
    print("Drop all object ..... 3")
    Etudiant.objects.all().delete()
    print("Drop all object ..... 4")
    Comptable.objects.all().delete()
    print("Drop all object ..... 5")
    Tuteur.objects.all().delete()
    print("Drop all object ..... 6")
    Ue.objects.all().delete()
    print("Drop all object ..... 7")
    Matiere.objects.all().delete()
    print("Drop all object ..... 8")
    Evaluation.objects.all().delete()
    print("Drop all object ..... 9")
    Competence.objects.all().delete()
    print("Drop all object ..... 10")
    Semestre.objects.all().delete()
    print("Drop all object ..... 11")
    Domaine.objects.all().delete()
    print("Drop all object ..... 12")
    Parcours.objects.all().delete()
    print("Drop all object ..... 13")
    Note.objects.all().delete()
    print("Drop all object .....")
    AnneeUniversitaire.objects.all().delete()
    print("Drop all object ..... end")

     # Génération des fausses instances pour le modèle AnneeUniversitaire
    current = False
    for i in range(1,11):
        if i == 9:
            current = True
        annee_universitaire = AnneeUniversitaire(
            annee=2013+i,
            annee_courante=current
        )
        annee_universitaire.save()
        print(f"AnneeUniversitaire créé : {annee_universitaire}")
    
    # Génération des fausses instances pour le modèle Domaine
    domaine = Domaine(
        nom="Siences et technologie",
        description="Siences et technologie"
    )
    domaine.save()
    print(f"Domaine créé : {domaine}")

    # Génération des fausses instances pour le modèle Parcours
    domaines = Domaine.objects.all()

    parcours = Parcours(
        nom="Licence en génie logiciel",
        domaine=domaine,
        description="Licence en génie logiciel"
    )
    
    parcours.save()
    print(f"Parcours créé : {parcours}")

