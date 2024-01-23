import random
from faker import Faker
from main.models import Etudiant, Personnel, Enseignant, Comptable, Programme,  Tuteur, Ue, Matiere, Evaluation, Competence, Semestre, Domaine, Parcours, AnneeUniversitaire, Note
from cahier_de_texte.models import Seance
from django.contrib.auth.models import User 
from django.contrib.auth.models import Group, Permission


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
        if i == 10:
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

def create_groups_if_exist(request):
    permissions = [
        'view', 'add', 'change', 'delete', "diplome", "carte", "releve_details", "releve_synthetique",
    ]
    applications = "main"
    permissions_all_directeur_des_etudes = [
        "annee universitaire", "competence",
        "comptable", "conge", "Directeur des études",
        "domaine", "enseignant", "Etudiant", "evaluation",
        "fiche de paie", "information", "matiere", "note",
        "paiement", "parcours", "personnel", "programme",
        "salaire", "seance", "semestre", "tuteur", "ue"
        ]

    permissions_directeur_des_etudes = {
        "view": permissions_all_directeur_des_etudes,
        "add": permissions_all_directeur_des_etudes,
        "change": permissions_all_directeur_des_etudes,
        "delete": permissions_all_directeur_des_etudes,
        "diplome": ["Etudiant"],
        "releve_details": ["Etudiant"],
        "releve_synthetique": ["Etudiant"],
        "carte": ["Etudiant"],
        "attestation": ["Etudiant"]
        }

    permissions_etudiant = {
        "view": ["etudiant", "matiere", "ue", "evaluation", "note", "seance"],
        "add": ["seance"],
        "change": ["seance"],
        "delete": [],
        "releve_details": ["etudiant"],
        "releve_synthetique": ["etudiant"],
    }

    permissions_enseignant = {
        "view": ["etudiant", "matiere", "ue", "evaluation", "note", "enseignant", "seance",],
        "add": ["evaluation", "note"],
        "change": ["evaluation", "note", "seance"],
        "delete": ["evaluation", "note"],
    }

    permissions_comptable = {
        "view": ["fiche de paie", "information", "personnel", "salaire", "etudiant", "enseignant", "tuteur"],
        "add": ["fiche de paie", "information", "salaire",],
        "change": ["fiche de paie", "information", "salaire",],
        "delete": [],
    }

    permissions_secretaire = {
        "view": ["etudiant", "matiere", "ue", "evaluation", "note", "enseignant", "seance", "tuteur"],
        "add": ["evaluation", "note", "seance", "ue", "matiere", "enseignant", "tuteur", "etudiant"],
        "change": ["evaluation", "note", "seance", "ue", "matiere", "enseignant", "tuteur", "etudiant"],
        "delete": ["evaluation", "note"],
        "releve_details": ["etudiant"],
        "releve_synthetique": ["etudiant"],
        "carte": ["etudiant"],
        "attestation": ["etudiant"]
    }

    groupe, is_created = Group.objects.get_or_create(
        name="directeur_des_etudes")
    if is_created:
        # Ajouter des permission
        add_permissions_to_groupe(groupe, permissions_directeur_des_etudes)

    groupe, is_created = Group.objects.get_or_create(name="etudiant")
    if is_created:
        add_permissions_to_groupe(groupe, permissions_etudiant)

    groupe, is_created = Group.objects.get_or_create(name="enseignant")
    if is_created:
        add_permissions_to_groupe(groupe, permissions_enseignant)

    groupe, is_created = Group.objects.get_or_create(name="comptable")
    if is_created:
        add_permissions_to_groupe(groupe, permissions_comptable)

    groupe, is_created = Group.objects.get_or_create(name="secretaire")
    if is_created:
        add_permissions_to_groupe(groupe, permissions_secretaire)

def add_permissions_to_groupe(groupe, model_dictionnary):
    permissions_name = []
    for permission_key in model_dictionnary:
        permissions = model_dictionnary[permission_key]
        if permissions:
            for permission in permissions:
                permissions_name.append(permission_key+" "+permission)

    for name in permissions_name:
        try:
            permission = Permission.objects.filter(name__contains=name).get()
        except Exception as e:
            print(":::: Exception ::::")
        groupe.permissions.add(permission)

