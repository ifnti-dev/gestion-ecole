from main.models import *
import os
from django import forms
from decimal import Decimal
from django.http import FileResponse, HttpResponse
from paiement.forms import ComptableForm, FicheDePaieForm, PaiementForm, FournisseurForm, FraisForm, CompteBancaireForm, SalaireForm, ChargeForm
from django.db.models import Sum
from num2words import num2words
import datetime
from main.pdfMaker import generate_pdf
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_DOWN
from datetime import datetime
import locale

# Définir la locale en français
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

@login_required(login_url=settings.LOGIN_URL)
def liste_frais(request, id_annee_selectionnee):
    """
    Affiche la liste des frais pour une année universitaire donnée.

    :param request: L'objet HttpRequest utilisé pour effectuer la requête.
    :param id_annee_selectionnee: L'ID de l'année universitaire sélectionnée.
    :return: Un objet HttpResponse contenant le rendu de la page 'frais/liste_frais.html'.
    :raises: Http404 si l'année universitaire sélectionnée n'est pas trouvée.

    Cette vue récupère les frais associés à l'année universitaire spécifiée,
    puis les renvoie au template 'frais/liste_frais.html' pour affichage.
    """
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    current_annee = AnneeUniversitaire.static_get_current_annee_universitaire()
    frais = Frais.objects.filter(annee_universitaire = annee_universitaire)
    context = {
        "frais": frais,
        "annee_universitaire": annee_universitaire,
    }
    return render(request, 'frais/liste_frais.html', context)


@login_required(login_url=settings.LOGIN_URL)
def enregistrer_frais(request, id=0):
    """
    Cette vue permet d'enregistrer ou de modifier le montant des frais de scolarité.
    Si l'ID est fourni, elle met à jour le montant des frais existant avec les nouvelles données.
    Sinon, elle crée une nouvelle instance de frais scolaire.

    Args:
        request (HttpRequest): L'objet HttpRequest reçu.
        id (int, optional): L'identifiant du frais à mettre à jour. Par défaut 0.

    Returns:
        HttpResponse: La réponse HTTP rendue par la vue.
    'frais/enregistrer_frais.html' : correspond au template qui est renvoyer.

    Raises:
        None
    """
    if request.method == "GET":
        if id == 0:
            form = FraisForm()
        else:
            frais = Frais.objects.get(pk=id)
            form = FraisForm(instance=frais)   
        return render(request, 'frais/enregistrer_frais.html', {'form': form})
    else:
        if id == 0:
            form = FraisForm(request.POST)
        else:
            frais = Frais.objects.get(pk=id)
            form = FraisForm(request.POST,instance = frais)
        if form.is_valid():
            form.save()
            id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
            return redirect('paiement:liste_frais', id_annee_selectionnee=id_annee_selectionnee)
        else:
            print(form.errors)
            return render(request, 'frais/enregistrer_frais.html', {'form': form})


@login_required(login_url=settings.LOGIN_URL)
def create_comptable(request, id=0):
    """
    Cette vue permet d'enregistrer ou de modifier un comptable.
    Si l'ID est fourni, elle met à jour les informations du comptable existante avec les nouvelles données.
    Sinon, elle crée une nouvelle instance de comptable.

    Args:
        request (HttpRequest): L'objet HttpRequest reçu.
        id (int, optional): L'identifiant du comptable à mettre à jour. Par défaut 0.

    Returns:
        HttpResponse: La réponse HTTP rendue par la vue.
    'comptables/create_comptable.html' : correspond au template qui est renvoyer.

    Raises:
        None
    """
    if request.method == "GET":
        if id == 0:
            form = ComptableForm()
        else:
            comptable = Comptable.objects.get(pk=id)
            form = ComptableForm(instance=comptable)   
        return render(request, 'comptables/create_comptable.html', {'form': form})
    else:
        if id == 0:
            form = ComptableForm(request.POST)
        else:
            comptable = Comptable.objects.get(pk=id)
            form = ComptableForm(request.POST,instance= comptable)
        if form.is_valid():
            form.save()
            return redirect('paiement:comptable_list')
        else:
            print(form.errors)
            return render(request, 'comptables/create_comptable.html', {'form': form})


@login_required(login_url=settings.LOGIN_URL)
def comptable_detail(request, id):
    """
    Affiche les informations détaillées d'un comptable donnée.

    :param request: L'objet HttpRequest utilisé pour effectuer la requête.
    :param id : L'ID du comptable sélectionné.
    :return: Un objet HttpResponse contenant le rendu de la page 'comptables/comptable_detail.html'.

    Cette vue récupère les informations détaillées d'un comptable spécifique,
    puis les renvoie au template 'comptables/comptable_detail.html' pour affichage.
    """
    comptable = get_object_or_404(Comptable, id=id)
    return render(request, 'comptables/comptable_detail.html', {'comptable': comptable})


@login_required(login_url=settings.LOGIN_URL)
def comptable_list(request):
    """
    Affiche la liste des comptables actifs.

    Args: request: L'objet HttpRequest pour la requête entrante.
    Returns: Un objet HttpResponse contenant le rendu HTML de la liste des comptables actifs.
    Raises: Aucune exception n'est levée.

    Cette vue récupèrela liste des comptables actifs,
    puis les renvoie au template 'comptables/comptable_list.html' pour affichage.

    """
    current_annee = AnneeUniversitaire.static_get_current_annee_universitaire()
    comptables = Comptable.objects.filter(is_active=True)
    context = {
        "comptables": comptables,
    }
    return render(request, 'comptables/comptable_list.html', context)


@login_required(login_url=settings.LOGIN_URL)
def comptables_suspendu(request):
    """
    Affiche la liste des comptables inactifs.

    Args: request: L'objet HttpRequest pour la requête entrante.
    Returns: Un objet HttpResponse contenant le rendu HTML de la liste des comptables inactifs.
    Raises: Aucune exception n'est levée.

    Cette vue récupèrela liste des comptables inactifs,
    puis les renvoie au template 'comptables/comptable_list.html' pour affichage.

    """
    annee_universitaire_courante = AnneeUniversitaire.static_get_current_annee_universitaire()
    comptables = Comptable.objects.filter(is_active=False)
    context = {
        "comptables": comptables,
        "annee_universitaire_courante": annee_universitaire_courante,
    }
    return render(request, 'comptables/comptable_list.html', context)


