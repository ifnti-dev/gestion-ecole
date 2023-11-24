from import_export import resources
from .models import Enseignant, Evaluation, Domaine,Information, Parcours,Programme, Matiere, Etudiant, Competence, Note, Comptable, Semestre, Ue, AnneeUniversitaire, Personnel, Tuteur, Paiement, FicheDePaie, DirecteurDesEtudes, Seance

class EtudiantResource(resources.ModelResource):
    class Meta:
        model = Etudiant