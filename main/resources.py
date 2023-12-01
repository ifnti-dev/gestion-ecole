from import_export import resources
from .models import Enseignant, Frais, CompteEtudiant, CompteBancaire, Salaire, Fournisseur, Charge, Conge, Evaluation, Domaine,Information, Parcours,Programme, Matiere, Etudiant, Competence, Note, Comptable, Semestre, Ue, AnneeUniversitaire, Personnel, Tuteur, Paiement, FicheDePaie, DirecteurDesEtudes, Seance


class AnneeUniversitaireResource(resources.ModelResource):
    class Meta:
        model = AnneeUniversitaire

class DomaineResource(resources.ModelResource):
    class Meta:
        model = Domaine

class EnseignantResource(resources.ModelResource):
    class Meta:
        model = Enseignant

class ComptableResource(resources.ModelResource):
    class Meta:
        model = Comptable

class DirecteurDesEtudesResource(resources.ModelResource):
    class Meta:
        model = DirecteurDesEtudes

class EvaluationResource(resources.ModelResource):
    class Meta:
        model = Evaluation

class MatiereResource(resources.ModelResource):
    class Meta:
        model = Matiere

class PersonnelResource(resources.ModelResource):
    class Meta:
        model = Personnel

class EtudiantResource(resources.ModelResource):
    class Meta:
        model = Etudiant

class UeResource(resources.ModelResource):
    class Meta:
        model = Ue

class SemestreResource(resources.ModelResource):
    class Meta:
        model = Semestre

class SeanceResource(resources.ModelResource):
    class Meta:
        model = Seance

class ParcoursResource(resources.ModelResource):
    class Meta:
        model = Parcours

class ProgrammeResource(resources.ModelResource):
    class Meta:
        model = Programme

class NoteResource(resources.ModelResource):
    class Meta:
        model = Note

class FraisResource(resources.ModelResource):
    class Meta:
        model = Frais

class CompteEtudiantResource(resources.ModelResource):
    class Meta:
        model = CompteEtudiant

class PaiementResource(resources.ModelResource):
    class Meta:
        model = Paiement

class CompteBancaireResource(resources.ModelResource):
    class Meta:
        model = CompteBancaire

class SalaireResource(resources.ModelResource):
    class Meta:
        model = Salaire

class FournisseurResource(resources.ModelResource):
    class Meta:
        model = Fournisseur

class InformationResource(resources.ModelResource):
    class Meta:
        model = Information

class FicheDePaieResource(resources.ModelResource):
    class Meta:
        model = FicheDePaie

class ChargeResource(resources.ModelResource):
    class Meta:
        model = Charge

class CongeResource(resources.ModelResource):
    class Meta:
        model = Conge


def get_model_by_name(model_name):
    model_name = model_name.lower()
    models = {
        'anneeuniversitaire': AnneeUniversitaire,
        'domaine': Domaine,
        'enseignant': Enseignant,
        'comptable': Comptable,
        'directeurdesetudes': DirecteurDesEtudes,
        'evaluation': Evaluation,
        'matiere': Matiere,
        'personnel': Personnel,
        'etudiant': Etudiant,
        'ue': Ue,
        'semestre': Semestre,
        'seance': Seance,
        'parcours': Parcours,
        'programme': Programme,
        'note': Note,
        'frais': Frais,
        'compteetudiant': CompteEtudiant,
        'paiement': Paiement,
        'comptebancaire': CompteBancaire,
        'salaire': Salaire,
        'fournisseur': Fournisseur,
        'information': Information,
        'fichedepaie': FicheDePaie,
        'charge': Charge,
        'conge': Conge,
    }
    return models.get(model_name)

def get_resource_by_name(model_name):
    model_name = model_name.lower()
    resources = {
        'anneeuniversitaire': AnneeUniversitaireResource,
        'domaine': DomaineResource,
        'enseignant': EnseignantResource,
        'comptable': ComptableResource,
        'directeurdesetudes': DirecteurDesEtudesResource,
        'evaluation': EvaluationResource,
        'matiere': MatiereResource,
        'personnel': PersonnelResource,
        'etudiant': EtudiantResource,
        'ue': UeResource,
        'semestre': SemestreResource,
        'seance': SeanceResource,
        'parcours': ParcoursResource,
        'programme': ProgrammeResource,
        'note': NoteResource,
        'frais': FraisResource,
        'compteetudiant': CompteEtudiantResource,
        'paiement': PaiementResource,
        'comptebancaire': CompteBancaireResource,
        'salaire': SalaireResource,
        'fournisseur': FournisseurResource,
        'information': InformationResource,
        'fichedepaie': FicheDePaieResource,
        'charge': ChargeResource,
        'conge': CongeResource,
    }
    return resources.get(model_name)