@login_required(login_url=settings.LOGIN_URL)
def liste_paiements(request, id_annee_selectionnee):
    """
    Affiche la liste des versements de frais de scolarité pour une année universitaire donnée.

    :param request: L'objet HttpRequest utilisé pour effectuer la requête.
    :param id_annee_selectionnee: L'ID de l'année universitaire sélectionnée.
    :return: Un objet HttpResponse contenant le rendu de la page 'paiements/liste_paiements.html'.
    :raises: Http404 si l'année universitaire sélectionnée n'est pas trouvée.

    Cette vue récupère les versements de frais de scolarité  associés à l'année universitaire spécifiée,
    puis les renvoie au template 'paiements/liste_paiements.html' pour affichage.
    """
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    paiements = Paiement.objects.filter(annee_universitaire=annee_universitaire)
    context = {
        'annee_universitaire': annee_universitaire,
        'paiements': paiements,
    }
    return render(request, 'paiements/liste_paiements.html', context)


@login_required(login_url=settings.LOGIN_URL)
def enregistrer_paiement(request, id=0):
    """
    Cette vue permet d'enregistrer ou de mettre à jour les informations concernant le paiement des frais scolaires.
    Si l'ID est fourni, elle met à jour les informations concernant le paiement existant avec les nouvelles données.
    Sinon, elle crée une nouvelle instance pour stocker les informations concernant le paiement.

    Args:
        request (HttpRequest): L'objet HttpRequest reçu.
        id (int, optional): L'identifiant du paiement à mettre à jour. Par défaut 0.

    Returns:
        HttpResponse: La réponse HTTP rendue par la vue.
    'paiements/enregistrer_paiement.html' : correspond au template qui est renvoyer.

    Raises:
        None
    """
    if request.method == "GET":
        if id == 0:
            form = PaiementForm()
        else:
            paiement = Paiement.objects.get(pk=id)
            form = PaiementForm(instance=paiement)   
        return render(request, 'paiements/enregistrer_paiement.html', {'form': form}) 
    else:
        if id == 0:
            form = PaiementForm(request.POST)
        else:
            paiement = Paiement.objects.get(pk=id)
            compte_universite = paiement.compte_bancaire
            compte_universite.solde_bancaire -= paiement.montant
            compte_universite.save()
            form = PaiementForm(request.POST,instance= paiement)
        if form.is_valid():
            paiement = form.save(commit=False)
            comptable = Comptable.objects.get(user=request.user)
            paiement.comptable = comptable

            compte_universite = CompteBancaire.objects.first()
            paiement.compte_bancaire = compte_universite
            paiement.save()

            etudiant = paiement.etudiant
            annee_universitaire = paiement.annee_universitaire
            compte_etudiant, created = CompteEtudiant.objects.get_or_create(
                etudiant=etudiant,
                annee_universitaire=annee_universitaire
            )
            compte_etudiant.solde += paiement.montant
            compte_etudiant.save()

            compte_universite.solde_bancaire += paiement.montant
            compte_universite.save()

            id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
            return redirect('paiement:liste_paiements', id_annee_selectionnee=id_annee_selectionnee)                                          
        else:
            return render(request, 'paiements/enregistrer_paiement.html', {'form': form})



def etat_paiements(request, id_annee_selectionnee, id):
    """
        Affiche les informations concernant l'état de paiement d'un étudiant donnée pour une année universitaire sélectionnée.

        Paramètres :
            request – L’objet HttpRequest utilisé pour effectuer la requête.
            id_annee_selectionnee – est l'identifiant de l’année universitaire sélectionnée et  
            id - correspond à l'identifiant de l'étudiant sélectionné.

        Renvoie :
        Un objet HttpResponse contenant le rendu de la page 'paiements/etat_paiements.html'.

        Raises :
            Http404 si l’année universitaire sélectionnée n’est pas trouvée.

        Cette vue récupère les informations concernant l'état de paiement actuel d'un étudiant associés à l’année universitaire spécifiée, puis les renvoie au template 'paiements/etat_paiements.html' pour affichage.
    
    """
    etudiant = get_object_or_404(Etudiant, pk=id)
    annee_selectionnee = AnneeUniversitaire.objects.get(pk=id_annee_selectionnee)
    paiements = Paiement.objects.filter(annee_universitaire=id_annee_selectionnee, etudiant=etudiant)
    frais_etudiant = Frais.objects.filter(annee_universitaire=id_annee_selectionnee).first()
    montant_du = 0
    somme_restante = 0
    montant_total = 0 
    arrierees = 0

    if frais_etudiant is None:
        context = {
            'id_annee_selectionnee': id_annee_selectionnee,
            'etudiant': etudiant,
            'message_alerte': "Les frais ne sont pas définis pour cette année universitaire.",
        }
        return render(request, 'paiements/etat_paiements.html', context)

    """
        Calcul du montant total pour l'étudiant 
    """
    montant_verse = paiements.filter(etudiant=etudiant).aggregate(Sum('montant'))['montant__sum'] or 0
    total_frais_courante = frais_etudiant.montant_inscription + frais_etudiant.montant_scolarite if frais_etudiant else 0
    
    """
        alcul des arriérés pour l'étudiant
    """
    annees_etudiant = etudiant.semestres.values_list('annee_universitaire', flat=True).distinct()
    if len(annees_etudiant) > 1:
        frais_annees_etudiant = Frais.objects.filter(annee_universitaire__in=annees_etudiant)
        for frais_annee_etudiant in frais_annees_etudiant:
            montant_du += frais_annee_etudiant.montant_inscription + frais_annee_etudiant.montant_scolarite
        arrierees = montant_du - total_frais_courante
        montant_total = arrierees + total_frais_courante
        somme_restante = montant_total - montant_verse
    else :
        arrierees = 0
        montant_total = total_frais_courante
        montant_verse = paiements.filter(etudiant=etudiant).aggregate(Sum('montant'))['montant__sum'] or 0
        somme_restante = montant_total - montant_verse

    context = {
        'id_annee_selectionnee': id_annee_selectionnee,
        'etudiant': etudiant,
        'montant_verse': montant_verse,
        'somme_restante': somme_restante,
        'arrierees': arrierees,
        'frais_etudiant': frais_etudiant,
        'total_frais_courante': total_frais_courante,
        'montant_total' : montant_total,
        'paiements': paiements,
    }

    return render(request, 'paiements/etat_paiements.html', context)



