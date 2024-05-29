from main.models import AnneeUniversitaire, Enseignant, Etudiant, Evaluation, Matiere, Semestre, Ue
import datetime
import random
from faker import Faker
import decimal



fake = Faker()

# Obtenir ou créer l'année universitaire actuelle
annee_universitaire = AnneeUniversitaire.objects.get_or_create(
    annee=2023,
)[0]

# Créer ou obtenir un semestre
semestre = Semestre.objects.get_or_create(
    libelle='S1',
    annee_universitaire=annee_universitaire,
)[0]

# Créer des étudiants
etudiant1 = Etudiant.objects.create(
    nom="TCHABANA",
    prenom="Abdoul Hafiz",
    sexe="M",
    datenaissance=fake.date_of_birth(minimum_age=18, maximum_age=30),
    lieunaissance=fake.city()[:10],
    contact=fake.phone_number(),
    email=fake.email()[:10],
    adresse=fake.address()[:10],
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

etudiant2 = Etudiant.objects.create(
    nom="ALISERA",
    prenom="Manar",
    sexe="F",
    datenaissance=fake.date_of_birth(minimum_age=18, maximum_age=30),
    lieunaissance=fake.city()[:10],
    contact=fake.phone_number(),
    email=fake.email()[:10],
    adresse=fake.address()[:10],
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


# Créer ou obtenir un enseignant responsable
enseignant = Enseignant.objects.filter(email="sabirou.teouri@ifnti.com")[0]

# Créer des instances d'UE
ue_technologie = Ue.objects.create(
    codeUE="TEC101",
    libelle="Introduction à la Technologie",
    niveau="1",  # Licence
    type="Technologie",
    nbreCredits=30,
    minValue=10,
    heures=15.0,  # Total d'heures d'enseignement
    enseignant=enseignant,  # Lien vers l'enseignant responsable
)

ue_maths = Ue.objects.create(
    codeUE="MAT101",
    libelle="Mathématiques de base",
    niveau="1",  # Licence
    type="Maths",
    nbreCredits=30,
    minValue=10,
    heures=20.0,
    enseignant=enseignant,
)

ue_communication = Ue.objects.create(
    codeUE="COM101",
    libelle="Introduction à la Communication",
    niveau="1",
    type="Communication",
    nbreCredits=20,
    minValue=10,
    heures=10.0,
    enseignant=enseignant,
)


# Créer des instances de Matiere
matiere1 = Matiere.objects.create(
    codematiere="CS101A",  # Code unique pour la matière
    libelle="Programmation en Python",
    coefficient=2,
    minValue=7,
    heures=decimal.Decimal('50.0'),  # Nombre total d'heures
    abbreviation="Python",
    enseignant=enseignant,  # Lien vers l'enseignant
    ue=ue_technologie,  # Lien vers l'UE
)

matiere2 = Matiere.objects.create(
    codematiere="CS101B",
    libelle="Algorithmes et structures de données",
    coefficient=3,
    minValue=7,
    heures=decimal.Decimal('70.0'),
    abbreviation="Algo",
    enseignant=enseignant,
    ue=ue_maths,
)

# Créer une évaluation pour le semestre
evaluation_math = Evaluation.objects.create(
    libelle='Examen Mathématiques',
    ponderation=50,
    date=datetime.date(2024, 6, 15),
    matiere=matiere1,
    semestre=semestre,
)

evaluation_angl = Evaluation.objects.create(
    libelle='Examen Anglais',
    ponderation=50,
    date=datetime.date(2024, 6, 16),
    matiere=matiere2,
    semestre=semestre,
)

# Associer les étudiants aux évaluations

# Ajouter des étudiants à l'évaluation de mathématiques
evaluation_math.etudiants.add(etudiant1, etudiant2)

# Ajouter des étudiants à l'évaluation d'anglais
evaluation_angl.etudiants.add(etudiant1, etudiant2)
