import random
from faker import Faker
from main.models import Etudiant, Personnel, FicheDePaie, Enseignant, Comptable, Programme,  Tuteur, Ue, Matiere, Evaluation, Competence, Semestre, Domaine, Parcours, AnneeUniversitaire, Note
from cahier_de_texte.models import Seance
from django.contrib.auth.models import User 
from django.contrib.auth.models import Group, Permission


def run():
    users = User.objects.exclude(username__in=["malia", "amk", "walid", 'kaiser'])
    for user in users:
        user.delete()
    
    create_groups_if_exist()
    clean_data_base()
    response = input("Veux tu créer des seeders ? (oui|non) ")
    if response.lower() in ['o', 'oui', 'y', 'yes']:
        create_seed()
    else:
        create_faker()

def clean_data_base():
    models = [AnneeUniversitaire, Programme, Seance, Personnel, Enseignant, Etudiant, Comptable, Tuteur, Ue, Matiere, Evaluation, Competence, Semestre, Domaine, Note]
    for model in models:
        print(f"::::::::::::::::::::::: Delete Model {model.__name__} :::::::::::::::::::::::")
        model.objects.all().delete()
        
def create_faker():      
    print("::::::::::::::::::::::: Create Faker Data :::::::::::::::::::::::")
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
        print(f"::: AnneeUniversitaire créé : {annee_universitaire} :::")
    
    # Génération des fausses instances pour le modèle Domaine
    domaine = Domaine(
        nom="Siences et technologie",
        description="Siences et technologie"
    )
    domaine.save()
    print(f"::: Domaine créé : {domaine} :::")

    # Génération des fausses instances pour le modèle Parcours
    domaines = Domaine.objects.all()

    parcours = Parcours(
        nom="Licence en génie logiciel",
        domaine=domaine,
        description="Licence en génie logiciel"
    )
    
    parcours.save()
    print(f"::: Parcours créé : {parcours} :::")
    
    response = input("Veux tu créer des instances de tests ? (oui|non) ")
    if response.lower() in ['o', 'oui', 'y', 'yes']:
        fake = Faker()
        s1 = AnneeUniversitaire.objects.last().semestre_set.first()
        for _ in range(1):
            etudiant = Etudiant(
                nom=fake.last_name(),
                prenom=fake.first_name(),
                sexe=random.choice(['F', 'M']),
                datenaissance=fake.date_of_birth(minimum_age=18, maximum_age=30),
                lieunaissance=fake.city(),
                contact=fake.phone_number(),
                email=fake.email(),
                adresse=fake.address(),
                prefecture=fake.city(),
                carte_identity=fake.random_number(digits=10),
                nationalite='Togolaise',
                anneeentree = 2023,
                seriebac1 = random.choice(['A', 'C', 'D', 'E', 'F1', 'F2', 'F3', 'F4', 'G2']),
                seriebac2 = random.choice(['A', 'C', 'D', 'E', 'F1', 'F2', 'F3', 'F4', 'G2']),
                anneebac1 = fake.random_int(min=2000, max=2022),
                anneebac2 = fake.random_int(min=2000, max=2022),
                etablissementSeconde = fake.company(),
                francaisSeconde = round(random.uniform(10, 20), 2),
                anglaisSeconde = round(random.uniform(10, 20), 2),
                mathematiqueSeconde = round(random.uniform(10, 20), 2),
                etablissementPremiere = fake.company(),
                francaisPremiere = round(random.uniform(10, 20), 2),
                anglaisPremiere = round(random.uniform(10, 20), 2),
                mathematiquePremiere = round(random.uniform(10, 20), 2),
                etablissementTerminale = fake.company(),
                francaisTerminale = round(random.uniform(10, 20), 2),
                anglaisTerminale = round(random.uniform(10, 20), 2),
                mathematiqueTerminale = round(random.uniform(10, 20), 2),
            )
            
            #etudiant.semestre.add(Semestre.objects.all()[0])
            etudiant.save()
            # etudiant.semestres.add(s1)
            print(f"Etudiant créé : {etudiant.user.username}")
        
        for _ in range(2):
            # Génération des données aléatoires
            nom = fake.last_name()
            prenom = fake.first_name()
            sexe = random.choice(['F', 'M'])
            datenaissance = fake.date_of_birth(minimum_age=18, maximum_age=60)
            lieunaissance = fake.city()
            contact = fake.phone_number()
            email = fake.email()
            adresse = fake.address()
            prefecture = fake.city()
            carte_identity = fake.random_number(digits=8)
            nationalite = fake.country()
            salaireBrut = fake.pydecimal(left_digits=5, right_digits=2, positive=True)
            nbreJrsCongesRestant = random.randint(0, 30)

            # Création de l'objet Personnel
            personnel = Personnel(
                nom=nom,
                prenom=prenom,
                sexe=sexe,
                datenaissance=datenaissance,
                lieunaissance=lieunaissance,
                contact=contact,
                email=email,
                adresse=adresse,
                prefecture=prefecture,
                carte_identity=carte_identity,
                nationalite=nationalite,
                salaireBrut=salaireBrut,
                nbreJrsCongesRestant=nbreJrsCongesRestant,
                nbreJrsConsomme=0
            )
            personnel.save()

            print(f"Personnel créé : {personnel}")

        for _ in range(1):
            enseignant = Enseignant(
                nom=fake.last_name(),
                prenom=fake.first_name(),
                sexe=random.choice(['F', 'M']),
                datenaissance=fake.date_of_birth(minimum_age=25, maximum_age=60),
                lieunaissance=fake.city(),
                contact=fake.phone_number(),
                email=fake.email(),
                adresse=fake.address(),
                prefecture=fake.city(),
                carte_identity=fake.random_number(digits=10),
                nationalite='Togolaise',
                salaireBrut=random.uniform(1000, 5000),
                dernierdiplome=None,
                nbreJrsCongesRestant=random.randint(0, 30),
                nbreJrsConsomme=random.randint(0, 30),
                specialite=fake.job(),
            )
            enseignant.save()
            print(f"Enseignant créé : {enseignant}")

