from faker import Faker
from datetime import timedelta
import random
from django.utils import timezone
from .models import Seance, Matiere, Semestre, Etudiant, Enseignant, SeancePlannifier

fake = Faker()

def create_fake_seance(seme,matieres):
    intitule = fake.sentence()
    date_et_heure_debut = fake.date_time_this_year()
    date_et_heure_fin = date_et_heure_debut + timedelta(hours=2)
    description = fake.paragraph()
    auteur = Etudiant.objects.order_by('?').first()  # Get a random Etudiant
    valider = fake.boolean()
    matiere = matieres.objects.order_by('?').first()  # Get a random Matiere
    semestre = seme  # Get a random Semestre
    enseignant = Enseignant.objects.order_by('?').first()  # Get a random Enseignant
    commentaire = fake.paragraph()
    seance_plannifier = SeancePlannifier.objects.order_by('?').first()  # Get a random SeancePlannifier

    seance_instance = Seance.objects.create(
        intitule=intitule,
        date_et_heure_debut=date_et_heure_debut,
        date_et_heure_fin=date_et_heure_fin,
        description=description,
        auteur=auteur,
        valider=valider,
        matiere=matiere,
        semestre=semestre,
        enseignant=enseignant,
        commentaire=commentaire,
        seancePlannifier=seance_plannifier
    )

    return seance_instance

# Usage example:
# Generate and save 10 fake Seance instances
def creer_seance(nombre) :
    semestre = Semestre.objects.order_by('?').first()
    ues = semestre.get_all_ues()
    for ue in ues :                   
        matieres = ue.matiere_set.all()
        
    for _ in range(nombre):
        print(create_fake_seance(semestre,matieres))
