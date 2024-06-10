from typing import Any, Dict
import re
from typing import Any, Dict
from django import forms
from django.db.models import Sum  
from main.models import Paiement, FicheDePaie
from .models import Evaluation, Note, Utilisateur, Frais, CompteEtudiant, CompteBancaire, Personnel, Enseignant, Etudiant, Matiere, AnneeUniversitaire, Ue, Tuteur, Semestre, VersmentSalaire, Fournisseur, Charge
from django.core.exceptions import ValidationError
from django.forms import DateField
from django.forms.utils import ErrorList,ErrorDict
from django.forms.utils import ErrorList,ErrorDict
from django.utils.translation import gettext_lazy as _



class PersonnelForm(forms.ModelForm):
    datenaissance = DateField(widget=forms.SelectDateWidget(years=range(1990, 2006)), label='Date de naissance')
    class Meta:
        model = Personnel
        fields = ['nom', 'prenom', 'contact', 'sexe', 'email', 'adresse', 'datenaissance', 'lieunaissance', 'numero_cnss', 'nif', 'profil', 'salaireBrut', 'nombre_de_personnes_en_charge', 'profil', 'dernierdiplome', 'is_active']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'sexe': forms.Select(choices=Etudiant.SEXE_CHOISE, attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'datenaissance': DateField(widget=forms.SelectDateWidget(years=range(1900, 2006)), label="Date de naissance"),
            'lieunaissance': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_cnss': forms.TextInput(attrs={'class': 'form-control'}),
            'nif': forms.TextInput(attrs={'class': 'form-control'}),
            'profil': forms.FileInput(attrs={'class': 'form-control'}),
            'salaireBrut': forms.NumberInput(attrs={'class': 'form-control'}),
            'nombre_de_personnes_en_charge': forms.NumberInput(attrs={'class': 'form-control'}), 
            'dernierdiplome': forms.FileInput(attrs={'class': 'form-control'}),
            'profil': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-control'}),
        }


class FraisForm(forms.ModelForm):
    class Meta:
        model = Frais
        fields = ['montant_inscription', 'montant_scolarite' ]
        widgets = {
            #'annee_universitaire': forms.Select(attrs={'class': 'form-control'}),       
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
    montant=forms.IntegerField(initial=None,widget=forms.NumberInput(attrs={'class': 'form-control','placeholder':1,"min":1},))
  
    class Meta:
        model = Paiement
        fields = ['type', 'montant', 'dateversement','etudiant' ,'numerobordereau']
        
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'dateversement': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'etudiant':forms.Select(attrs={'class': 'form-control js-select2 col-md-12'}),
            'numerobordereau': forms.TextInput(attrs={'class': 'form-control'}),
            
        }

    def clean(self):
        cleaned_data = super().clean()
        etudiant = cleaned_data.get('etudiant')
        montant = cleaned_data.get('montant')
        annee_universitaire = cleaned_data.get('annee_universitaire')
        
        if etudiant and annee_universitaire :
            total_versements = Paiement.objects.filter(etudiant=etudiant, annee_universitaire=annee_universitaire).aggregate(Sum('montant'))['montant__sum'] or 0
            frais = Frais.objects.filter(annee_universitaire=annee_universitaire).first()
            print("ok")
            if frais:
                total_frais = frais.montant_inscription + frais.montant_scolarite
                # modifier la validation
                print("montant etu",montant)
                print("montant_total",total_versements)
                
                if  montant < frais.montant_scolarite :
                    if montant and (montant + total_versements >=total_frais) :
                        raise forms.ValidationError(f"L'étudiant a déjà versé une somme de : {total_versements} FCFA .Il lui reste {total_frais-total_versements} FCFA")
                else:
                    raise forms.ValidationError(f"Le Montant du frais de scolarité ne doit pas depassé {frais.montant_scolarite}")

            else:
                raise forms.ValidationError("Les frais ne sont pas définis pour l'année universitaire sélectionnée.")

            return cleaned_data

        



    
     
