from typing import Any, Dict
import re
from typing import Any, Dict
from django import forms

from main.utils.forms_utils import chercher_utilisateur
from .models import Evaluation, Information, Programme, Parcours, Note, Utilisateur, Personnel, Enseignant, Etudiant, Matiere, AnneeUniversitaire, Ue, Tuteur, Semestre
from django.core.exceptions import ValidationError
from django.forms import DateField
from django.forms.utils import ErrorList,ErrorDict
from django.utils.translation import gettext_lazy as _


def contains_special_caractere(word, carractere_speciaux="/:!?*+=@#$%&()[]{_<>}|~\"\\`"):
    for caractere in word:
        if caractere in carractere_speciaux:
            return True
    return False

def contains_numerique(word):
    if not word:
        return True
    carractere_speciaux = "1234567890"
    for caractere in word:
        if caractere in carractere_speciaux:
            return True
    return False

class EvaluationForm(forms.ModelForm):
    date = DateField(widget=forms.SelectDateWidget(years=range(2020, 2100), attrs={'class':'form-control'}), label="Date évaluation")
    class Meta:
        model = Evaluation
        fields = ['libelle', 'ponderation', 'date', 'rattrapage']
        widgets = {
            'libelle' : forms.TextInput(attrs={'class':'form-control'}),
            'ponderation' : forms.NumberInput(attrs={'class':'form-control'}),
            'rattrapage' : forms.CheckboxInput(attrs={'class':'form-control col-md-6'}),
        }
    
    def set_max_ponderation(self, value):
        print(value)
        self.max_ponderation = value-1
    
    def set_rattrapage(self, value):
        self.rattrapage = value
        
    def clean(self):
        cleaned_data = super(EvaluationForm, self).clean()
        ponderation = cleaned_data.get('ponderation')
        if self.rattrapage:
            cleaned_data['rattrapage'] = True
            return cleaned_data
        cleaned_data['rattrapage'] = False
        if self.instance:
            self.max_ponderation += self.instance.ponderation+1
        if ponderation > self.max_ponderation:
            self._errors['ponderation'] = "Ponderation invalide "+str(self.max_ponderation)
        return cleaned_data

class NoteForm(forms.ModelForm):
    etudiant = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'autocomplete': 'off', 'hidden' : True,}))
    etudiant_full_name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class':'form-control note_set-etudiant_full_name','autocomplete': 'off', "value": ""}), required=False)
    
    class Meta:
        model = Note
        fields = ['etudiant', 'valeurNote']
        widgets = {
            'valeurNote' : forms.NumberInput(attrs={'class':'form-control'})
        }
        
        
    def clean_etudiant(self):
        etudiant_id = self.cleaned_data.get('etudiant')
        etudiant = Etudiant.objects.get(id=etudiant_id)
        return etudiant
    
    # def clean_etudiant_full_name(self):
    #     etudiant_full_name = self.cleaned_data.get('etudiant')
    #     return etudiant_full_name



