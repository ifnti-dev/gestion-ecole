from typing import Any
from django import forms

from main.models import CorrespondanceMaquette, Domaine, Matiere, Parcours, Programme, Semestre, Ue

class GenerateMaquetteForm(forms.Form):
   # The code is defining two fields, `semestre` and `parcours`, for a form.
    semestre = forms.ModelChoiceField(
        queryset=Semestre.static_get_current_semestre(),
        widget=forms.Select(attrs={'class' : 'form-control'}),
        required=False
    )
    # parcours = forms.ModelChoiceField(
    #     queryset=Parcours.objects.all(),
    #     widget=forms.Select(attrs={'class' : 'form-control'})
    # )
    type_maquette = forms.CharField(
        widget=forms.Select(
            attrs={'class' : 'form-control'}, 
            choices=[('', 'Séléctionner'), (0, 'generique'), (1, 'spécifique')]
            )
    )
    
    def clean(self):
        cleaned_data = super(GenerateMaquetteForm, self).clean()
        # domaine = cleaned_data.get('domaine')
        parcours = cleaned_data.get('parcours')
        type_maquette = cleaned_data.get('semestre')
        
        if type_maquette == "":
            self._errors['type_maquette'] = "Type_maquette invalide"
        
        return cleaned_data

class DataForm(forms.Form):
    maquette_excel_file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}), required=False, label="Fichier maquette")
    matieres_excel_file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}), required=False, label="Fichier matières")
    notes_excel_file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}), required=False, label="Fichier notes")

class CorrespondanceMaquetteForm(forms.ModelForm):
    error = forms.CharField(max_length=255, required=False) 
    class Meta:
        model = CorrespondanceMaquette
        fields = '__all__'
    
        widgets = {
            'nature' : forms.Select(attrs={'class':'form-control'}),
            'ancienne' : forms.TextInput(attrs={'hidden': True}),
            'nouvelle' : forms.TextInput(attrs={'hidden': True}),
        }
    
    def clean(self):
        cleaned_data = super(CorrespondanceMaquetteForm, self).clean()
        nature = cleaned_data.get('nature')
        ancienne = cleaned_data.get('ancienne')
        nouvelle = cleaned_data.get('nouvelle')
        model = None
        if nature == "" and nature == ancienne == nouvelle:
            self._errors['errors'] = "Veuillez remplire le formulaire."
            
        if nature.lower() == "u" :
            model = Ue
        elif nature.lower() == "m" :
            model = Matiere
        else:
            self._errors['error'] = "Veuillez selectionner la nature de la correspondance."
        return cleaned_data


class ProgrammeForm(forms.ModelForm):
    semestre = forms.ModelChoiceField(
        queryset=Semestre.static_get_current_semestre(),
        widget=forms.Select(attrs={'class' : 'form-control'}),
    )
    parcours = forms.ModelChoiceField(
        queryset=Parcours.objects.all(),
        widget=forms.Select(attrs={'class' : 'form-control'})
    )
    ues = forms.ModelMultipleChoiceField(
        queryset=Ue.objects.all(),
        widget=forms.SelectMultiple(attrs={'class' : 'form-control js-select2 form-control w-100'})
    )
    
    class Meta:
        model = Programme
        fields = ('semestre', 'ues','parcours')
    
    def clean(self):
        cleanned_data = super(ProgrammeForm, self).clean()   
        return cleanned_data


ProgrammeFormSet = forms.modelformset_factory(Programme, form=ProgrammeForm, extra=0)

class DomaineForm(forms.ModelForm):
    class Meta:
        model = Domaine
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super(DomaineForm, self).clean()   
        return cleaned_data

class ParcoursForm(forms.ModelForm):
    class Meta:
        model = Parcours
        exclude = ('domaine',)
    
    def clean(self):
        cleaned_data = super(ParcoursForm, self).clean()   
        return cleaned_data