class VersmentSalaireForm(forms.ModelForm):
    class Meta:
        model = VersmentSalaire
        fields = ['date_debut','date_fin', 'personnel', 'prime_efficacite', 'prime_qualite', 'frais_travaux_complementaires', 'prime_anciennete', 'prime_forfaitaire', 'acomptes']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'personnel': forms.Select(attrs={'class': 'form-control'}),
            'prime_efficacite': forms.NumberInput(attrs={'class': 'form-control'}),
            'prime_qualite': forms.NumberInput(attrs={'class': 'form-control'}),
            'frais_travaux_complementaires': forms.NumberInput(attrs={'class': 'form-control'}),
            'prime_anciennete': forms.NumberInput(attrs={'class': 'form-control'}),
            'acomptes': forms.NumberInput(attrs={'class': 'form-control'}),
            'prime_forfaitaire': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class StagiairesForm(forms.ModelForm):
    class Meta:
        model = VersmentSalaire
        fields = ['date_debut','date_fin', 'personnel', 'prime_efficacite', 'prime_qualite', 'frais_travaux_complementaires', 'prime_anciennete', 'prime_forfaitaire', 'acomptes']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'personnel': forms.Select(attrs={'class': 'form-control'}),
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
        fields = ['type', 'montant', 'dateversement', 'le_mois','facture_pdf']      
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'dateversement': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'le_mois': forms.Select(attrs={'class': 'form-control'}),
            'facture_pdf': forms.FileInput(attrs={'class': 'form-control'}),
        }


class FicheDePaieForm(forms.ModelForm):
    matieres_L1 = forms.ModelMultipleChoiceField(
        queryset=Matiere.objects.filter(ue__programme__semestre__libelle__in=['S1', 'S2']),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label="Matière L1",
        required=False
    )
    matieres_L2 = forms.ModelMultipleChoiceField(
        queryset=Matiere.objects.filter(ue__programme__semestre__libelle__in=['S3', 'S4']),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label="Matière L2",
        required=False
    )
    matieres_L3 = forms.ModelMultipleChoiceField(
        queryset=Matiere.objects.filter(ue__programme__semestre__libelle__in=['S5', 'S6']),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label="Matière L3",
        required=False
    )

    class Meta:
        model = FicheDePaie
        fields = ['dateDebut', 'dateFin', 'enseignant', 'prixUnitaire', 'acomptes', 'nombreHeureL1', 'nombreHeureL2', 'nombreHeureL3']
        widgets = {
            'dateDebut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'dateFin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'enseignant': forms.Select(attrs={'class': 'form-control'}),
            'nombreHeureL1': forms.NumberInput(attrs={'class': 'form-control'}),
            'nombreHeureL2': forms.NumberInput(attrs={'class': 'form-control'}),
            'nombreHeureL3': forms.NumberInput(attrs={'class': 'form-control'}),
            'prixUnitaire': forms.NumberInput(attrs={'class': 'form-control'}),
            'acomptes': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['matieres_L1'].queryset = Matiere.objects.filter(ue__programme__semestre__libelle__in=['S1', 'S2'])
        self.fields['matieres_L2'].queryset = Matiere.objects.filter(ue__programme__semestre__libelle__in=['S3', 'S4'])
        self.fields['matieres_L3'].queryset = Matiere.objects.filter(ue__programme__semestre__libelle__in=['S5', 'S6'])

    def clean(self):
        cleaned_data = super().clean()
        nombreHeureL1 = cleaned_data.get('nombreHeureL1')
        nombreHeureL2 = cleaned_data.get('nombreHeureL2')
        nombreHeureL3 = cleaned_data.get('nombreHeureL3')

        # Vérifier si au moins un champ de nombre d'heures est renseigné
        if nombreHeureL1 is None and nombreHeureL2 is None and nombreHeureL3 is None:
            raise forms.ValidationError("Au moins un champ 'Nombre d'heures' doit être renseigné.")
        return cleaned_data



class ChargeForm(forms.ModelForm):
    class Meta:
        model = Charge
        fields = ['dateDebut', 'dateFin',  'personnel', 'frais_de_vie', 'frais_nourriture', 'frais_de_vie_dcc', 'frais_nourriture_dcc']   
        widgets = {
            'dateDebut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'dateFin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'personnel': forms.Select(attrs={'class': 'form-control'}),
            'frais_de_vie': forms.NumberInput(attrs={'class': 'form-control'}),
            'frais_nourriture': forms.NumberInput(attrs={'class': 'form-control'}),
            'frais_de_vie_dcc': forms.NumberInput(attrs={'class': 'form-control'}),
            'frais_nourriture_dcc': forms.NumberInput(attrs={'class': 'form-control'}),
        }