class EtudiantForm(forms.ModelForm):
    datenaissance = DateField(widget=forms.DateInput( attrs={'class': 'form-control',"type":"date"}), label="Date de naissance")
    class Meta:
        model = Etudiant
        fields = ['nom', 'prenom', 'contact', 'sexe', 'adresse', 'datenaissance', 'lieunaissance', 'profil', 'prefecture', 'is_active', 'seriebac1', 'seriebac2', 'anneebac1', 'anneebac2', 'etablissementSeconde', 'etablissementPremiere', 'etablissementTerminale', 'francaisSeconde', 'francaisPremiere','francaisTerminale', 'anglaisSeconde', 'anglaisPremiere', 'anglaisTerminale', 'mathematiqueSeconde', 'mathematiquePremiere', 'mathematiqueTerminale', 'semestres', 'photo_passport']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'sexe': forms.Select(choices=Etudiant.SEXE_CHOISE, attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'datenaissance': DateField(widget=forms.SelectDateWidget(years=range(1900, 2006)), label="Date de naissance"),
            'lieunaissance': forms.TextInput(attrs={'class': 'form-control'}),
            'prefecture': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'seriebac1': forms.Select(choices=Etudiant.CHOIX_SERIE, attrs={'class': 'form-control'}),
            'seriebac2': forms.Select(choices=Etudiant.CHOIX_SERIE, attrs={'class': 'form-control'}), 
            'anneebac1': forms.TextInput(attrs={'class': 'form-control'}),
            'anneebac2': forms.TextInput(attrs={'class': 'form-control'}),
            'etablissementSeconde': forms.TextInput(attrs={'class': 'form-control'}),
            'etablissementPremiere': forms.TextInput(attrs={'class': 'form-control'}),
            'etablissementTerminale': forms.TextInput(attrs={'class': 'form-control'}),
            'francaisSeconde': forms.TextInput(attrs={'class': 'form-control'}),
            'francaisPremiere': forms.TextInput(attrs={'class': 'form-control'}),
            'francaisTerminale': forms.TextInput(attrs={'class': 'form-control'}),
            'anglaisSeconde': forms.TextInput(attrs={'class': 'form-control'}),
            'anglaisPremiere': forms.TextInput(attrs={'class': 'form-control'}),
            'anglaisTerminale': forms.TextInput(attrs={'class': 'form-control'}),
            'mathematiqueSeconde': forms.TextInput(attrs={'class': 'form-control'}),
            'mathematiquePremiere': forms.TextInput(attrs={'class': 'form-control'}),
            'mathematiqueTerminale': forms.TextInput(attrs={'class': 'form-control'}),
            'semestres' : forms.SelectMultiple(attrs={'class': 'form-control js-select2 col-md-12'}),
        }
        

    def clean(self):
        cleaned_data = super(EtudiantForm, self).clean()
        nom = cleaned_data.get('nom')
        prenom = cleaned_data.get('prenom')
        contact = cleaned_data.get('contact')
        adresse = cleaned_data.get('adresse')
        lieunaissance = cleaned_data.get('lieunaissance')
        prefecture = cleaned_data.get('prefecture')
        etablissementSeconde = cleaned_data.get('etablissementSeconde')
        etablissementPremiere = cleaned_data.get('etablissementPremiere')
        etablissementTerminale = cleaned_data.get('etablissementTerminale')
        
        
        if contains_special_caractere(nom):
            self._errors['nom'] = 'Le nom ne doit pas contenir des caractères spéciaux'

        if contains_numerique(nom):
            self._errors['nom'] = 'Le nom ne doit pas contenir des chiffres'
        
        if contains_special_caractere(prenom):
            self._errors['prenom'] = 'Le prénom ne doit pas contenir des caractères spéciaux'

        if contains_numerique(prenom):
            self._errors['prenom'] = 'Le prénom ne doit pas contenir des chiffres'

        if contains_special_caractere(contact):
            self._errors['contact'] = 'Le contact ne doit pas contenir des caractères spéciaux'

        #if contact.isdecimal():
        #   self._errors['contact'] = 'Le contact ne doit pas contenir des lettres'
        
        carractere_speciaux = "/:!?*+=@#$%&()[]{}_<>|~\"\\`" 
        
        if adresse and contains_special_caractere(adresse):
            self._errors['adresse'] = 'L\'adresse ne doit pas contenir des caractères spéciaux'

        if lieunaissance and contains_special_caractere(lieunaissance):
            self._errors['lieunaissance'] = 'Le lieu de naissance ne doit pas contenir des caractères spéciaux'

        if prefecture and contains_special_caractere(prefecture):
            self._errors['prefecture'] = 'La préfecture ne doit pas contenir des caractères spéciaux'

        if etablissementPremiere and contains_special_caractere(etablissementPremiere):
            self._errors['etablissementSeconde'] = "Le nom de l'établissement ne doit pas contenir des caractères spéciaux"

        if etablissementSeconde and contains_special_caractere(etablissementSeconde):
            self._errors['etablissementSeconde'] = "Le nom de l'établissement ne doit pas contenir des chiffres"

        if etablissementPremiere and contains_special_caractere(etablissementPremiere):
            self._errors['etablissementPremiere'] = "Le nom de l'établissement ne doit pas contenir des caractères spéciaux"

        if etablissementPremiere and contains_numerique(etablissementPremiere):
            self._errors['etablissementPremiere'] = "Le nom de l'établissement ne doit pas contenir des chiffres"

        if etablissementTerminale and contains_special_caractere(etablissementTerminale):
            self._errors['etablissementTerminale'] = "Le nom de l'établissement ne doit pas contenir des caractères spéciaux"

        if etablissementTerminale and contains_numerique(etablissementTerminale):
            self._errors['etablissementTerminale'] = "Le nom de l'établissement ne doit pas contenir des chiffres"


