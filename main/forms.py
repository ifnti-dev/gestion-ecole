from typing import Any, Dict
import re
from typing import Any, Dict
from django import forms
from .models import Evaluation, Information, Programme, Parcours, Note, Utilisateur, Personnel, Enseignant, Etudiant, Matiere, AnneeUniversitaire, Ue, Tuteur, Semestre
from django.core.exceptions import ValidationError
from django.forms import DateField
from django.forms.utils import ErrorList,ErrorDict
from django.utils.translation import gettext_lazy as _


def contains_special_caractere(word):
    if not word:
        return True
    carractere_speciaux = ";/.,:!?*+=@#$%&()[]{}_<>|~\"\'\\`" 
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
            'ponderation' : forms.TextInput(attrs={'class':'form-control'}),
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
    etudiant = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'autocomplete': 'off', 'hidden' : True}))
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
    datenaissance = DateField(widget=forms.SelectDateWidget(years=range(1900, 2006), attrs={'class': 'form-control'}), label="Date de naissance")
    class Meta:
        model = Etudiant
        fields = ['nom', 'prenom', 'contact', 'sexe', 'adresse', 'datenaissance', 'lieunaissance', 'prefecture', 'is_active', 'seriebac1', 'seriebac2', 'anneebac1', 'anneebac2', 'etablissementSeconde', 'etablissementPremiere', 'etablissementTerminale', 'francaisSeconde', 'francaisPremiere','francaisTerminale', 'anglaisSeconde', 'anglaisPremiere', 'anglaisTerminale', 'mathematiqueSeconde', 'mathematiquePremiere', 'mathematiqueTerminale', 'tuteurs']
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

        if contains_special_caractere(adresse):
            self._errors['adresse'] = 'L\'adresse ne doit pas contenir des caractères spéciaux'

        if contains_special_caractere(lieunaissance):
            self._errors['lieunaissance'] = 'Le lieu de naissance ne doit pas contenir des caractères spéciaux'

        if contains_special_caractere(prefecture):
            self._errors['prefecture'] = 'La préfecture ne doit pas contenir des caractères spéciaux'

        if contains_special_caractere(etablissementPremiere):
            self._errors['etablissementSeconde'] = "Le nom de l'établissement ne doit pas contenir des caractères spéciaux"

        if contains_special_caractere(etablissementSeconde):
            self._errors['etablissementSeconde'] = "Le nom de l'établissement ne doit pas contenir des chiffres"

        if contains_special_caractere(etablissementPremiere):
            self._errors['etablissementPremiere'] = "Le nom de l'établissement ne doit pas contenir des caractères spéciaux"

        if contains_numerique(etablissementPremiere):
            self._errors['etablissementPremiere'] = "Le nom de l'établissement ne doit pas contenir des chiffres"

        if contains_special_caractere(etablissementTerminale):
            self._errors['etablissementTerminale'] = "Le nom de l'établissement ne doit pas contenir des caractères spéciaux"

        if contains_numerique(etablissementTerminale):
            self._errors['etablissementTerminale'] = "Le nom de l'établissement ne doit pas contenir des chiffres"


