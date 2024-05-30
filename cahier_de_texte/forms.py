from django import forms
from cahier_de_texte.models import Seance

class SeanceForm(forms.ModelForm):
    class Meta:
        model = Seance
        fields = ['intitule', 'date_et_heure_debut', 'date_et_heure_fin', 'description','auteur', 'matiere', 'semestre', 'enseignant',"commentaire",'eleves_presents',"seancePlannifier"]