@login_required(login_url=settings.LOGIN_URL)
def create_compte(request, id=0):
    """
    Vue pour créer ou mettre à jour un compte bancaire.

    Args:
        request (HttpRequest): L'objet HttpRequest représentant la requête HTTP reçue.
        id (int, optional): L'identifiant du compte bancaire à mettre à jour, par défaut 0.

    Returns:
        HttpResponse: L'objet HttpResponse représentant la réponse HTTP retournée.
    'compte_bancaire/create_compte.html' : correspond au template qui est renvoyer.
    Raises:
        N/A

    """
    if request.method == "GET":
        if id == 0:
            form = CompteBancaireForm()
        else:
            compte = CompteBancaire.objects.get(pk=id)
            form = CompteBancaireForm(instance=compte)   
        return render(request, 'compte_bancaire/create_compte.html', {'form': form})
    else:
        if id == 0:
            form = CompteBancaireForm(request.POST)
        else:
            compte = CompteBancaire.objects.get(pk=id)
            form = CompteBancaireForm(request.POST,instance= compte)
        if form.is_valid():
            form.save()
            id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
            return redirect('paiement:compte_bancaire', id_annee_selectionnee=id_annee_selectionnee)
        else:
            print(form.errors)
            return render(request, 'compte_bancaire/create_compte.html', {'form': form})



@login_required(login_url=settings.LOGIN_URL)
def compte_bancaire(request, id_annee_selectionnee):
    """
    Affiche les informations du compte bancaire pour une année universitaire donnée.

    :param request: L'objet HttpRequest utilisé pour effectuer la requête.
    :param id_annee_selectionnee: L'ID de l'année universitaire sélectionnée.
    :return: Un objet HttpResponse contenant le rendu de la page 'compte_bancaire/compte_bancaire.html'.
    :raises: Http404 si l'année universitaire sélectionnée n'est pas trouvée.

    Cette vue récupère les frais associés à l'année universitaire spécifiée,
    puis les renvoie au template 'compte_bancaire/compte_bancaire.html' pour affichage.
    """
    semestres_annee = Semestre.objects.filter(annee_universitaire=id_annee_selectionnee)
    etudiants_annee = Etudiant.objects.filter(semestres__in=semestres_annee)
    paiements_annee = Paiement.objects.filter(etudiant__in=etudiants_annee)
    montant_total_paiements = paiements_annee.aggregate(Sum('montant'))['montant__sum'] or 0

    salaires = Salaire.objects.filter(annee_universitaire=id_annee_selectionnee)
    total_salaire_brut = sum(salaire.personnel.salaireBrut + salaire.prime_efficacite + salaire.prime_qualite + salaire.frais_travaux_complementaires+ salaire.prime_anciennete for salaire in salaires)
    total_cnss = sum(salaire.frais_prestations_familiale_salsalaire * salaire.personnel.salaireBrut + salaire.frais_prestations_familiales * salaire.personnel.salaireBrut + salaire.frais_risques_professionnel * salaire.personnel.salaireBrut + salaire.frais_pension_vieillesse_emsalaire * salaire.personnel.salaireBrut for salaire in salaires)
    total_irpp = sum(salaire.irpp + salaire.tcs for salaire in salaires)
    total_salaire_net = sum(salaire.salaire_net_a_payer for salaire in salaires)
    montant_total_salaires = sum(salaire.salaire_net_a_payer + (salaire.frais_prestations_familiale_salsalaire * salaire.personnel.salaireBrut + salaire.frais_prestations_familiales * salaire.personnel.salaireBrut + salaire.frais_risques_professionnel * salaire.personnel.salaireBrut + salaire.frais_pension_vieillesse_emsalaire * salaire.personnel.salaireBrut + salaire.tcs)for salaire in salaires)

    fournisseurs = Fournisseur.objects.filter(annee_universitaire=id_annee_selectionnee)
    total_paiements_fournisseurs = sum(fournisseur.montant for fournisseur in fournisseurs)

    fiche_de_paies = FicheDePaie.objects.filter(annee_universitaire=id_annee_selectionnee)
    total_fiche_de_paies = sum(fiche_de_paie.montant for fiche_de_paie in fiche_de_paies)

    fiche_de_charge = Charge.objects.filter(annee_universitaire=id_annee_selectionnee)
    total_charges = sum(fiche.montant for fiche in fiche_de_charge)

    total_salaires = (total_charges + total_fiche_de_paies) + montant_total_salaires

    compte_bancaire_obj = CompteBancaire.objects.first()
    compte_existe = compte_bancaire_obj is not None

    context = {
        'id_annee_selectionnee': id_annee_selectionnee,
        'total_paiements': montant_total_paiements,
        'montant_total_salaires': montant_total_salaires,
        'compte_bancaire_obj': compte_bancaire_obj,
        'total_salaire_brut': total_salaire_brut,
        'total_cnss': total_cnss,
        'total_irpp': total_irpp,
        'total_salaire_net': total_salaire_net,
        'total_paiements_fournisseurs': total_paiements_fournisseurs,
        'total_fiche_de_paies': total_fiche_de_paies,
        'total_charges': total_charges,
        'total_salaires': total_salaires,
        'compte_existe': compte_existe,
    }
    return render(request, 'compte_bancaire/compte_bancaire.html', context)


@login_required(login_url=settings.LOGIN_URL)
def etat_compte_bancaire(request, id_annee_selectionnee, compte_bancaire_id):
    """
        Affiche les informations concernant l'état du compte bancaire de l'institut pour une année universitaire sélectionnée.

        Paramètres :
            request – L’objet HttpRequest utilisé pour effectuer la requête.
            id_annee_selectionnee – est l'identifiant de l’année universitaire sélectionnée et  
            compte_bancaire_id - correspond à l'identifiant du compte bancaire sélectionné.

        Renvoie :
        Un objet HttpResponse contenant le rendu de la page 'compte_bancaire/etat_compte_bancaire.html'.

        Raises :
            Http404 si l’année universitaire sélectionnée n’est pas trouvée.

        Cette vue récupère les informations le compte bancaire associés à l’année universitaire spécifiée, puis les renvoie au template 'compte_bancaire/etat_compte_bancaire.html' pour affichage.
    
    """
    compte_bancaire = CompteBancaire.objects.get(id=compte_bancaire_id)
    semestres_annee = Semestre.objects.filter(annee_universitaire=id_annee_selectionnee)
    etudiants_annee = Etudiant.objects.filter(semestres__in=semestres_annee)
    paiements_frais_scolaires = Paiement.objects.filter(compte_bancaire=compte_bancaire, etudiant__in=etudiants_annee)
    
    salaires = Salaire.objects.filter(annee_universitaire=id_annee_selectionnee)
    montant_total_paiements = paiements_frais_scolaires.aggregate(Sum('montant'))['montant__sum'] or 0
    fournisseurs = Fournisseur.objects.filter(annee_universitaire=id_annee_selectionnee)
    fiches_de_paies = FicheDePaie.objects.filter(annee_universitaire=id_annee_selectionnee)
    fiche_charges = Charge.objects.filter(annee_universitaire=id_annee_selectionnee)

    context = {
        'id_annee_selectionnee': id_annee_selectionnee,
        'total_paiements': paiements_frais_scolaires,
        'total_salaires': salaires,
        'compte_bancaire': montant_total_paiements,
        'total_fournisseurs' : fournisseurs,
        'total_fiches_de_paies': fiches_de_paies,
        'total_fiche_charges': fiche_charges,
    }
    return render(request, 'compte_bancaire/etat_compte_bancaire.html', context)