class TuteurForm(forms.ModelForm):
    class Meta:
        model = Tuteur
        fields = ['nom', 'prenom', 'contact', 'sexe', 'adresse', 'profession', 'type']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control col-md-12'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control col-md-12'}),
            'contact': forms.TextInput(attrs={'class': 'form-control col-md-12'}),
            'sexe': forms.Select(choices=Tuteur.CHOIX_SEX, attrs={'class': 'form-control col-md-12'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control col-md-12'}),
            'profession': forms.TextInput(attrs={'class': 'form-control col-md-12'}),
            'type': forms.Select(choices=Tuteur.CHOIX_TYPE, attrs={'class': 'form-control col-md-12'}),
        }


class ProgrammeForm(forms.ModelForm):
    parcours = forms.ModelChoiceField(queryset=Parcours.objects.all())    
    semestre = forms.ModelChoiceField(queryset=Semestre.objects.all())    
    ue = forms.ModelChoiceField(queryset=Ue.objects.all())    
    class Meta:
        model = Programme
        fields = ['parcours', 'semestre', 'ue']
        widgets = {
            'parcours':forms.Select(),
            'semestre':forms.Select(),
            'ue': forms.Select(),
        }



class UeForm(forms.ModelForm):
    class Meta:
        model = Ue
        fields = ['libelle', 'type', 'niveau', 'nbreCredits','minValue', 'heures', 'enseignant']
        widgets = {
            'libelle': forms.TextInput(attrs={'class': 'form-control col-md-12'}),
            'type': forms.Select(attrs={'class': 'form-control col-md-12'}),       
            'niveau': forms.Select(attrs={'class': 'form-control col-md-12'}),       
            'nbreCredits': forms.TextInput(attrs={'class': 'form-control col-md-12'}),
            'minValue': forms.TextInput(attrs={'class': 'form-control col-md-12'}),
            'heures': forms.TextInput(attrs={'class': 'form-control col-md-12'}),
            'enseignant': forms.Select(attrs={'class': 'form-control col-md-12'}),       

        }
 

class MatiereForm(forms.ModelForm):

    def set_ue(self, ues):
        self.fields['ue'] = forms.ModelChoiceField(
        queryset=ues,
        widget=forms.Select(attrs={'class': 'form-control  col-md-12'}
        )
    )
        
    class Meta:
        model = Matiere
        fields = ['libelle', 'coefficient', 'minValue', 'ue', 'enseignant', 'abbreviation', 'heures']
        widgets = {
            'libelle': forms.TextInput(attrs={'class': 'form-control col-md-12'}),
            'coefficient': forms.TextInput(attrs={'class': 'form-control col-md-12'}),
            'minValue': forms.TextInput(attrs={'class': 'form-control col-md-12'}),
            'enseignant': forms.Select(attrs={'class': 'form-control col-md-12'}),  
            'abbreviation': forms.TextInput(attrs={'class': 'form-control col-md-12'}),
            'heures': forms.NumberInput(attrs={'class': 'form-control col-md-12'}),
        }


class InformationForm(forms.ModelForm):
    class Meta:
        model = Information
        fields = ('enseignant', 'numeroSecurite', 'discipline', 'niveau', 'dateDebut', 'dateFin')
        widgets = {
           # 'directeur': forms.Select(attrs={'class': 'form-control'}), 
            'enseignant': forms.Select(attrs={'class': 'form-control'}), 
            'discipline': forms.Select(attrs={'class': 'form-control'}), 
            'numeroSecurite': forms.TextInput(attrs={'class': 'form-control'}),
            'niveau': forms.Select(choices=Information.TYPE_CHOISE, attrs={'class': 'form-control'}),
          #  'duree': forms.TextInput(attrs={'class': 'form-control'}),
            'dateDebut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'dateFin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class PersonnelForm(forms.ModelForm):
    custom_errors = forms.CharField(widget=forms.TextInput(attrs={"hidden": True}), required=False)
    roles = forms.ModelMultipleChoiceField(queryset=None, widget=forms.SelectMultiple(attrs={'class': 'form-control js-select2'}))
    
    type = forms.CharField(widget=forms.Select(attrs={'class': 'form-control'}, choices=Enseignant.CHOIX_TYPE), required=False)
    specialite = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

    
    class Meta:
        model = Personnel
        fields = ['nom', 'prenom', 'contact', 'sexe', 'email', 'adresse', 'datenaissance', 'lieunaissance', 'numero_cnss', 'nif', 'profil', 'salaireBrut', 'nombre_de_personnes_en_charge', 'dernierdiplome', 'is_active','qualification_professionnel']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'sexe': forms.Select(choices=Etudiant.SEXE_CHOISE, attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'datenaissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lieunaissance': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'prefecture': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_cnss': forms.NumberInput(attrs={'class': 'form-control'}),
            'salaireBrut': forms.NumberInput(attrs={'class': 'form-control'}),
            'dernierdiplome': forms.FileInput(attrs={'class': 'form-control'}),
            'nombre_de_personnes_en_charge': forms.NumberInput(attrs={'class': 'form-control'}),
            'nif': forms.NumberInput(attrs={'class': 'form-control'}),
            'qualification_professionnel': forms.Select(attrs={'class': 'form-control'}, choices=Personnel.TYPE_CHOICES),
        }

    def clean(self):
        cleaned_data = super(PersonnelForm, self).clean()
        nom = cleaned_data.get('nom')
        prenom = cleaned_data.get('prenom')
        contact = cleaned_data.get('contact')
        email = cleaned_data.get('email')
        adresse = cleaned_data.get('adresse')
        sexe = cleaned_data.get('sexe')
        if not self.instance and chercher_utilisateur(nom, prenom):
            self._errors["custom_errors"] = "Cet utilisateur exist déjà"
        return cleaned_data


class EnseignantForm(forms.ModelForm):
    #datenaissance = DateField(widget=forms.SelectDateWidget(years=range(1990, 2006)), label='Date de naissance')
    datenaissance = DateField(widget=forms.DateInput(attrs={"type":"date"}), label='Date de naissance')

    class Meta:
        model = Enseignant
        fields = ['type', 'specialite', "personnel"]
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'specialite': forms.TextInput(attrs={'class': 'form-control'}),      
            'personnel': forms.Select(attrs={'class': 'form-control'}),
        }
    def clean(self):
        cleaned_data = super(EnseignantForm, self).clean()
        nom = cleaned_data.get('nom', '')
        prenom = cleaned_data.get('prenom', '')
        contact = cleaned_data.get('contact', '')
        email = cleaned_data.get('email', '')
        adresse = cleaned_data.get('adresse', '')
        sexe = cleaned_data.get('sexe', '')
        return cleaned_data

   