def create_seed():
    print("::::::::::::::::::::::: Create Seed Data :::::::::::::::::::::::")
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
        print(f"::: AnneeUniversitaire créé : {annee_universitaire} :::")
    
    # Génération des fausses instances pour le modèle Domaine
    domaine = Domaine(
        nom="Siences et technologie",
        description="Siences et technologie"
    )
    domaine.save()
    print(f"::: Domaine créé : {domaine} :::")

    # Génération des fausses instances pour le modèle Parcours
    domaines = Domaine.objects.all()

    parcours = Parcours(
        nom="Licence en génie logiciel",
        domaine=domaine,
        description="Licence en génie logiciel"
    )
    
    parcours.save()
    print(f"::: Parcours créé : {parcours} :::")
    enseignant = Enseignant(
        nom="TEOURI",
        prenom="Mohamed Sabirou",
        sexe="M",
        datenaissance="1966-05-03",
        lieunaissance="Sokodé",
        contact="90919141",
        email="sabirou.teouri@ifnti.com",
        adresse="Sokodé",
        prefecture="Sokodé",
        carte_identity=0,
        nationalite='Togolaise',
        salaireBrut=0,
        dernierdiplome=None,
        nbreJrsCongesRestant=30,
        nbreJrsConsomme=0,
        specialite="Base de donnée",
    )
    enseignant.save()
    group = Group.objects.get(name="directeur_des_etudes")
    enseignant.user.groups.add(group)
    print(f"Enseignant créé : {enseignant.user.username}")
    user = User.objects.create_user(username="ifnti", password="ifnti", is_superuser=True)
    user.groups.add(group)
    print(f"User directeur créé : {user}")

def create_groups_if_exist():
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
        "salaire", "seance", "semestre", "tuteur", "ue", "seance plannifier" , "plannig"
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
        "view": ["etudiant", "matiere", "ue", "evaluation", "note", "seance", "seance plannifier", "plannig"],
        "add": ["seance"],
        "change": ["seance"],
        "delete": [],
        "releve_details": ["etudiant"],
        "releve_synthetique": ["etudiant"],
    }

    permissions_enseignant = {
        "view": ["etudiant", "matiere", "ue", "evaluation", "note", "enseignant", "seance", "seance plannifier", "plannig"],
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
        "view": ["etudiant", "matiere", "ue", "evaluation", "note", "enseignant", "seance", "tuteur", "seance plannifier", "plannig"],
        "add": ["evaluation", "note", "seance", "ue", "matiere", "enseignant", "tuteur", "etudiant", "seance plannifier", "plannig"],
        "change": ["evaluation", "note", "seance", "ue", "matiere", "enseignant", "tuteur", "etudiant", "seance plannifier", "plannig"],
        "delete": ["evaluation", "note", "seance plannifier", "plannig"],
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
            permission = Permission.objects.filter(name__contains=name).first()
            groupe.permissions.add(permission)
        except Exception as e:
            #print(e, name)
            print(":::: Exception ::::")