def liste_etudiants(request, id_annee_selectionnee):
    """
        Affiche la liste des étudiants avec le montant totale à payer, le montant restant à payer pour l'année universitaire courante ainsi que les arriérés des années dernières.

        Paramètres :
            request – L’objet HttpRequest utilisé pour effectuer la requête.
            id_annee_selectionnee – L’ID de l’année universitaire sélectionnée.

        Renvoie :
        Un objet HttpResponse contenant le rendu de la page 'liste_etudiants.html'.

        Raises :
            Http404 si l’année universitaire sélectionnée n’est pas trouvée.

        Cette vue récupère la liste des étudiants associés à l’année universitaire spécifiée, puis les renvoie au template 'liste_etudiants.html' pour affichage.
    
    """
    # Récupérer les étudiants pour l'année universitaire sélectionnée
    etudiants_annee = Etudiant.objects.filter(semestres__annee_universitaire=id_annee_selectionnee).distinct()

    # Récupérer l'objet AnneeUniversitaire correspondant à l'id fourni
    annee_selectionnee = AnneeUniversitaire.objects.get(pk=id_annee_selectionnee)

    # Récupérer les paiements pour l'année universitaire sélectionnée
    paiements = Paiement.objects.filter(annee_universitaire=id_annee_selectionnee)

    # Récupérer les frais pour l'année universitaire sélectionnée
    frais_etudiant = Frais.objects.filter(annee_universitaire=id_annee_selectionnee).first()

    # Initialiser une liste pour stocker les étudiants avec leur montant total et restant
    etudiants_avec_montant_total = []

    # Initialiser une variable pour stocker le total des frais de scolarité courante
    total_frais_courante = 0

    for etudiant in etudiants_annee:
        montant_du = 0
        somme_restante = 0
        arrierees = 0

        # Calculer le montant total payé par l'étudiant
        montant_total = paiements.filter(etudiant=etudiant).aggregate(Sum('montant'))['montant__sum'] or 0

        # Calculer le total des frais de scolarité courante
        total_frais_courante = frais_etudiant.montant_inscription + frais_etudiant.montant_scolarite if frais_etudiant else 0

        # Calculer le montant restant à payer
        somme_restante = total_frais_courante - montant_total

        """
            Vérifier si l'étudiant est lié à une seule année universitaire
            Si oui, pas d'arriérés
        """
        if len(etudiant.semestres.values_list('annee_universitaire', flat=True).distinct()) == 1:
            arrierees = 0
        else:
            """
                Calculer le montant total dû pour toutes les années universitaires
            """
            frais_annees_etudiant = Frais.objects.filter(annee_universitaire__in=etudiant.semestres.values_list('annee_universitaire', flat=True).distinct())
            for frais_annee_etudiant in frais_annees_etudiant:
                montant_du += frais_annee_etudiant.montant_inscription + frais_annee_etudiant.montant_scolarite

            """
                Calculer le montant restant à payer et les arriérés
            """
            montant_total = paiements.filter(etudiant=etudiant).aggregate(Sum('montant'))['montant__sum'] or 0
            somme_restante = montant_du - montant_total
            arrierees = montant_du - total_frais_courante
        """
            Ajouter l'étudiant avec les montants calculés à la liste
        """
        etudiants_avec_montant_total.append({
            'etudiant': etudiant,
            'montant_total': montant_total,
            'somme_restante': somme_restante,
            'arrierees': arrierees,
        })

    """
        Créer un contexte contenant les données nécessaires pour le template
    """
    context = {
        'id_annee_selectionnee': id_annee_selectionnee,
        'etudiants_avec_montant_total': etudiants_avec_montant_total,
        'total_frais_courante': total_frais_courante,
    }

    """ 
        Rendre le template avec le contexte 
    """
    return render(request, 'liste_etudiants.html', context)


#Méthode affichant le bilan annuel des paiements des frais scolaires
@login_required(login_url=settings.LOGIN_URL)
def bilan_paiements_annuel(request, id_annee_selectionnee):
    """
    Affiche en version pdf le bilan annuel des paiements effectués par les étudiants pour une année universitaire donnée.

    Args:
        request (HttpRequest): L'objet de requête HTTP utilisé par Django.
        id_annee_selectionnee (int): L'identifiant de l'année universitaire sélectionnée.

    Returns:HttpResponse: Une réponse HTTP contenant le bilan des paiements en format HTML.
    Raises:AnneeUniversitaire.DoesNotExist: Si l'année universitaire avec l'ID donné n'existe pas.

    """
    etudiants_annee = Etudiant.objects.filter(semestres__annee_universitaire=id_annee_selectionnee).distinct()
    annee_selectionnee = AnneeUniversitaire.objects.get(pk=id_annee_selectionnee)
    paiements = Paiement.objects.filter(annee_universitaire=id_annee_selectionnee)
    frais_etudiant = Frais.objects.filter(annee_universitaire=id_annee_selectionnee).first()
    etudiants_avec_montant_total = []
    total_frais_courante = 0

    for etudiant in etudiants_annee:
        montant_du = 0
        somme_restante = 0
        arrierees = 0
        montant_total = paiements.filter(etudiant=etudiant).aggregate(Sum('montant'))['montant__sum'] or 0
        total_frais_courante = frais_etudiant.montant_inscription + frais_etudiant.montant_scolarite if frais_etudiant else 0
        somme_restante = total_frais_courante - montant_total
        annees_etudiant = etudiant.semestres.values_list('annee_universitaire', flat=True).distinct()

        # Vérifiez si l'étudiant est lié à une seule année universitaire
        if len(annees_etudiant) == 1:
            arrierees = 0

        else:
            frais_annees_etudiant = Frais.objects.filter(annee_universitaire__in=annees_etudiant)
            for frais_annee_etudiant in frais_annees_etudiant:
                montant_du += frais_annee_etudiant.montant_inscription + frais_annee_etudiant.montant_scolarite
       
            montant_total = paiements.filter(etudiant=etudiant).aggregate(Sum('montant'))['montant__sum'] or 0
            somme_restante = montant_du - montant_total
            arrierees = montant_du - total_frais_courante

        etudiants_avec_montant_total.append({
            'etudiant': etudiant,
            'montant_total': montant_total,
            'somme_restante': somme_restante,
            'arrierees': arrierees,
        })

    context = {
        'id_annee_selectionnee': id_annee_selectionnee,
        'etudiants_avec_montant_total': etudiants_avec_montant_total,
        'montant_du': montant_du,
        'frais_etudiant': frais_etudiant,
        'arrierees': arrierees,
        'total_frais_courante': total_frais_courante, 
    }

    latex_input = 'bilan_paiements_annuel'
    latex_ouput = 'generated_bilan_paiements_annuel'
    pdf_file = 'pdf_bilan_paiements_annuel'

    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    # visualisation du pdf dans le navigateur
    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        return response


