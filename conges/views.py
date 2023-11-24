from main.models import *
import os
from django import forms
from decimal import Decimal
from django.http import FileResponse, HttpResponse, HttpResponseBadRequest
from conges.forms import CongeForm
from django.db.models import Sum
import datetime
from main.pdfMaker import generate_pdf
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .forms import RefusCongeForm

@login_required(login_url=settings.LOGIN_URL)
def liste_mes_conges(request, id_annee_selectionnee):
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)    
    conges = Conge.objects.filter(annee_universitaire=annee_universitaire, personnel__user=request.user)
    
    context = {
        "conges": conges,
        "annee_universitaire": annee_universitaire,
    }
    return render(request, 'conges/liste_conges.html', context)


@login_required(login_url=settings.LOGIN_URL)
def liste_conges(request, id_annee_selectionnee):
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    conges = Conge.objects.filter(annee_universitaire = annee_universitaire)
    context = {
        "conges": conges,
        "annee_universitaire": annee_universitaire,
    }
    return render(request, 'conges/liste_conges.html', context)


@login_required(login_url=settings.LOGIN_URL)
def demander_conges(request, id=0):
    if request.method == "GET":
        if id == 0:
            form = CongeForm()
        else:
            conge = Conge.objects.get(pk=id)
            form = CongeForm(instance=conge)   
        return render(request, 'conges/demander_conges.html', {'form': form})
    else:
        if id == 0:
            form = CongeForm(request.POST)
        else:
            conge = Conge.objects.get(pk=id)
            form = CongeForm(request.POST, instance=conge)
        
        if form.is_valid():
            conge = form.save(commit=False)
            personnel = Personnel.objects.get(user=request.user)
            conge.personnel = personnel

            # Vérifier la durée du congé
            duree = conge.date_et_heure_fin - conge.date_et_heure_debut
            if duree.days > 30:
                messages.error(request, "La durée du congé ne peut pas dépasser 30 jours.")
                return render(request, 'conges/demander_conges.html', {'form': form})

            conge.save()

            id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
            return redirect('conges:liste_mes_conges', id_annee_selectionnee=id_annee_selectionnee)
        else:
            print(form.errors)
            return render(request, 'conges/demander_conges.html', {'form': form})



@login_required(login_url=settings.LOGIN_URL)
def demandes_validees(request, id_annee_selectionnee):
    demandes_validees = Conge.objects.filter(valider="Actif")
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    context = {
        "demandes_validees": demandes_validees,
        "annee_universitaire": annee_universitaire,
    }
    return render(request, 'conges/demandes_validees.html', context)



@login_required(login_url=settings.LOGIN_URL)
def demandes_en_attentes(request, id_annee_selectionnee):
    demandes_en_attentes = Conge.objects.filter(valider="Inconnu")
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    context = {
        "demandes_en_attentes": demandes_en_attentes,
        "annee_universitaire": annee_universitaire,
    }
    return render(request, 'conges/demandes_en_attentes.html', context)



@login_required(login_url=settings.LOGIN_URL)
def demandes_rejettees(request, id_annee_selectionnee):
    demandes_rejettees = Conge.objects.filter(valider="Inactif")
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    context = {
        "demandes_rejettees": demandes_rejettees,
        "annee_universitaire": annee_universitaire,
    }
    return render(request, 'conges/demandes_rejettees.html', context)


@login_required(login_url=settings.LOGIN_URL)
def valider_conges(request, id):
    conge = get_object_or_404(Conge, id=id)
    conge.valider = "Actif"
    conge.save()
    id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
    return redirect('conges:demandes_en_attentes', id_annee_selectionnee=id_annee_selectionnee)



def refuser_conge(request, id):
    conge = get_object_or_404(Conge, id=id)

    if request.method == 'POST':
        form = RefusCongeForm(request.POST)
        if form.is_valid():
            motif_refus = form.cleaned_data['motif_refus']

            conge.valider = 'Inactif'
            conge.motif_refus = motif_refus
            conge.save()

            id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
            return redirect('conges:demandes_en_attentes', id_annee_selectionnee=id_annee_selectionnee)

    else:
        form = RefusCongeForm()

    return render(request, 'conges/demandes_rejettees.html', {'form': form, 'conge': conge})
