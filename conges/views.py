from main.models import *
import os
from django import forms
from decimal import Decimal
from django.http import FileResponse, HttpResponse, HttpResponseBadRequest
from conges.forms import CongeForm, RefusCongeForm, ModifierCongeForm
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
from datetime import datetime


@login_required(login_url=settings.LOGIN_URL)
def liste_mes_conges(request, id_annee_selectionnee):
    """
    Affiche la liste des demandes de congés (validées et rejettées) d'un employé donné pour une année universitaire sélectionnée.

    Args: 

    :param id_annee_selectionnee: L'ID de l'année universitaire sélectionnée.
    request: L'objet HttpRequest pour la requête entrante.

    Returns: Un objet HttpResponse contenant le rendu HTML de la liste des demandes de congés.

    Raises: Aucune exception n'est levée.

    Cette vue récupère la liste des demandes de congés (validées et rejettées) d'un employé donné pour une année universitaire sélectionnée,
    puis les renvoie au template 'conges/liste_conges.html' pour l'affichage.

    """
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)    
    conges = Conge.objects.filter(annee_universitaire=annee_universitaire, personnel__user=request.user)   
    
    personnel = get_object_or_404(Personnel, user=request.user)  # Récupérer l'objet Personnel associé à l'utilisateur actuel
    
    date_debut_formatted_list = []
    date_fin_formatted_list = []
    for cong in conges:
        date_debut_formatted = cong.date_et_heure_debut.strftime("%d %B %Y")
        date_fin_formatted = cong.date_et_heure_fin.strftime("%d %B %Y")
        date_debut_formatted_list.append(date_debut_formatted)
        date_fin_formatted_list.append(date_fin_formatted)

    context = {
        "conges": conges,
        "annee_universitaire": annee_universitaire,
        "personnel": personnel,
    }
    return render(request, 'conges/liste_conges.html', context)



@login_required(login_url=settings.LOGIN_URL)
def formulaire_de_demande_de_conges(request, id):
    """
    Affiche en version pdf le formulaire de demande de congés de l'employé sélectionné.

    Args:
        request (HttpRequest): L'objet de requête HTTP utilisé par Django.
        id (str): L'identifiant du formulaire de demande de l'employé sélectionné.

    Returns:HttpResponse: Une réponse HTTP contenant le formulaire de demande de congés en format HTML.

    """
    conge = get_object_or_404(Conge, pk=id) 
    role = conge.personnel.getrole().capitalize()
    if conge.valider == 'Actif':
        conge.valider = "Congés accordé"
        conge.motif_refus = "none"
    elif conge.valider == 'Inactif':
        conge.valider = "Congés refusé"

    date_debut_formatted = datetime.strptime(str(conge.date_et_heure_debut), "%Y-%m-%d").strftime("%d %B %Y")
    date_fin_formatted = datetime.strptime(str(conge.date_et_heure_debut), "%Y-%m-%d").strftime("%d %B %Y")

    context = {
        "conge": conge,
        "role" : role,
        "date_debut_formatted":date_debut_formatted,
        "date_fin_formatted":date_fin_formatted,

    }
    latex_input = 'formulaire_de_demande_de_conges'
    latex_ouput = 'generated_formulaire_de_demande_de_conges'
    pdf_file = 'pdf_formulaire_de_demande_de_conges'

    # génération du pdf
    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    # visualisation du pdf dans le navigateur
    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        return response
    


@login_required(login_url=settings.LOGIN_URL)
def liste_conges(request, id_annee_selectionnee):
    """
    Affiche la liste de toutes les demandes de congés (validées et rejettées) des employés pour une année universitaire sélectionnée.

    Args: 

    :param id_annee_selectionnee: L'ID de l'année universitaire sélectionnée.
    request: L'objet HttpRequest pour la requête entrante.

    Returns: Un objet HttpResponse contenant le rendu HTML de la liste de toutes les demandes de congés.

    Raises: Aucune exception n'est levée.

    Cette vue récupère la liste de toutes les demandes de congés (validées et rejettées) des employés pour une année universitaire sélectionnée,
    puis les renvoie au template 'conges/liste_conges.html' pour l'affichage.

    """
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    conges = Conge.objects.filter(annee_universitaire = annee_universitaire)
    date_debut_formatted_list = []
    date_fin_formatted_list = []
    for cong in conges:
        date_debut_formatted = cong.date_et_heure_debut.strftime("%d %B %Y")
        date_fin_formatted = cong.date_et_heure_fin.strftime("%d %B %Y")
        date_debut_formatted_list.append(date_debut_formatted)
        date_fin_formatted_list.append(date_fin_formatted)

    context = {
        "conges": conges,
        "annee_universitaire": annee_universitaire,
        'date_debut_formatted_list': date_debut_formatted_list,
        'date_fin_formatted_list': date_fin_formatted_list,
        "date_debut_formatted":date_debut_formatted,
        "date_fin_formatted":date_fin_formatted,
    }
    return render(request, 'conges/liste_conges.html', context)