@login_required(login_url=settings.LOGIN_URL)
def les_bulletins_de_paye(request, id_annee_selectionnee):
    """
    Affiche la liste des bulletins de paie pour une année universitaire donnée.

    :param request: L'objet HttpRequest utilisé pour effectuer la requête.
    :param id_annee_selectionnee: L'ID de l'année universitaire sélectionnée.
    :return: Un objet HttpResponse contenant le rendu de la page 'salaires/bulletins_de_paye.html'.
    :raises: Http404 si l'année universitaire sélectionnée n'est pas trouvée.

    Cette vue récupère les bulletins de paie associés à l'année universitaire spécifiée,
    puis les renvoie au template 'salaires/bulletins_de_paye.html' pour affichage.
    """
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    bulletins = Salaire.objects.filter(annee_universitaire=annee_universitaire)
    context = {
        'annee_universitaire': annee_universitaire,
        'bulletins': bulletins,
    }
    #return HttpResponse('')
    return render(request, 'salaires/bulletins_de_paye.html', context)



@login_required(login_url=settings.LOGIN_URL)
def enregistrer_bulletin(request, id=0):    
    """
    Enregistre ou met à jour le bulletin de paie dans le système.
    Si l’ID est fourni, elle met à jour les informations concernant le bulletin de paie existant avec les nouvelles données. Sinon, elle crée une nouvelle instance de bulletin de paie.

    Args:
        request: L'objet HttpRequest qui représente la requête HTTP reçue.
        id (int, optional): L'identifiant du bulletin de paie à modifier (par défaut : 0).

    Returns:
        HttpResponse: La réponse HTTP renvoyée au client.
    'salaires/enregistrer_bulletin.html' : correspond au template qui est renvoyer.

    Raises:
        None

    """
    if request.method == "GET":
        if id == 0:
            form = SalaireForm()
        else:
            bulletin = Salaire.objects.get(pk=id)
            form = SalaireForm(instance=bulletin)   
        return render(request, 'salaires/enregistrer_bulletin.html', {'form': form})
    else:
        if id == 0:
            form = SalaireForm(request.POST)
        else:
            bulletin = Salaire.objects.get(pk=id)
            compte_universite = bulletin.compte_bancaire
            compte_universite.solde_bancaire += bulletin.salaire_net_a_payer + bulletin.tcs + (Decimal(bulletin.frais_prestations_familiale_salsalaire) * Decimal(bulletin.personnel.salaireBrut) + Decimal(bulletin.frais_prestations_familiales) * Decimal(bulletin.personnel.salaireBrut) + Decimal(bulletin.frais_risques_professionnel) * Decimal(bulletin.personnel.salaireBrut) + Decimal(bulletin.frais_pension_vieillesse_emsalaire) * Decimal(bulletin.personnel.salaireBrut))
            print(bulletin.salaire_net_a_payer + bulletin.tcs + (Decimal(bulletin.frais_prestations_familiale_salsalaire) * Decimal(bulletin.personnel.salaireBrut) + Decimal(bulletin.frais_prestations_familiales) * Decimal(bulletin.personnel.salaireBrut) + Decimal(bulletin.frais_risques_professionnel) * Decimal(bulletin.personnel.salaireBrut) + Decimal(bulletin.frais_pension_vieillesse_emsalaire) * Decimal(bulletin.personnel.salaireBrut)))
            compte_universite.save()
            form = SalaireForm(request.POST, instance=bulletin)
        if form.is_valid():
            bulletin = form.save(commit=False)
            date_debut = bulletin.date_debut
            date_fin = bulletin.date_fin
            if date_debut and date_fin and date_debut > date_fin:
                form.add_error('date_fin', "La date de fin ne peut pas être antérieure à la date de début.")
                return render(request, 'salaires/enregistrer_bulletin.html', {'form': form})

            compte_universite = CompteBancaire.objects.first()
            if compte_universite is not None:
                bulletin.compte_bancaire = compte_universite
                bulletin.save()
                taxes_cnss = Decimal(bulletin.frais_prestations_familiale_salsalaire) * Decimal(bulletin.personnel.salaireBrut) + Decimal(bulletin.frais_prestations_familiales) * Decimal(bulletin.personnel.salaireBrut) + Decimal(bulletin.frais_risques_professionnel) * Decimal(bulletin.personnel.salaireBrut) + Decimal(bulletin.frais_pension_vieillesse_emsalaire) * Decimal(bulletin.personnel.salaireBrut) 
                deductions = taxes_cnss + bulletin.tcs
                montant_a_prelever = bulletin.salaire_net_a_payer + deductions 
                compte_universite.solde_bancaire -= montant_a_prelever
                compte_universite.save()
                
                id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
                return redirect('paiement:bulletins_de_paye', id_annee_selectionnee=id_annee_selectionnee)
            else :
                return render(request, 'etudiants/message_erreur.html', {'message': "Le compte bancaire n\'existe pas."})
        else:
            print(form.errors)
            return render(request, 'salaires/enregistrer_bulletin.html', {'form': form})


def delete_bulletin(request):
    """
        Supprime un bulletin de paie.

    :param request: L'objet HttpRequest utilisé pour effectuer la requête.
    :return: redirect : redirige l'utilisateur vers la page affichant la liste des bulletins de paie de l'année universitaire courante.
    
        **Context**

        ``bulletin``
            une instance du :model:`main.Salaire`.
    """
    if request.method == 'GET':
        bulletin_id = request.GET.get('id')
        bulletin = get_object_or_404(Salaire, id=bulletin_id)
        bulletin.delete()
    id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
    return redirect('paiement:bulletins_de_paye', id_annee_selectionnee=id_annee_selectionnee)