class TuteurForm(forms.ModelForm):
    class Meta:
        model = Tuteur
        fields = ['nom', 'prenom', 'contact', 'sexe', 'adresse', 'profession', 'type']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
            'contact': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
            'sexe': forms.Select(choices=Tuteur.CHOIX_SEX, attrs={'class': 'form-control col-md-6'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
            'profession': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
            'type': forms.Select(choices=Tuteur.CHOIX_TYPE, attrs={'class': 'form-control col-md-6'}),
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
        fields = ['libelle', 'type', 'niveau', 'nbreCredits', 'heures', 'enseignant']
        widgets = {
            'libelle': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
            'type': forms.Select(attrs={'class': 'form-control col-md-6'}),       
            'niveau': forms.Select(attrs={'class': 'form-control col-md-6'}),       
            'nbreCredits': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
            'heures': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
            'enseignant': forms.Select(attrs={'class': 'form-control col-md-6'}),       

        }
 

class MatiereForm(forms.ModelForm):
    ue = forms.ModelChoiceField(queryset=Ue.objects.all())    
    class Meta:
        model = Matiere
        fields = ['libelle', 'coefficient', 'minValue', 'ue', 'enseignant']
        widgets = {
            'libelle': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
            'coefficient': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
            'minValue': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
            'ue': forms.Select(),      
            'enseignant': forms.Select(attrs={'class': 'form-control col-md-6'}),       
        }


class EnseignantForm(forms.ModelForm):
    datenaissance = DateField(widget=forms.SelectDateWidget(years=range(1990, 2006)), label='Date de naissance')
    class Meta:
        model = Enseignant
        fields = ['nom', 'prenom', 'contact', 'sexe', 'email', 'adresse', 'datenaissance', 'lieunaissance', 'prefecture', 'photo_passport', 'salaireBrut', 'dernierdiplome', 'is_active', 'type', 'specialite']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'sexe': forms.Select(choices=Etudiant.SEXE_CHOISE, attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'datenaissance': DateField(widget=forms.SelectDateWidget(years=range(1900, 2006)), label="Date de naissance"),
            'lieunaissance': forms.TextInput(attrs={'class': 'form-control'}),
            'prefecture': forms.TextInput(attrs={'class': 'form-control'}),
            'photo_passport': forms.FileInput(attrs={'class': 'form-control'}),
            'salaireBrut': forms.NumberInput(attrs={'class': 'form-control'}),
            'dernierdiplome': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'specialite': forms.TextInput(attrs={'class': 'form-control'})      

        }

    def clean(self):
        cleaned_data = super(EnseignantForm, self).clean()
        nom = cleaned_data.get('nom')
        prenom = cleaned_data.get('prenom')
        contact = cleaned_data.get('contact')
        email = cleaned_data.get('email')
        adresse = cleaned_data.get('adresse')
        lieunaissance = cleaned_data.get('lieunaissance')
        sexe = cleaned_data.get('sexe')
        prefecture = cleaned_data.get('prefecture')

        if nom.find(';') != -1 or nom.find('/') != -1 or nom.find('.') != -1 or nom.find(',') != -1 or nom.find(':') != -1 or nom.find('!') != -1 or nom.find('?') != -1 or nom.find('*') != -1 or nom.find('+') != -1 or nom.find('=') != -1 or nom.find('@') != -1 or nom.find('#') != -1 or nom.find('$') != -1 or nom.find('%') != -1 or nom.find('&') != -1 or nom.find('(') != -1 or nom.find(')') != -1 or nom.find('_') != -1 or nom.find('<') != -1 or nom.find('>') != -1 or nom.find('|') != -1 or nom.find('~') != -1 or nom.find('^') != -1 or nom.find('{') != -1 or nom.find('}') != -1 or nom.find('[') != -1 or nom.find(']') != -1 or nom.find('"') != -1 or nom.find('\\') != -1 or nom.find('`') != -1:
            #forms.nom.errors = "Le nom ne doit pas contenir des caractères spéciaux"
            #print(self._errors)
            if not 'nom' in self._errors:
                self._errors['nom'] = ErrorDict()
            self._errors['nom'] = 'Le nom ne doit pas contenir des caractères spéciaux'


        if nom.find('0') != -1 or nom.find('1') != -1 or nom.find('2') != -1 or nom.find('3') != -1 or nom.find('4') != -1 or nom.find('5') != -1 or nom.find('6') != -1 or nom.find('7') != -1 or nom.find('8') != -1 or nom.find('9') != -1:
            if not 'nom' in self._errors:
                self._errors['nom'] = ErrorDict()
            self._errors['nom'] = 'Le nom ne doit pas contenir des chiffres'
        
        if prenom.find(';') != -1 or prenom.find('/') != -1 or prenom.find('.') != -1 or prenom.find(',') != -1 or prenom.find(':') != -1 or prenom.find('!') != -1 or prenom.find('?') != -1 or prenom.find('*') != -1 or prenom.find('+') != -1 or prenom.find('=') != -1 or prenom.find('@') != -1 or prenom.find('#') != -1 or prenom.find('$') != -1 or prenom.find('%') != -1 or prenom.find('&') != -1 or prenom.find('(') != -1 or prenom.find(')') != -1 or prenom.find('_') != -1 or prenom.find('<') != -1 or prenom.find('>') != -1 or prenom.find('|') != -1 or prenom.find('~') != -1 or prenom.find('^') != -1 or prenom.find('{') != -1 or prenom.find('}') != -1 or prenom.find('[') != -1 or prenom.find(']') != -1 or prenom.find('"') != -1 or prenom.find('\\') != -1 or prenom.find('`') != -1:
            if not 'prenom' in self._errors:
                self._errors['prenom'] = ErrorDict()
            self._errors['prenom'] = 'Le prénom ne doit pas contenir des caractères spéciaux'

        if prenom.find('0') != -1 or prenom.find('1') != -1 or prenom.find('2') != -1 or prenom.find('3') != -1 or prenom.find('4') != -1 or prenom.find('5') != -1 or prenom.find('6') != -1 or prenom.find('7') != -1 or prenom.find('8') != -1 or prenom.find('9') != -1:
            if not 'prenom' in self._errors:
                self._errors['prenom'] = ErrorDict()
            self._errors['prenom'] = 'Le prénom ne doit pas contenir des chiffres'

        if contact.find(';') != -1 or contact.find('/') != -1 or contact.find('.') != -1 or contact.find(',') != -1 or contact.find(':') != -1 or contact.find('!') != -1 or contact.find('?') != -1 or contact.find('*') != -1 or contact.find('`') != -1 or contact.find('=') != -1 or contact.find('@') != -1 or contact.find('#') != -1 or contact.find('$') != -1 or contact.find('%') != -1 or contact.find('&') != -1 or contact.find('(') != -1 or contact.find(')') != -1 or contact.find('_') != -1 or contact.find('<') != -1 or contact.find('>') != -1 or contact.find('|') != -1 or contact.find('~') != -1 or contact.find('^') != -1 or contact.find('{') != -1 or contact.find('}') != -1 or contact.find('[') != -1 or contact.find(']') != -1 or contact.find('"') != -1 or contact.find('\\') != -1 or contact.find(' ') != -1 or contact.find("'") != -1 :
            if not 'contact' in self._errors:
                self._errors['contact'] = ErrorDict()
            self._errors['contact'] = 'Le contact ne doit pas contenir des caractères spéciaux'

        if contact.find('a') != -1 or contact.find('b') != -1 or contact.find('c') != -1 or contact.find('d') != -1 or contact.find('e') != -1 or contact.find('f') != -1 or contact.find('g') != -1 or contact.find('h') != -1 or contact.find('i') != -1 or contact.find('j') != -1 or contact.find('k') != -1 or contact.find('l') != -1 or contact.find('m') != -1 or contact.find('n') != -1 or contact.find('o') != -1 or contact.find('p') != -1 or contact.find('q') != -1 or contact.find('r') != -1 or contact.find('s') != -1 or contact.find('t') != -1 or contact.find('u') != -1 or contact.find('v') != -1 or contact.find('w') != -1 or contact.find('x') != -1 or contact.find('y') != -1 or contact.find('z') != -1:
            if not 'contact' in self._errors:
                self._errors['contact'] = ErrorDict()
            self._errors['contact'] = 'Le contact ne doit pas contenir des lettres'

        if email.find(';') != -1 or email.find('/') != -1 or email.find(',') != -1 or email.find(':') != -1 or email.find('!') != -1 or email.find('?') != -1 or email.find('*') != -1 or email.find('+') != -1 or email.find('=') != -1 or email.find('#') != -1 or email.find('$') != -1 or email.find('%') != -1 or email.find('&') != -1 or email.find('(') != -1 or email.find(')') != -1 or email.find('_') != -1 or email.find('<') != -1 or email.find('>') != -1 or email.find('|') != -1 or email.find('~') != -1 or email.find('^') != -1 or email.find('{') != -1 or email.find('}') != -1 or email.find('[') != -1 or email.find(']') != -1 or email.find('"') != -1 or email.find('\\') != -1 or email.find(' ') != -1 or email.find("'") != -1 :
            if not 'email' in self._errors:
                self._errors['email'] = ErrorDict()
            self._errors['email'] = 'L\'email ne doit pas contenir des caractères spéciaux'

        if adresse.find(';') != -1 or adresse.find('/') != -1 or adresse.find(',') != -1 or adresse.find(':') != -1 or adresse.find('!') != -1 or adresse.find('?') != -1 or adresse.find('*') != -1 or adresse.find('+') != -1 or adresse.find('=') != -1 or adresse.find('#') != -1 or adresse.find('$') != -1 or adresse.find('%') != -1 or adresse.find('&') != -1 or adresse.find('(') != -1 or adresse.find(')') != -1 or adresse.find('_') != -1 or adresse.find('<') != -1 or adresse.find('>') != -1 or adresse.find('|') != -1 or adresse.find('~') != -1 or adresse.find('^') != -1 or adresse.find('{') != -1 or adresse.find('}') != -1 or adresse.find('[') != -1 or adresse.find(']') != -1 or adresse.find('"') != -1 or adresse.find('\\') != -1 or adresse.find("'") != -1 or adresse.find('@') != -1 :
            if not 'adresse' in self._errors:
                self._errors['adresse'] = ErrorDict()
            self._errors['adresse'] = 'L\'adresse ne doit pas contenir des caractères spéciaux'

        if lieunaissance.find(';') != -1 or lieunaissance.find('/') != -1 or lieunaissance.find(',') != -1 or lieunaissance.find(':') != -1 or lieunaissance.find('!') != -1 or lieunaissance.find('?') != -1 or lieunaissance.find('*') != -1 or lieunaissance.find('+') != -1 or lieunaissance.find('=') != -1 or lieunaissance.find('#') != -1 or lieunaissance.find('$') != -1 or lieunaissance.find('%') != -1 or lieunaissance.find('&') != -1 or lieunaissance.find('(') != -1 or lieunaissance.find(')') != -1 or lieunaissance.find('_') != -1 or lieunaissance.find('<') != -1 or lieunaissance.find('>') != -1 or lieunaissance.find('|') != -1 or lieunaissance.find('~') != -1 or lieunaissance.find('^') != -1 or lieunaissance.find('{') != -1 or lieunaissance.find('}') != -1 or lieunaissance.find('[') != -1 or lieunaissance.find(']') != -1 or lieunaissance.find('"') != -1 or lieunaissance.find('\\') != -1 or lieunaissance.find("'") != -1 or lieunaissance.find('@') != -1 :
            if not 'lieunaissance' in self._errors:
                self._errors['lieunaissance'] = ErrorDict()
            self._errors['lieunaissance'] = 'Le lieu de naissance ne doit pas contenir des caractères spéciaux'

        if sexe.find(';') != -1 or sexe.find('/') != -1 or sexe.find(',') != -1 or sexe.find(':') != -1 or sexe.find('!') != -1 or sexe.find('?') != -1 or sexe.find('*') != -1 or sexe.find('+') != -1 or sexe.find('=') != -1 or sexe.find('#') != -1 or sexe.find('$') != -1 or sexe.find('%') != -1 or sexe.find('&') != -1 or sexe.find('(') != -1 or sexe.find(')') != -1 or sexe.find('_') != -1 or sexe.find('<') != -1 or sexe.find('>') != -1 or sexe.find('|') != -1 or sexe.find('~') != -1 or sexe.find('^') != -1 or sexe.find('{') != -1 or sexe.find('}') != -1 or sexe.find('[') != -1 or sexe.find(']') != -1 or sexe.find('"') != -1 or sexe.find('\\') != -1 or sexe.find("'") != -1 or sexe.find('@') != -1 :
            if not 'sexe' in self._errors:
                self._errors['sexe'] = ErrorDict()
            self._errors['sexe'] = 'Le sexe ne doit pas contenir des caractères spéciaux'

        if sexe.find('0') != -1 or sexe.find('1') != -1 or sexe.find('2') != -1 or sexe.find('3') != -1 or sexe.find('4') != -1 or sexe.find('5') != -1 or sexe.find('6') != -1 or sexe.find('7') != -1 or sexe.find('8') != -1 or sexe.find('9') != -1 :
            if not 'sexe' in self._errors:
                self._errors['sexe'] = ErrorDict()
            self._errors['sexe'] = 'Le sexe ne doit pas contenir des chiffres'

        if prefecture.find(';') != -1 or prefecture.find('/') != -1 or prefecture.find(',') != -1 or prefecture.find(':') != -1 or prefecture.find('!') != -1 or prefecture.find('?') != -1 or prefecture.find('*') != -1 or prefecture.find('+') != -1 or prefecture.find('=') != -1 or prefecture.find('#') != -1 or prefecture.find('$') != -1 or prefecture.find('%') != -1 or prefecture.find('&') != -1 or prefecture.find('(') != -1 or prefecture.find(')') != -1 or prefecture.find('_') != -1 or prefecture.find('<') != -1 or prefecture.find('>') != -1 or prefecture.find('|') != -1 or prefecture.find('~') != -1 or prefecture.find('^') != -1 or prefecture.find('{') != -1 or prefecture.find('}') != -1 or prefecture.find('[') != -1 or prefecture.find(']') != -1 or prefecture.find('"') != -1 or prefecture.find('\\') != -1 or prefecture.find("'") != -1 or prefecture.find('@') != -1 :
            if not 'prefecture' in self._errors:
                self._errors['prefecture'] = ErrorDict()
            self._errors['prefecture'] = 'La préfecture ne doit pas contenir des caractères spéciaux'

        


    
class InformationForm(forms.ModelForm):
    class Meta:
        model = Information
        fields = ('enseignant', 'numeroSecurite', 'discipline', 'niveau', 'dateDebut', 'dateFin', 'duree')
        widgets = {
           # 'directeur': forms.Select(attrs={'class': 'form-control'}), 
            'enseignant': forms.Select(attrs={'class': 'form-control'}), 
            'discipline': forms.Select(attrs={'class': 'form-control'}), 
            'numeroSecurite': forms.TextInput(attrs={'class': 'form-control'}),
            'niveau': forms.Select(choices=Information.TYPE_CHOISE, attrs={'class': 'form-control'}),
            'duree': forms.TextInput(attrs={'class': 'form-control'}),
            'dateDebut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'dateFin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


         
        
        
        

        

        

        

