from typing import Any, Dict
import re
from typing import Any, Dict
from django import forms
from django.db.models import Sum  
from main.models import  Paiement, FicheDePaie
from .models import  Utilisateur, Personnel, Enseignant, AnneeUniversitaire, Conge
from django.core.exceptions import ValidationError
from django.forms import DateField
from django.forms.utils import ErrorList,ErrorDict
from django.forms.utils import ErrorList,ErrorDict
from django.utils.translation import gettext_lazy as _


class CongeForm(forms.ModelForm):
    class Meta:
        model = Conge
        fields = ['nature', 'autre_nature', 'date_et_heure_debut', 'date_et_heure_fin']
        widgets = {
            'nature': forms.Select(attrs={'class': 'form-control'}),
            'autre_nature': forms.TextInput(attrs={'class': 'form-control'}), 
            'date_et_heure_debut': forms.DateTimeInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_et_heure_fin': forms.DateTimeInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class RefusCongeForm(forms.Form):
    motif_refus = forms.CharField(widget=forms.Textarea)


class ModifierCongeForm(forms.ModelForm):
    class Meta:
        model = Conge
        fields = ['nature', 'autre_nature', 'date_et_heure_debut', 'date_et_heure_fin']
        widgets = {
            'nature': forms.Select(attrs={'class': 'form-control'}),
            'autre_nature': forms.TextInput(attrs={'class': 'form-control'}), 
            'date_et_heure_debut': forms.DateTimeInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_et_heure_fin': forms.DateTimeInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