def detail_bulletin(request, id):
    """
    Affiche les informations détaillées d'un bulletin de paie d'un employé donnée à savoir le salaire brut, les retenus CNSS, les primes, le salaire net à payer, etc...

    :param request: L'objet HttpRequest utilisé pour effectuer la requête.
    :param id : L'ID du bulletin de paie sélectionné.
    :return: Un objet HttpResponse contenant le rendu de la page 'salaires/detail_bulletin.html'.

    Cette vue récupère les informations détaillées d'un bulletin de paie d'un employé donnée,
    puis les renvoie au template 'salaires/detail_bulletin.html' pour affichage.
    """
    bulletin = get_object_or_404(Salaire, id=id)
    total_primes = bulletin.prime_efficacite + bulletin.prime_qualite + bulletin.frais_travaux_complementaires
    frais_prestations_familiale_salsalaire = bulletin.frais_prestations_familiale_salsalaire * bulletin.personnel.salaireBrut
    primes = (
            bulletin.prime_efficacite
            + bulletin.prime_qualite
            + bulletin.frais_travaux_complementaires
            + bulletin.prime_anciennete
    )
    Salaire_brut = bulletin.personnel.salaireBrut + primes

    ## pour le salarié
    tcs = bulletin.tcs
    retenues_cnss_personnel = frais_prestations_familiale_salsalaire + tcs

    ## pour l'employeur
    frais_prestations_familiales = bulletin.frais_prestations_familiales * bulletin.personnel.salaireBrut
    frais_risques_professionnel = bulletin.frais_risques_professionnel * bulletin.personnel.salaireBrut
    frais_pension_vieillesse_emsalaire = bulletin.frais_pension_vieillesse_emsalaire * bulletin.personnel.salaireBrut
    retenues_cnss_employeur = frais_prestations_familiales + frais_risques_professionnel + frais_pension_vieillesse_emsalaire

    context = {
        'bulletin' : bulletin,
        'Salaire_brut' : Salaire_brut,
        'retenues_cnss_personnel' : retenues_cnss_personnel,
        'total_primes' : total_primes,
        'retenues_cnss_employeur' : retenues_cnss_employeur,
    }

    return render(request, 'salaires/detail_bulletin.html', context)



@login_required(login_url=settings.LOGIN_URL)
def bulletin_de_paye(request, id):
    """
    Affiche en version pdf le bulletin de paie d'un employé donnée.

    Args:
        request (HttpRequest): L'objet de requête HTTP utilisé par Django.
        id_annee_selectionnee (int): L'identifiant de l'année universitaire sélectionnée.

    Returns:HttpResponse: Une réponse HTTP contenant le bilan des paiements en format HTML.
    Raises:AnneeUniversitaire.DoesNotExist: Si l'année universitaire avec l'ID donné n'existe pas.

    """

    bulletin = get_object_or_404(Salaire, id=id)
    date_debut_formatted = datetime.strptime(str(bulletin.date_debut), "%Y-%m-%d").strftime("%d %B %Y")
    date_fin_formatted = datetime.strptime(str(bulletin.date_fin), "%Y-%m-%d").strftime("%d %B %Y")

    total_primes = bulletin.prime_efficacite + bulletin.prime_qualite + bulletin.frais_travaux_complementaires
    frais_prestations_familiale_salsalaire = bulletin.frais_prestations_familiale_salsalaire * bulletin.personnel.salaireBrut
    primes = (
            bulletin.prime_efficacite
            + bulletin.prime_qualite
            + bulletin.frais_travaux_complementaires
            + bulletin.prime_anciennete
    )
    Salaire_brut = bulletin.personnel.salaireBrut + primes 
    ## pour le salarié
    tcs = bulletin.tcs
    irpp = bulletin.calculer_irpp_mensuel()
    print("calculer_irpp_mensuel   " + str(irpp))

    retenues_cnss_personnel = Decimal(frais_prestations_familiale_salsalaire) + Decimal(tcs) + Decimal(irpp)
    salaire_net = (Decimal(Salaire_brut) - Decimal(retenues_cnss_personnel))
    salaire_net = salaire_net.quantize(Decimal('0.000'), rounding=ROUND_DOWN) 
    bulletin.salaire_net_a_payer = salaire_net - bulletin.acomptes

    ## pour l'employeur
    frais_prestations_familiales = bulletin.frais_prestations_familiales * bulletin.personnel.salaireBrut
    frais_risques_professionnel = bulletin.frais_risques_professionnel * bulletin.personnel.salaireBrut
    frais_pension_vieillesse_emsalaire = bulletin.frais_pension_vieillesse_emsalaire * bulletin.personnel.salaireBrut
    retenues_cnss_employeur = frais_prestations_familiales + frais_risques_professionnel + frais_pension_vieillesse_emsalaire

    context = {
        'bulletin' : bulletin,
        'Salaire_brut': Salaire_brut,
        'irpp' : irpp,
        'tcs' : tcs,
        'salaire_net' : salaire_net,
        'total_primes' : total_primes,
        'retenues_cnss_employeur' : retenues_cnss_employeur,
        'frais_risques_professionnel' : frais_risques_professionnel,
        'frais_prestations_familiales' : frais_prestations_familiales,
        'frais_pension_vieillesse_emsalaire' : frais_pension_vieillesse_emsalaire,
        'frais_prestations_familiale_salsalaire' : frais_prestations_familiale_salsalaire,
        "date_debut_formatted" : date_debut_formatted,
        "date_fin_formatted" : date_fin_formatted,
    }

    latex_input = 'bulletin_de_paye'
    latex_ouput = 'generated_bulletin_de_paye'
    pdf_file = 'pdf_bulletin_de_paye'

    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    # visualisation du pdf dans le navigateur
    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        return response



@login_required(login_url=settings.LOGIN_URL)
def liste_paiements_fournisseurs(request, id_annee_selectionnee):
    """
    Affiche la liste des versements effectués aux fournisseurs de services pour une année universitaire donnée.

    :param request: L'objet HttpRequest utilisé pour effectuer la requête.
    :param id_annee_selectionnee: L'ID de l'année universitaire sélectionnée.
    :return: Un objet HttpResponse contenant le rendu de la page 'fournisseurs/liste_paiements_fournisseurs.html'.
    :raises: Http404 si l'année universitaire sélectionnée n'est pas trouvée.

    Cette vue récupère les versements effectués aux fournisseurs de services associés à l'année universitaire spécifiée,
    puis les renvoie au template 'fournisseurs/liste_paiements_fournisseurs.html' pour affichage.
    """
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    paiements_fournisseurs = Fournisseur.objects.filter(annee_universitaire=annee_universitaire)
    context = {
        'annee_universitaire': annee_universitaire,
        'paiements_fournisseurs': paiements_fournisseurs,
    }
    return render(request, 'fournisseurs/liste_paiements_fournisseurs.html', context)



