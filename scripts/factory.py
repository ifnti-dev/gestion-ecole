import random
from faker import Faker
from main.models import Etudiant, Personnel, Enseignant, Comptable, Programme, Seance, Tuteur, Ue, Matiere, Evaluation, Competence, Semestre, Domaine, Parcours, AnneeUniversitaire, Note
from django.contrib.auth.models import User 

def run():
    users = User.objects.exclude(username__in=["malia", "amk", "walid", 'kaiser'])
    for user in users:
        user.delete()
    
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

    fake = Faker()

    # Génération des fausses instances pour le modèle AnneeUniversitaire
    current = False
    for i in range(1,10):
        if i == 9:
            current = True
        annee_universitaire = AnneeUniversitaire(
            annee=2013+i,
            annee_courante=current
        )
        annee_universitaire.save()
        print(f"AnneeUniversitaire créé : {annee_universitaire}")
        

    # for _ in range(10):
    #     etudiant = Etudiant(
    #         nom=fake.last_name(),
    #         prenom=fake.first_name(),
    #         sexe=random.choice(['F', 'M']),
    #         datenaissance=fake.date_of_birth(minimum_age=18, maximum_age=30),
    #         lieunaissance=fake.city(),
    #         contact=fake.phone_number(),
    #         email=fake.email(),
    #         adresse=fake.address(),
    #         prefecture=fake.city(),
    #         carte_identity=fake.random_number(digits=10),
    #         nationalite='Togolaise',
    #         anneeentree = fake.random_int(min=2010, max=2023),
    #         seriebac1 = random.choice(['A', 'C', 'D', 'E', 'F1', 'F2', 'F3', 'F4', 'G2']),
    #         seriebac2 = random.choice(['A', 'C', 'D', 'E', 'F1', 'F2', 'F3', 'F4', 'G2']),
    #         anneebac1 = fake.random_int(min=2000, max=2022),
    #         anneebac2 = fake.random_int(min=2000, max=2022),
    #         etablissementSeconde = fake.company(),
    #         francaisSeconde = round(random.uniform(10, 20), 2),
    #         anglaisSeconde = round(random.uniform(10, 20), 2),
    #         mathematiqueSeconde = round(random.uniform(10, 20), 2),
    #         etablissementPremiere = fake.company(),
    #         francaisPremiere = round(random.uniform(10, 20), 2),
    #         anglaisPremiere = round(random.uniform(10, 20), 2),
    #         mathematiquePremiere = round(random.uniform(10, 20), 2),
    #         etablissementTerminale = fake.company(),
    #         francaisTerminale = round(random.uniform(10, 20), 2),
    #         anglaisTerminale = round(random.uniform(10, 20), 2),
    #         mathematiqueTerminale = round(random.uniform(10, 20), 2),
    #     )
        
    #     #etudiant.semestre.add(Semestre.objects.all()[0])
    #     etudiant.save()
    #     print(f"Etudiant créé : {etudiant.user.username}")
        


    # # Création de 10 objets Personnel fictifs
    # for _ in range(10):
    #     # Génération des données aléatoires
    #     nom = fake.last_name()
    #     prenom = fake.first_name()
    #     sexe = random.choice(['F', 'M'])
    #     datenaissance = fake.date_of_birth(minimum_age=18, maximum_age=60)
    #     lieunaissance = fake.city()
    #     contact = fake.phone_number()
    #     email = fake.email()
    #     adresse = fake.address()
    #     prefecture = fake.city()
    #     carte_identity = fake.random_number(digits=8)
    #     nationalite = fake.country()
    #     salaireBrut = fake.pydecimal(left_digits=5, right_digits=2, positive=True)
    #     nbreJrsCongesRestant = random.randint(0, 30)

    #     # Création de l'objet Personnel
    #     personnel = Personnel(
    #         nom=nom,
    #         prenom=prenom,
    #         sexe=sexe,
    #         datenaissance=datenaissance,
    #         lieunaissance=lieunaissance,
    #         contact=contact,
    #         email=email,
    #         adresse=adresse,
    #         prefecture=prefecture,
    #         carte_identity=carte_identity,
    #         nationalite=nationalite,
    #         salaireBrut=salaireBrut,
    #         nbreJrsCongesRestant=nbreJrsCongesRestant,
    #         nbreJrsConsomme=0
    #     )
    #     personnel.save()

    #     print(f"Personnel créé : {personnel}")


    # # # Génération des fausses instances pour le modèle Enseignant
    # personnels = Personnel.objects.all()
    # for _ in range(10):
    #     nom = fake.last_name()
    #     prenom = fake.first_name()
    #     username = f"{prenom.lower()}.{nom.lower()}"
    #     password = fake.password()
    #     enseignant = Enseignant(
    #         nom=fake.last_name(),
    #         prenom=fake.first_name(),
    #         sexe=random.choice(['F', 'M']),
    #         datenaissance=fake.date_of_birth(minimum_age=25, maximum_age=60),
    #         lieunaissance=fake.city(),
    #         contact=fake.phone_number(),
    #         email=fake.email(),
    #         adresse=fake.address(),
    #         prefecture=fake.city(),
    #         carte_identity=fake.random_number(digits=10),
    #         nationalite='Togolaise',
    #         salaireBrut=random.uniform(1000, 5000),
    #         dernierdiplome=None,
    #         nbreJrsCongesRestant=random.randint(0, 30),
    #         nbreJrsConsomme=random.randint(0, 30),
    #         specialite=fake.job(),
    #     )
    #     enseignant.save()
    #     print(f"Enseignant créé : {enseignant}")


    # # Génération des fausses instances pour le modèle Comptable
    # for _ in range(10):
    #     comptable = Comptable(
    #         nom=fake.last_name(),
    #         prenom=fake.first_name(),
    #         sexe=random.choice(['F', 'M']),
    #         datenaissance=fake.date_of_birth(minimum_age=25, maximum_age=60),
    #         lieunaissance=fake.city(),
    #         contact=fake.phone_number(),
    #         email=fake.email(),
    #         adresse=fake.address(),
    #         prefecture=fake.city(),
    #         carte_identity=fake.random_number(digits=10),
    #         nationalite='Togolaise',
    #         salaireBrut=random.uniform(1000, 5000),
    #         dernierdiplome=None,
    #         nbreJrsCongesRestant=random.randint(0, 30),
    #         nbreJrsConsomme=random.randint(0, 30),
    #     )
    #     comptable.save()
    #     print(f"Comptable créé : {comptable}")

    # # Génération des fausses instances pour le modèle Tuteur
    # etudiants = Etudiant.objects.all()
    # for _ in range(10):
    #     tuteur = Tuteur(
    #         nom=fake.last_name(),
    #         prenom=fake.first_name(),
    #         sexe=random.choice(['F', 'M']),
    #         type=random.choice(["Père", "Mère", "Tuteur"]),
    #         contact=fake.phone_number(),
    #         profession=fake.job(),
    #     )
    #     tuteur.save()
    #     print(f"Tuteur créé : {tuteur}")

    # # Génération des fausses instances pour le modèle Domaine
    # domaine = Domaine(
    #     nom="Siences et technologie",
    #     description=fake.sentence()
    # )
    # domaine.save()
    # print(f"Domaine créé : {domaine}")

    # # Génération des fausses instances pour le modèle Parcours
    # domaines = Domaine.objects.all()

    # parcours = Parcours(
    #     nom="Licence en génie logiciel",
    #     domaine=domaine,
    #     description=fake.sentence()
    # )
    
    # parcours.save()
    # print(f"Parcours créé : {parcours}")

    # # Génération des fausses instances pour le modèle Ue
    # matieres_ue = {
    #     "DAP" : ["Python", "Introduction à l'informatique", "Monde binaire", "algorithmie"],
    #     "BD" : ["MRD", "MCD", "postgresql"],
    #     "TDSS" : ["Html/css", "Xml", "Xsd", "Dtd"],
    #     "COMMUNICATION" : ["Français", "Anglais"],
    #     "ELECTRONIQUE EMBARQUÉ" : ["Arduino", "Assembleur"]
    # }

    # for ue_key in matieres_ue:
    #     # Génération des données aléatoires
    #     libelle = ue_key
    #     nbreCredits = random.randint(1, 10)
    #     heures = round(random.uniform(10, 100), 1)
    #     enseignant = random.choice(Enseignant.objects.all())

    #     # Création de l'objet Ue
    #     ue = Ue.objects.create(
    #         libelle=libelle,
    #         nbreCredits=nbreCredits,
    #         heures=heures,
    #         enseignant=enseignant,
    #     )
        
    #     print(f"Ue créé : {ue}")

    #     for matiere in matieres_ue[ue_key]:
    #         matiere = Matiere(
    #             libelle=matiere,
    #             coefficient=random.uniform(1, 3),
    #             heures=round(random.uniform(10, 100), 1),
    #             ue=ue,
    #             minValue = fake.random_int(min=5, max=12),
    #             is_active = True
    #         )
    #         matiere.save()
    #         print(f"Matiere créé : {matiere}")

    # # """ 
    # # import main.factory
    # # """