@login_required(login_url=settings.LOGIN_URL)
def creer_demande_conges(request):
    """
    Enregistre le formulaire de demande de congés dans le système.

    Args:
        request: L'objet HttpRequest qui représente la requête HTTP reçue.

    Returns:
        HttpResponse: La réponse HTTP renvoyée au client.
    'conges/demander_conges.html' : correspond au template qui est renvoyer.

    Raises:
        None

    """
    if request.method == "POST":
        form = CongeForm(request.POST)
        if form.is_valid():
            conge = form.save(commit=False)
            personnel = Personnel.objects.get(user=request.user)
            conge.personnel = personnel
            # Vérifier la durée du congé
            duree = conge.date_et_heure_fin - conge.date_et_heure_debut
            if duree.days > 30:
                messages.error(request, "La durée du congé ne peut pas dépasser 30 jours.")
                return render(request, 'conges/demander_conges.html', {'form': form})
            
            elif conge.date_et_heure_debut > conge.date_et_heure_fin :
                messages.error(request, "La date de fin doit être supérieur à la date de début.")
                return render(request, 'conges/demander_conges.html', {'form': form})
            conge.save()

            id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
            return redirect('conges:liste_mes_conges', id_annee_selectionnee=id_annee_selectionnee)
    else:
        form = CongeForm()
    return render(request, 'conges/demander_conges.html', {'form': form, })



@login_required(login_url=settings.LOGIN_URL)
def modifier_demande_conges(request, id):
    """
    Met à jour le formulaire de demande de congés dans le système.
    Si l’ID est fourni, elle met à jour les informations concernant la demande de congés existante avec les nouvelles données.
    Args:
        request: L'objet HttpRequest qui représente la requête HTTP reçue.
        id (int, optional): L'identifiant du formulaire de demande de congés à modifier (par défaut : 0).

    Returns:
        HttpResponse: La réponse HTTP renvoyée au client.
    'conges/modifier_demande_conges.html' : correspond au template qui est renvoyer.

    Raises:
        None

    """
    conge = get_object_or_404(Conge, pk=id)
    if request.method == "POST":
        form = CongeForm(request.POST, instance=conge)
        if form.is_valid():
            conge = form.save(commit=False)
            # Ne récupérez pas l'objet Personnel si l'utilisateur n'est pas membre du personnel
            if request.user.is_staff:
                conge.save()
                id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
                return redirect('conges:demandes_en_attentes', id_annee_selectionnee=id_annee_selectionnee)
            else:
                messages.error(request, "Vous n'êtes pas autorisé à modifier cette demande.")
                return render(request, 'conges/modifier_demande_conges.html', {'form': form})
    else:
        form = CongeForm(instance=conge)
    return render(request, 'conges/modifier_demande_conges.html', {'form': form})




@login_required(login_url=settings.LOGIN_URL)
def demandes_validees(request, id_annee_selectionnee):
    """
    Affiche la liste des demandes de congés validées par le responsable de l'établissement (congés actifs) pour une année universitaire sélectionnée.

    Args: 

    :param id_annee_selectionnee: L'ID de l'année universitaire sélectionnée.
    request: L'objet HttpRequest pour la requête entrante.

    Returns: Un objet HttpResponse contenant le rendu HTML de la liste des demandes validées.

    Raises: Aucune exception n'est levée.

    Cette vue récupère la liste des demandes de congés validées pour une année universitaire sélectionnée,
    puis les renvoie au template 'conges/demandes_validees.html' pour affichage.

    """
    demandes_validees = Conge.objects.filter(valider="Actif")
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    date_debut_formatted_list = []
    date_fin_formatted_list = []
    for cong in demandes_validees:
        date_debut_formatted = cong.date_et_heure_debut.strftime("%d %B %Y")
        date_fin_formatted = cong.date_et_heure_fin.strftime("%d %B %Y")
        date_debut_formatted_list.append(date_debut_formatted)
        date_fin_formatted_list.append(date_fin_formatted)
    context = {
        "demandes_validees": demandes_validees,
        "annee_universitaire": annee_universitaire,
    }
    return render(request, 'conges/demandes_validees.html', context)