@login_required(login_url=settings.LOGIN_URL)
def enregistrer_paiement_fournisseur(request, id=0):
    """
    Cette vue permet d'enregistrer ou de mettre à jour les informations concernant les paiements effectués aux fournisseurs de service.
    Si l'ID est fourni, elle met à jour les informations concernant le paiement existant avec les nouvelles données.
    Sinon, elle crée une nouvelle instance pour stocker les informations concernant le paiement.

    Args:
        request (HttpRequest): L'objet HttpRequest reçu.
        id (int, optional): L'identifiant du paiement à mettre à jour. Par défaut 0.

    Returns:
        HttpResponse: La réponse HTTP rendue par la vue.
    'fournisseurs/enregistrer_paiement_fournisseur.html' : correspond au template qui est renvoyer.

    Raises:
        None
    """
    if request.method == "GET":
        if id == 0:
            form = FournisseurForm()
        else:
            paiement_fournisseur = Fournisseur.objects.get(pk=id)
            form = FournisseurForm(instance=paiement_fournisseur)   
        return render(request, 'fournisseurs/enregistrer_paiement_fournisseur.html', {'form': form}) 
    else:
        if id == 0:
            form = FournisseurForm(request.POST)
        else:
            paiement_fournisseur = Fournisseur.objects.get(pk=id)
            compte_universite = paiement_fournisseur.compte_bancaire
            compte_universite.solde_bancaire += paiement_fournisseur.montant
            compte_universite.save()
            form = FournisseurForm(request.POST,instance= paiement_fournisseur)
        if form.is_valid():
            paiement_fournisseur = form.save(commit=False)
            compte_universite = CompteBancaire.objects.first()
            paiement_fournisseur.compte_bancaire = compte_universite
            paiement_fournisseur.save()

            compte_universite.solde_bancaire -= paiement_fournisseur.montant
            compte_universite.save()

            id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
            return redirect('paiement:liste_paiements_fournisseurs', id_annee_selectionnee=id_annee_selectionnee)                                          
        else:
            return render(request, 'fournisseurs/enregistrer_paiement_fournisseur.html', {'form': form})



@login_required(login_url=settings.LOGIN_URL)
def liste_fiches_de_paie(request, id_annee_selectionnee):
    """
    Affiche la liste des fiches de paie pour une année universitaire donnée.

    :param request: L'objet HttpRequest utilisé pour effectuer la requête.
    :param id_annee_selectionnee: L'ID de l'année universitaire sélectionnée.
    :return: Un objet HttpResponse contenant le rendu de la page 'fichePaies/fiche_de_paie_list.html'.
    :raises: Http404 si l'année universitaire sélectionnée n'est pas trouvée.

    Cette vue récupère les fiches de paie associés à l'année universitaire spécifiée,
    puis les renvoie au template 'fichePaies/fiche_de_paie_list.html' pour affichage.
    """
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    fiches = FicheDePaie.objects.filter(annee_universitaire=annee_universitaire)
    context = {
        'annee_universitaire': annee_universitaire,
        'fiches': fiches,
    }
    return render(request, 'fichePaies/fiche_de_paie_list.html', context)



def delete_fiches_de_paie(request):
    """
        Supprime une fiche de paie.

    :param request: L'objet HttpRequest utilisé pour effectuer la requête.
    :return: redirect : redirige l'utilisateur vers la page affichant la liste des fiches de paie de l'année universitaire courante.
    
        **Context**

        ``fiche_paie``
            une instance du : model:`main.FicheDePaie`.
    """
    if request.method == 'GET':
        fiche_paie_id = request.GET.get('id')
        fiche_paie = get_object_or_404(FicheDePaie, id=fiche_paie_id)
        fiche_paie.delete()
    id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
    return redirect('paiement:liste_fiches_de_paie', id_annee_selectionnee=id_annee_selectionnee)


@login_required(login_url=settings.LOGIN_URL)
def enregistrer_fiche_de_paie(request, id=0):
    """
    Enregistre ou met à jour la fiche de paie dans le système.
    Si l’ID est fourni, elle met à jour les informations concernant la fiche de paie existante avec les nouvelles données. Sinon, elle crée une nouvelle instance de fiche de paie.

    Args:
        request: L'objet HttpRequest qui représente la requête HTTP reçue.
        id (int, optional): L'identifiant de la fiche de paie à modifier (par défaut : 0).

    Returns:
        HttpResponse: La réponse HTTP renvoyée au client.
    'fichePaies/create_fiche_de_paie.html' : correspond au template qui est renvoyer.

    Raises:
        None

    """
    if request.method == "GET":
        if id == 0:
            form = FicheDePaieForm()
        else:
            fiche_de_paie = FicheDePaie.objects.get(pk=id)
            form = FicheDePaieForm(instance=fiche_de_paie)   
        return render(request, 'fichePaies/create_fiche_de_paie.html', {'form': form})
    else:
        if id == 0:
            form = FicheDePaieForm(request.POST)
        else:
            fiche_de_paie = FicheDePaie.objects.get(pk=id)
            compte_universite = fiche_de_paie.compte_bancaire
            compte_universite.solde_bancaire += fiche_de_paie.montant 
            compte_universite.save()
            form = FicheDePaieForm(request.POST,instance=fiche_de_paie)
        if form.is_valid():
            fiche_de_paie = form.save(commit=False)
            dateDebut = form.cleaned_data['dateDebut']
            dateFin = form.cleaned_data['dateFin']
            matieres_L1 = form.cleaned_data['matieres_L1']
            matieres_L2 = form.cleaned_data['matieres_L2']
            matieres_L3 = form.cleaned_data['matieres_L3']

            # Vérification de la validité des dates
            if dateDebut and dateFin and dateDebut > dateFin:
                form.add_error('dateFin', "La date de fin ne peut pas être antérieure à la date de début.")
                return render(request, 'fichePaies/create_fiche_de_paie.html', {'form': form})
            
            compte_universite = CompteBancaire.objects.first()
            if compte_universite is not None :
                fiche_de_paie.compte_bancaire = compte_universite
                fiche_de_paie.save()

                # Ajouter les matières sélectionnées à la fiche de paie
                fiche_de_paie.matiere.add(*matieres_L1, *matieres_L2, *matieres_L3)

                compte_universite.solde_bancaire -= fiche_de_paie.montant 
                compte_universite.save()

                id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
                return redirect('paiement:liste_fiches_de_paie', id_annee_selectionnee=id_annee_selectionnee)           
            else:
                return render(request, 'etudiants/message_erreur.html', {"message": "Le compte bancaire n'existe pas"})                               
        else:
            return render(request, 'fichePaies/create_fiche_de_paie.html', {'form': form})
    


