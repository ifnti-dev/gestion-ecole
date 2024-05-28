from django.contrib import admin
from .models import User, Enseignant, Evaluation, CompteBancaire, Fournisseur, Domaine,Information, Parcours,Programme, Matiere, Etudiant, Competence, Note, Semestre, Ue, AnneeUniversitaire, Personnel, Tuteur, Paiement, FicheDePaie, Frais, CompteEtudiant, VersmentSalaire, Conge
from cahier_de_texte.models import Seance
from planning.models import Planning,SeancePlannifier
from main.forms import EnseignantForm
from import_export.admin import ImportExportModelAdmin


@admin.register(Etudiant)
class EtudiantImportExport(ImportExportModelAdmin):
    pass

@admin.register(Tuteur)
class TuteurImportExport(ImportExportModelAdmin):
    pass

@admin.register(Enseignant)
class EnseignantImportExport(ImportExportModelAdmin):
    pass

@admin.register(Ue)
class UeImportExport(ImportExportModelAdmin):
    pass

@admin.register(Matiere)
class MatiereImportExport(ImportExportModelAdmin):
    pass

@admin.register(Semestre)
class SemestreImportExport(ImportExportModelAdmin):
    pass

@admin.register(Programme)
class ProgrammeImportExport(ImportExportModelAdmin):
    pass

@admin.register(Competence)
class CompetenceImportExport(ImportExportModelAdmin):
    pass

@admin.register(Note)
class NoteImportExport(ImportExportModelAdmin):
    pass


@admin.register(Personnel)
class PersonnelImportExport(ImportExportModelAdmin):
    pass

@admin.register(AnneeUniversitaire)
class AnneeUniversitaireImportExport(ImportExportModelAdmin):
    pass


admin.site.unregister(User)
@admin.register(User)
class UserImportExport(ImportExportModelAdmin):
    pass
@admin.register(Evaluation)
class EvaluationImportExport(ImportExportModelAdmin):
    pass
class EnseignantAdmin(admin.ModelAdmin):
    form = EnseignantForm

#admin.site.register(Programme)
#admin.site.register(Enseignant, EnseignantAdmin)
#admin.site.register(Matiere)
#admin.site.register(Etudiant)
#admin.site.register(Competence)
#admin.site.register(Note)
#admin.site.register(Ue)
#admin.site.register(Semestre)
#admin.site.register(Comptable)
#admin.site.register(Tuteur)
#admin.site.register(Personnel)
#admin.site.register(AnneeUniversitaire)
admin.site.register(Information)
admin.site.register(Paiement)
#admin.site.register(DirecteurDesEtudes)
admin.site.register(Seance)
admin.site.register(FicheDePaie)
admin.site.register(Parcours)
admin.site.register(Domaine)
admin.site.register(Frais)
admin.site.register(CompteBancaire)
admin.site.register(CompteEtudiant)
admin.site.register(VersmentSalaire)
admin.site.register(Fournisseur)
admin.site.register(Planning)
admin.site.register(SeancePlannifier)
admin.site.register(Conge)
from django import forms

class EtudiantAdminForm(forms.ModelForm):
    class Meta:
        model = Etudiant
        exclude = ['nom', 'prenom', 'contact', 'sexe', 'adresse', 'datenaissance', 'lieunaissance', 'prefecture', 'is_active', 'seriebac1', 'seriebac2', 'anneebac1', 'anneebac2', 'etablissementSeconde', 'etablissementPremiere', 'etablissementTerminale', 'francaisSeconde', 'francaisPremiere','francaisTerminale', 'anglaisSeconde', 'anglaisPremiere', 'anglaisTerminale', 'mathematiqueSeconde', 'mathematiquePremiere', 'mathematiqueTerminale', 'semestres']


    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.email = instance.generate_email()
        if commit:
            instance.save()
        return instance