@login_required(login_url=settings.LOGIN_URL)
def demandes_en_attentes(request, id_annee_selectionnee):
    """
    Affiche la liste des demandes de congés en attente pour une année universitaire sélectionnée.

    Args: 

    :param id_annee_selectionnee: L'ID de l'année universitaire sélectionnée.
    request: L'objet HttpRequest pour la requête entrante.

    Returns: Un objet HttpResponse contenant le rendu HTML de la liste des demandes en attente.

    Raises: Aucune exception n'est levée.

    Cette vue récupère la liste des demandes de congés en attente pour une année universitaire sélectionnée,
    puis les renvoie au template 'conges/demandes_en_attentes.html' pour affichage.

    """
    demandes_en_attentes = Conge.objects.filter(valider="Inconnu")
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    date_debut_formatted_list = []
    date_fin_formatted_list = []
    for cong in demandes_en_attentes:
        date_debut_formatted = cong.date_et_heure_debut.strftime("%d %B %Y")
        date_fin_formatted = cong.date_et_heure_fin.strftime("%d %B %Y")
        date_debut_formatted_list.append(date_debut_formatted)
        date_fin_formatted_list.append(date_fin_formatted)

    context = {
        "demandes_en_attentes": demandes_en_attentes,
        "annee_universitaire": annee_universitaire,
    }
    return render(request, 'conges/demandes_en_attentes.html', context)



@login_required(login_url=settings.LOGIN_URL)
def demandes_rejettees(request, id_annee_selectionnee):
    """
    Affiche la liste des demandes de congés rejettées par le responsable de l'établissement (congés inactifs) pour une année universitaire sélectionnée.

    Args: 

    :param id_annee_selectionnee: L'ID de l'année universitaire sélectionnée.
    request: L'objet HttpRequest pour la requête entrante.

    Returns: Un objet HttpResponse contenant le rendu HTML de la liste des demandes rejettées.

    Raises: Aucune exception n'est levée.

    Cette vue récupère la liste des demandes de congés rejettées pour une année universitaire sélectionnée,
    puis les renvoie au template 'conges/demandes_rejettees.html' pour affichage.

    """
    demandes_rejettees = Conge.objects.filter(valider="Inactif")
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    date_debut_formatted_list = []
    date_fin_formatted_list = []
    for cong in demandes_rejettees:
        date_debut_formatted = cong.date_et_heure_debut.strftime("%d %B %Y")
        date_fin_formatted = cong.date_et_heure_fin.strftime("%d %B %Y")
        date_debut_formatted_list.append(date_debut_formatted)
        date_fin_formatted_list.append(date_fin_formatted)

    context = {
        "demandes_rejettees": demandes_rejettees,
        "annee_universitaire": annee_universitaire,
    }
    return render(request, 'conges/demandes_rejettees.html', context)


@login_required(login_url=settings.LOGIN_URL)
def valider_conges(request, id):
    """
    Vue pour valider une demande de congé spécifique.

    Args:
        request (HttpRequest): L'objet de demande HTTP qui contient les détails de la demande.
        id (int): L'ID de la demande de congé à valider.

    Returns:
        HttpResponseRedirect: Une redirection vers la vue 'conges:demandes_en_attentes', avec l'ID de l'année universitaire sélectionnée en tant que paramètre.

    Raises:
        Http404: Si aucune demande de congé correspondant à l'ID spécifié n'est trouvée.

    """
    conge = get_object_or_404(Conge, id=id)
    conge.valider = "Actif"
    conge.save()
    id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
    return redirect('conges:demandes_en_attentes', id_annee_selectionnee=id_annee_selectionnee)



def refuser_conge(request, id):
    """
    Cette vue permet de refuser une demande de congé.

    Params:
        - request: L'objet Request contenant les données de la requête HTTP.
        - id: L'identifiant du congé à refuser.

    Returns:
        - Si la méthode de la requête est POST et le formulaire est valide, une redirection vers la liste des demandes en attente.
        - Sinon, le rendu du template 'conges/demandes_rejettees.html' avec le formulaire et l'objet congé.

    """
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