@login_required(login_url=settings.LOGIN_URL)
def fiche_paie(request, id):
    """
    Affiche en version pdf la fiche de paie d'un employé donnée à savoir les identifiants de l'employé en question, la période de paie, le nombre d'heure travaillé, le salaire net à payer etc...

    :param request: L'objet HttpRequest utilisé pour effectuer la requête.
    :param id : L'ID de la fiche de paie sélectionné.

    """
    fiche_paie = get_object_or_404(FicheDePaie, id=id)

    # Formatage des dates en "jour mois année"
    
    date_debut_formatted = datetime.strptime(str(fiche_paie.dateDebut), "%Y-%m-%d").strftime("%d %B %Y")
    date_fin_formatted = datetime.strptime(str(fiche_paie.dateFin), "%Y-%m-%d").strftime("%d %B %Y")


    matieres_L1 = ", ".join([matiere.libelle for matiere in fiche_paie.matiere.filter(ue__programme__semestre__libelle__in=['S1', 'S2'])])
    matieres_L2 = ", ".join([matiere.libelle for matiere in fiche_paie.matiere.filter(ue__programme__semestre__libelle__in=['S3', 'S4'])])
    matieres_L3 = ", ".join([matiere.libelle for matiere in fiche_paie.matiere.filter(ue__programme__semestre__libelle__in=['S5', 'S6'])])

    context = {
        'fiche_paie': fiche_paie,
        'matieres_L1': matieres_L1,
        'matieres_L2': matieres_L2,
        'matieres_L3': matieres_L3,
        'date_debut_formatted': date_debut_formatted,
        'date_fin_formatted': date_fin_formatted,
    }

    latex_input = 'fiche_paie'
    latex_ouput = 'generated_fiche_paie'
    pdf_file = 'pdf_fiche_paie'

    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        return response



@login_required(login_url=settings.LOGIN_URL)
def liste_fiches_de_prise_en_charge(request, id_annee_selectionnee):
    """
    Affiche la liste des fiches de prise en charge des volontaires pour une année universitaire donnée.

    :param request: L'objet HttpRequest utilisé pour effectuer la requête.
    :param id_annee_selectionnee: L'ID de l'année universitaire sélectionnée.
    :return: Un objet HttpResponse contenant le rendu de la page 'charges/liste_fiches_de_prise_en_charge.html'.
    :raises: Http404 si l'année universitaire sélectionnée n'est pas trouvée.

    Cette vue récupère les fiches de prise en charge des volontaires associés à l'année universitaire spécifiée,
    puis les renvoie au template 'charges/liste_fiches_de_prise_en_charge.html' pour affichage.
    """
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    fiches = Charge.objects.filter(annee_universitaire=annee_universitaire)
    context = {
        'annee_universitaire': annee_universitaire,
        'fiches': fiches,
    }
    return render(request, 'charges/liste_fiches_de_prise_en_charge.html', context)



@login_required(login_url=settings.LOGIN_URL)
def enregistrer_fiche_de_prise_en_charge(request, id=0):
    """
    Enregistre ou met à jour la fiche de prise en charge dans le système.
    Si l’ID est fourni, elle met à jour les informations concernant la fiche de prise en charge existante avec les nouvelles données. Sinon, elle crée une nouvelle instance de fiche de prise en charge.

    Args:
        request: L'objet HttpRequest qui représente la requête HTTP reçue.
        id (int, optional): L'identifiant de la fiche de prise en charge à modifier (par défaut : 0).

    Returns:
        HttpResponse: La réponse HTTP renvoyée au client.
    'charges/create_fiche_de_prise_en_charge.html' : correspond au template qui est renvoyer.

    Raises:
        None

    """
    if request.method == "GET":
        if id == 0:
            form = ChargeForm()
        else:
            fiche_de_charge = Charge.objects.get(pk=id)
            form = ChargeForm(instance=fiche_de_charge)   
        return render(request, 'charges/create_fiche_de_prise_en_charge.html', {'form': form})
    else:
        if id == 0:
            form = ChargeForm(request.POST)
        else:
            fiche_de_charge = Charge.objects.get(pk=id)
            compte_universite = fiche_de_charge.compte_bancaire
            compte_universite.solde_bancaire += fiche_de_charge.montant 
            compte_universite.save()
            form = ChargeForm(request.POST,instance=fiche_de_charge)
        if form.is_valid():
            fiche_de_charge = form.save(commit=False)
            dateDebut = fiche_de_charge.dateDebut
            dateFin = fiche_de_charge.dateFin

            # Vérification de la validité des dates
            if dateDebut and dateFin and dateDebut > dateFin:
                form.add_error('dateFin', "La date de fin ne peut pas être antérieure à la date de début.")
                return render(request, 'charges/create_fiche_de_prise_en_charge.html', {'form': form})
            
            compte_universite = CompteBancaire.objects.first()
            if compte_universite is not None :
                fiche_de_charge.compte_bancaire = compte_universite
                fiche_de_charge.save()

                compte_universite.solde_bancaire -= fiche_de_charge.montant 
                compte_universite.save()

                id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
                return redirect('paiement:liste_fiches_de_prise_en_charge', id_annee_selectionnee=id_annee_selectionnee)         
            else:
                return render(request, 'etudiants/message_erreur.html', {"message": "Le compte bancaire n'existe pas"})                               
        else:
            return render(request, 'charges/create_fiche_de_prise_en_charge.html', {'form': form})


@login_required(login_url=settings.LOGIN_URL)
def fiche_de_charge(request, id):
    """
    Affiche en version pdf la fiche de prise en charge d'un employé donnée à savoir les identifiants de l'employé en question, les frais de vie, les frais de nourriture etc...

    :param request: L'objet HttpRequest utilisé pour effectuer la requête.
    :param id : L'ID de la fiche de paie sélectionné.

    """
    fiche_de_charge = get_object_or_404(Charge, id=id)
    date_debut_formatted = datetime.strptime(str(fiche_de_charge.dateDebut), "%Y-%m-%d").strftime("%d %B %Y")
    date_fin_formatted = datetime.strptime(str(fiche_de_charge.dateFin), "%Y-%m-%d").strftime("%d %B %Y")

    context = {
        'fiche_de_charge': fiche_de_charge,
        'date_debut_formatted' :date_debut_formatted,
        'date_fin_formatted' : date_fin_formatted,
    }

    latex_input = 'fiche_de_charge'
    latex_ouput = 'generated_fiche_de_charge'
    pdf_file = 'pdf_fiche_de_charge'

    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        return response