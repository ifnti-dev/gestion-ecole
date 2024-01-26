from typing import Any, Dict
import re
from typing import Any, Dict
from django import forms
from django.db.models import Sum  
from main.models import Comptable, Paiement, FicheDePaie
from .models import Evaluation, Note, Utilisateur, Frais, CompteEtudiant, CompteBancaire, Personnel, Enseignant, Etudiant, Matiere, AnneeUniversitaire, Ue, Tuteur, Semestre, Salaire, Fournisseur, Charge
from django.core.exceptions import ValidationError
from django.forms import DateField
from django.forms.utils import ErrorList,ErrorDict
from django.forms.utils import ErrorList,ErrorDict
from django.utils.translation import gettext_lazy as _




class FraisForm(forms.ModelForm):
    class Meta:
        model = Frais
        fields = ['annee_universitaire', 'montant_inscription', 'montant_scolarite' ]
        widgets = {
            'annee_universitaire': forms.Select(attrs={'class': 'form-control'}),       
            'montant_inscription': forms.NumberInput(attrs={'class': 'form-control'}),
            'montant_scolarite': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class CompteBancaireForm(forms.ModelForm):
    class Meta:
        model = CompteBancaire
        fields = ['numero', 'frais_tenue_de_compte' ]
        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'form-control'}),       
            'frais_tenue_de_compte': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['type','etudiant', 'montant', 'dateversement', 'numerobordereau', 'annee_universitaire']
        
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'dateversement': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'etudiant': forms.Select(attrs={'class': 'form-control'}),
            'numerobordereau': forms.TextInput(attrs={'class': 'form-control'}),
            'annee_universitaire': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        etudiant = cleaned_data.get('etudiant')
        montant = cleaned_data.get('montant')
        annee_universitaire = cleaned_data.get('annee_universitaire')

        if etudiant and annee_universitaire:
            total_versements = Paiement.objects.filter(etudiant=etudiant, annee_universitaire=annee_universitaire).aggregate(Sum('montant'))['montant__sum'] or 0
            frais = Frais.objects.filter(annee_universitaire=annee_universitaire).first()

            if frais:
                total_frais = frais.montant_inscription + frais.montant_scolarite

                if montant and montant + total_versements > total_frais:
                    raise forms.ValidationError("L'étudiant a déjà versé le montant total des frais. Aucun versement supplémentaire n'est autorisé.")
            else:
                raise forms.ValidationError("Les frais ne sont pas définis pour l'année universitaire sélectionnée.")

        return cleaned_data

        


class ComptableForm(forms.ModelForm):
    datenaissance = DateField(widget=forms.SelectDateWidget(years=range(1990, 2006)), label='Date de naissance')
    class Meta:
        model = Comptable
        fields = ['nom', 'prenom', 'contact', 'sexe', 'email', 'adresse', 'datenaissance', 'lieunaissance', 'photo_passport', 'salaireBrut', 'nombre_de_personnes_en_charge', 'dernierdiplome', 'is_active']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'sexe': forms.Select(choices=Etudiant.SEXE_CHOISE, attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'datenaissance': DateField(widget=forms.SelectDateWidget(years=range(1900, 2006)), label="Date de naissance"),
            'lieunaissance': forms.TextInput(attrs={'class': 'form-control'}),
            'photo_passport': forms.FileInput(attrs={'class': 'form-control'}),
            'salaireBrut': forms.NumberInput(attrs={'class': 'form-control'}),
            'nombre_de_personnes_en_charge': forms.NumberInput(attrs={'class': 'form-control'}),
            'dernierdiplome': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super(ComptableForm, self).clean()
        nom = cleaned_data.get('nom')
        prenom = cleaned_data.get('prenom')
        contact = cleaned_data.get('contact')
        email = cleaned_data.get('email')
        adresse = cleaned_data.get('adresse')
        lieunaissance = cleaned_data.get('lieunaissance')
        sexe = cleaned_data.get('sexe')

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

     
class SalaireForm(forms.ModelForm):
    class Meta:
        model = Salaire
        fields = ['date_debut','date_fin', 'personnel', 'numero_cnss', 'qualification_professionnel', 'tcs', 'prime_efficacite', 'prime_qualite', 'frais_travaux_complementaires', 'prime_anciennete', 'prime_forfaitaire', 'acomptes']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'personnel': forms.Select(attrs={'class': 'form-control'}),
            'numero_cnss': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification_professionnel': forms.Select(attrs={'class': 'form-control'}),
            'tcs': forms.NumberInput(attrs={'class': 'form-control'}),
            'prime_efficacite': forms.NumberInput(attrs={'class': 'form-control'}),
            'prime_qualite': forms.NumberInput(attrs={'class': 'form-control'}),
            'frais_travaux_complementaires': forms.NumberInput(attrs={'class': 'form-control'}),
            'prime_anciennete': forms.NumberInput(attrs={'class': 'form-control'}),
            'acomptes': forms.NumberInput(attrs={'class': 'form-control'}),
            'prime_forfaitaire': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    

class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['type', 'montant', 'dateversement', 'le_mois']      
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'dateversement': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'le_mois': forms.Select(attrs={'class': 'form-control'}),
        }



class FicheDePaieForm(forms.ModelForm):
    class Meta:
        model = FicheDePaie
        matiere = forms.ModelMultipleChoiceField(
                queryset=Matiere.objects.all(),
                widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
                label="Matière L1",
                required=False
            ),
        fields = ['dateDebut', 'dateFin',  'enseignant', 'prixUnitaire', 'acomptes', 'matiere', 'nombreHeureL1', 'nombreHeureL2', 'nombreHeureL3']   
        widgets = {
            'dateDebut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'dateFin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'enseignant': forms.Select(attrs={'class': 'form-control'}),
            'nombreHeureL1': forms.NumberInput(attrs={'class': 'form-control'}),
            'nombreHeureL2': forms.NumberInput(attrs={'class': 'form-control'}),
            'nombreHeureL3': forms.NumberInput(attrs={'class': 'form-control'}),
            'prixUnitaire': forms.NumberInput(attrs={'class': 'form-control'}),
            'acomptes': forms.NumberInput(attrs={'class': 'form-control'}),
#            'matiere' : forms.SelectMultiple(attrs={'class': 'form-control'}),
            
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['matiere'].queryset = self.get_matiere_choices()

    def get_matiere_choices(self):
        # Filtrer les matières de L1 (Semestre1 et Semestre2)
        return Matiere.objects.filter(ue__programme__semestre__libelle__in=['S1', 'S2'])

        

class ChargeForm(forms.ModelForm):
    class Meta:
        model = Charge
        fields = ['dateDebut', 'dateFin',  'personnel', 'frais_de_vie', 'frais_nourriture']   
        widgets = {
            'dateDebut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'dateFin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'personnel': forms.Select(attrs={'class': 'form-control'}),
            'frais_de_vie': forms.NumberInput(attrs={'class': 'form-control'}),
            'frais_nourriture': forms.NumberInput(attrs={'class': 'form-control'}),
        }

     
