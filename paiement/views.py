from main.models import *
import os
from django import forms
from decimal import Decimal
from django.http import HttpResponse, JsonResponse
from paiement.forms import  FicheDePaieForm, PersonnelForm, PaiementForm, FournisseurForm, FraisForm, CompteBancaireForm, VersmentSalaireForm, ChargeForm, StagiairesForm
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
from django.contrib import messages
# Définir la locale en français
# locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')


###############
@login_required(login_url=settings.LOGIN_URL)
def delete_frais_scolarite(request,id):
    """
   Supprime un frais soclaire .

    :param request: L'objet HttpRequest utilisé pour effectuer la requête.
    :param id: L'ID du paiment à supprimer.
    :return: rediriger vers l'url  'paiement/liste_paiements' qui affiche la liste des paiements.
   

    Cette vue récupère un frais soclaire associé à l'Id spécifié et la supprime,
    puis redirige vers l'url 'paiement/liste_paiements' pour affichage de la liste des paiements.
    """
    
    paiement=get_object_or_404(Paiement,pk=id)
    paiement.delete()
    id_annee_selectionnee = request.session.get('id_annee_selectionnee')
    texte=f"Le paiement {paiement.type}  a été supprimé avec sucèss"
    messages.success(request, texte)
    return redirect("paiement:liste_paiements",id_annee_selectionnee=id_annee_selectionnee)



@login_required(login_url=settings.LOGIN_URL)
def liste_des_membres_de_personnels(request):
    membres_de_personnels = Personnel.objects.all()
    membres_de_personnels_data = {
        "membres_de_personnels": membres_de_personnels,
    }
    #return JsonResponse(membres_de_personnels_data)
    return render(request, 'personnels/membres_de_personnels.html', membres_de_personnels_data)


@login_required(login_url=settings.LOGIN_URL)
def ajouter_personnel(request, id=0):
    if request.method == "GET":
        if id == 0:
            form = PersonnelForm()
        else:
            personnel = Personnel.objects.get(pk=id)
            form = PersonnelForm(instance=personnel)   
        return render(request, 'personnels/create_personnel.html', {'form': form})
    else:
        if id == 0:
            form = PersonnelForm(request.POST)
        else:
            personnel = Personnel.objects.get(pk=id)
            form = PersonnelForm(request.POST,instance= personnel)
        if form.is_valid():
            form.save()
            return redirect('paiement:liste_des_membres_de_personnels')
        else:
            print(form.errors)
            return render(request, 'personnels/create_personnel.html', {'form': form})


@login_required(login_url=settings.LOGIN_URL)
def personnel_details(request, id):
    personnel_details = get_object_or_404(Personnel, id=id)
    return render(request, 'personnels/personnel_details.html', {'personnel_details': personnel_details})


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
            ###retarder la sauvegarde pour recuperer annee_selectionnee avant de sauvegarder
            frais=form.save(commit=False)
            id_annee_selectionnee = request.session.get('id_annee_selectionnee')
            annee_selectionnee = get_object_or_404( AnneeUniversitaire, pk=id_annee_selectionnee)
            frais.annee_universitaire =annee_selectionnee
            frais.save()

            
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
            form = PersonnelForm()
        else:
            comptable = PersonnelForm.objects.get(pk=id)
            form = PersonnelForm(instance=comptable)   
        return render(request, 'comptables/create_comptable.html', {'form': form})
    else:
        if id == 0:
            form = PersonnelForm(request.POST)
        else:
            comptable = Personnel.objects.get(pk=id)
            form = PersonnelForm(request.POST,instance= comptable)
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
    comptable = get_object_or_404(Personnel, id=id)
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
    comptables = Personnel.objects.filter(user__is_active=True,user__groups__name="comptable")
    
    
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
    comptables = Personnel.objects.filter(is_active=False,user__groups__name="comptable")
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
    id_annee_selectionnee = request.session["id_annee_selectionnee"]
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    paiements = Paiement.objects.filter(annee_universitaire=annee_universitaire)

    
    semestres = annee_universitaire.get_semestres()
    
    

    context = {
        'semestres' : semestres,
        'paiements': paiements,
        'frais_scolaires_min' : 0,
        'frais_scolaires_max' : 600000,
    }
    return render(request, 'paiements/liste_paiements.html', context)

### verifier si c'est un comptable
def is_comptable(personnel):
    pass

#ajouter un controle de permisssion pour verifier que le user faisant cette operation est un comptable
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
    #recuperons l'annee courante
    id_annee_selectionnee = request.session.get('id_annee_selectionnee')
    annee_selectionnee = get_object_or_404( AnneeUniversitaire, pk=id_annee_selectionnee)
    if request.method == "GET":
        if id == 0:
            form = PaiementForm()
        else:
            paiement = Paiement.objects.get(pk=id)
            form = PaiementForm(instance=paiement) 
            
        #recuperons le montant d'inscription qui sera injecté dans le script js de template une fois accessible
        
        frais_scolaire=Frais.objects.get(annee_universitaire=annee_selectionnee)

        frais_inscription=frais_scolaire.montant_inscription  
        return render(request, 'paiements/enregistrer_paiement.html', {'form': form,'frais_inscription':frais_inscription}) 
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
            
            comptable = Personnel.objects.get(user=request.user)
            paiement.comptable = comptable
            compte_universite = CompteBancaire.objects.first()
            paiement.compte_bancaire = compte_universite
            
            paiement.annee_universitaire=annee_selectionnee
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
def irpp_mensuel(request,id_annee_selectionnee):
    """
    Affiche IRPP pour un mois donnée.

    :param request: L'objet HttpRequest utilisé pour effectuer la requête.
    :param date_debut: L'ID de l'année universitaire sélectionnée.
    :param id_annee_selectionnee: L'ID de l'année universitaire sélectionnée.
    :return: Un objet HttpResponse contenant les donnée sous form de json.
    :raises: Http404 si l'année universitaire sélectionnée n'est pas trouvée.

    Cette vue récupère IRPP pour un mois donnée,
    puis  renvoie l'irpp sous form de json.
    """
    salaires = VersmentSalaire.objects.filter(annee_universitaire=id_annee_selectionnee)
    total_irpp = sum(VersmentSalaire.irpp + salaire.tcs for salaire in salaires)    
    total_irpp_by_month = VersmentSalaire.objects.values('date_debut__month').annotate(total_irpp=Sum('irpp'))
    MONTH_NAMES = {
    1: "Janvier",
    2: "Février",
    3: "Mars",
    4: "Avril",
    5: "Mai",
    6: "Juin",
    7: "Juillet",
    8: "Août",
    9: "Septembre",
    10: "Octobre",
    11: "Novembre",
    12: "Décembre",
    }
    for item in total_irpp_by_month:
        month_number = item['date_debut__month']
        item['month_name'] = MONTH_NAMES[month_number]
    context={
        "total_irpp":total_irpp,
        "total_irpp_by_month":total_irpp_by_month,
    }
    return render(request, 'compte_bancaire/irpp_mensuel.html', context)




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

    ##########
    salaires=VersmentSalaire.objects.filter(annee_universitaire=id_annee_selectionnee)
    
    salaires_anpe =VersmentSalaire.objects.filter(annee_universitaire=id_annee_selectionnee,personnel__qualification_professionnel='Stagiaire')
    ### salaires_ifnti est une liste des salaires des enseignants d'ifnti sauf le stagiaire
    salaires_ifnti = VersmentSalaire.objects.filter(annee_universitaire=id_annee_selectionnee).exclude(personnel__qualification_professionnel='Stagiaire')
       
    total_salaire_brut = sum(salaire.personnel.salaireBrut + salaire.prime_efficacite + salaire.prime_qualite + salaire.frais_travaux_complementaires+ salaire.prime_anciennete for salaire in salaires)
      
      
    total_cnss = 0
    total_ifnti=0
    total_anpe=0
    for salaire in salaires_ifnti:
        total_ifnti += (salaire.frais_prestations_familiale_salsalaire * salaire.personnel.salaireBrut) + (salaire.frais_prestations_familiales * salaire.personnel.salaireBrut) + (salaire.frais_risques_professionnel * salaire.personnel.salaireBrut) + (salaire.frais_pension_vieillesse_emsalaire * salaire.personnel.salaireBrut) + (salaire.assurance_maladie_universelle*salaire.personnel.salaireBrut + salaire.assurance_maladie_universelle*salaire.personnel.salaireBrut) 
    
    for salaire in salaires_anpe:
        total_anpe+=salaire.frais_risques_professionnel * salaire.personnel.salaireBrut
        
    total_cnss=total_ifnti+total_anpe
      
    total_irpp = sum(salaire.irpp + salaire.tcs for salaire in salaires)
    total_salaire_net = sum(salaire.salaire_net_a_payer for salaire in salaires)
    montant_total_salaires = sum(salaire.salaire_net_a_payer + (salaire.frais_prestations_familiale_salsalaire * salaire.personnel.salaireBrut + salaire.frais_prestations_familiales * salaire.personnel.salaireBrut + salaire.frais_risques_professionnel * salaire.personnel.salaireBrut + salaire.frais_pension_vieillesse_emsalaire * salaire.personnel.salaireBrut + salaire.tcs)for salaire in salaires)

    fournisseurs = Fournisseur.objects.filter(annee_universitaire=id_annee_selectionnee)
    total_paiements_fournisseurs = sum(fournisseur.montant for fournisseur in fournisseurs)

    fiche_de_paies = FicheDePaie.objects.filter(annee_universitaire=id_annee_selectionnee)
    total_fiche_de_paies = sum(fiche_de_paie.montant for fiche_de_paie in fiche_de_paies)

    fiche_de_charge = Charge.objects.filter(annee_universitaire=id_annee_selectionnee)
    total_charges = sum(fiche.montant for fiche in fiche_de_charge)

    total_salaires = (total_charges + total_fiche_de_paies) + float(montant_total_salaires)

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
        'salaires':salaires
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
    
    salaires = VersmentSalaire.objects.filter(annee_universitaire=id_annee_selectionnee)
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
    #bulletins = VersmentSalaire.objects.filter(annee_universitaire=annee_universitaire, personnel__qualification_professionnel__in=['Enseignant', 'Comptable', 'Directeur des études', 'Gardien', 'Agent d\'entretien'])
    bulletins = VersmentSalaire.objects.filter(annee_universitaire=annee_universitaire).exclude(personnel__qualification_professionnel='Stagiaire')
    print("liste des bulletins")
    print(bulletins)
    context = {
        'annee_universitaire': annee_universitaire,
        'bulletins': bulletins,
    }
    #return HttpResponse('')
    return render(request, 'salaires/bulletins_de_paye.html', context)


@login_required(login_url=settings.LOGIN_URL)
def les_bulletins_de_paye_stagiaire(request, id_annee_selectionnee):
    """
    Affiche la liste des bulletins de paie pour une année universitaire donnée.

    :param request: L'objet HttpRequest utilisé pour effectuer la requête.
    :param id_annee_selectionnee: L'ID de l'année universitaire sélectionnée.
    :return: Un objet HttpResponse contenant le rendu de la page 'salaires/bulletins_de_paye.html'.
    :raises: Http404 si l'année universitaire sélectionnée n'est pas trouvée.

    Cette vue récupère les bulletins de paie associés à l'année universitaire spécifiée,
    puis les renvoie au template 'salaires/bulletins_de_paye.html' pour affichage.
    """
    id_annee_selectionnee = request.session.get('id_annee_selectionnee')
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    print(VersmentSalaire.objects.filter(personnel__qualification_professionnel='Stagiaire'))
    bulletins = VersmentSalaire.objects.filter(annee_universitaire=annee_universitaire, personnel__qualification_professionnel='Stagiaire')
    context = {
        'annee_universitaire': annee_universitaire,
        'bulletins': bulletins,
    }
    return render(request, 'salaires/les_bulletins_de_paye_stagiaire.html', context)




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
            form = VersmentSalaireForm()
        else:
            bulletin = VersmentSalaire.objects.get(pk=id)
            form = VersmentSalaireForm(instance=bulletin)   
        return render(request, 'salaires/enregistrer_bulletin.html', {'form': form})
    else:
        if id == 0:
            form = VersmentSalaireForm(request.POST)
        else:
            bulletin = VersmentSalaire.objects.get(pk=id)
            compte_universite = bulletin.compte_bancaire
            compte_universite.solde_bancaire += bulletin.salaire_net_a_payer + bulletin.tcs + (Decimal(bulletin.frais_prestations_familiale_salsalaire) * Decimal(bulletin.personnel.salaireBrut) + Decimal(bulletin.frais_prestations_familiales) * Decimal(bulletin.personnel.salaireBrut) + Decimal(bulletin.frais_risques_professionnel) * Decimal(bulletin.personnel.salaireBrut) + Decimal(bulletin.frais_pension_vieillesse_emsalaire) * Decimal(bulletin.personnel.salaireBrut))
            print(bulletin.salaire_net_a_payer + bulletin.tcs + (Decimal(bulletin.frais_prestations_familiale_salsalaire) * Decimal(bulletin.personnel.salaireBrut) + Decimal(bulletin.frais_prestations_familiales) * Decimal(bulletin.personnel.salaireBrut) + Decimal(bulletin.frais_risques_professionnel) * Decimal(bulletin.personnel.salaireBrut) + Decimal(bulletin.frais_pension_vieillesse_emsalaire) * Decimal(bulletin.personnel.salaireBrut)))
            compte_universite.save()
            form = VersmentSalaireForm(request.POST, instance=bulletin)
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
                compte_universite.solde_bancaire -= float(montant_a_prelever)
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
        bulletin = get_object_or_404(VersmentSalaire, id=bulletin_id)
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
    bulletin = get_object_or_404(VersmentSalaire, id=id)
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

    bulletin = get_object_or_404(VersmentSalaire, id=id)
    salaireDeBase = int(bulletin.personnel.salaireBrut)
    prime_efficacite = int(bulletin.prime_efficacite)
    prime_qualite = int(bulletin.prime_qualite)
    frais_travaux_complementaires = int(bulletin.frais_travaux_complementaires)
    prime_anciennete = int(bulletin.prime_anciennete)
    date_debut_formatted = datetime.strptime(str(bulletin.date_debut), "%Y-%m-%d").strftime("%d %B %Y")
    date_fin_formatted = datetime.strptime(str(bulletin.date_fin), "%Y-%m-%d").strftime("%d %B %Y")

    total_primes = int(bulletin.prime_efficacite + bulletin.prime_qualite + bulletin.frais_travaux_complementaires)
    primes = (
            bulletin.prime_efficacite
            + bulletin.prime_qualite
            + bulletin.frais_travaux_complementaires
            + bulletin.prime_anciennete
    )
    Salaire_brut = int(bulletin.personnel.salaireBrut + primes)
    
    ## pour le salarié
    frais_prestations_familiale_salsalaire = int(bulletin.frais_prestations_familiale_salsalaire * bulletin.personnel.salaireBrut)
    assurance_maladie_universelle = int(bulletin.assurance_maladie_universelle * bulletin.personnel.salaireBrut)
    retenues_cnss_salarie = int(frais_prestations_familiale_salsalaire + assurance_maladie_universelle)
    tcs = int(bulletin.tcs)
    irpp = int(bulletin.calculer_irpp_mensuel())
    acomptes = int(bulletin.acomptes)
    prime_forfaitaire = int(bulletin.prime_forfaitaire)
    print("calculer_irpp_mensuel   " + str(irpp))

    retenues_cnss_personnel = Decimal(retenues_cnss_salarie) + Decimal(tcs) + Decimal(irpp)
    salaire_net = (Decimal(Salaire_brut) - Decimal(retenues_cnss_personnel))
    bulletin.salaire_net_a_payer = int(salaire_net - bulletin.acomptes) + int(bulletin.prime_forfaitaire)   # Conversion en entier
    # Convertir le montant en une chaîne de caractères
    salaire_net_str = "{:,.0f}".format(bulletin.salaire_net_a_payer)
    # Assigner la chaîne de caractères formatée à salaire_net_a_payer
    bulletin.salaire_net_a_payer = salaire_net_str


    ## pour l'employeur
    frais_prestations_familiales = int(bulletin.frais_prestations_familiales * bulletin.personnel.salaireBrut)
    frais_risques_professionnel = int(bulletin.frais_risques_professionnel * bulletin.personnel.salaireBrut)
    frais_pension_vieillesse_emsalaire = int(bulletin.frais_pension_vieillesse_emsalaire * bulletin.personnel.salaireBrut)
    retenues_cnss_employeur = int(frais_prestations_familiales + frais_risques_professionnel + frais_pension_vieillesse_emsalaire + assurance_maladie_universelle)

    # Convertir les montants en chaînes de caractères formatées avec des séparateurs de milliers
    prime_efficacite_str = "{:,.0f}".format(prime_efficacite)
    prime_qualite_str = "{:,.0f}".format(prime_qualite)
    frais_travaux_complementaires_str = "{:,.0f}".format(frais_travaux_complementaires)
    prime_anciennete_str = "{:,.0f}".format(prime_anciennete)
    salaireDeBase_str = "{:,.0f}".format(salaireDeBase)
    Salaire_brut_str = "{:,.0f}".format(Salaire_brut)
    irpp_str = "{:,.0f}".format(irpp)
    tcs_str = "{:,.0f}".format(tcs)
    acomptes_str = "{:,.0f}".format(acomptes)
    prime_forfaitaire_str = "{:,.0f}".format(prime_forfaitaire)
    total_primes_str = "{:,.0f}".format(total_primes)
    retenues_cnss_employeur_str = "{:,.0f}".format(retenues_cnss_employeur)
    frais_risques_professionnel_str = "{:,.0f}".format(frais_risques_professionnel)
    frais_prestations_familiales_str = "{:,.0f}".format(frais_prestations_familiales)
    frais_pension_vieillesse_emsalaire_str = "{:,.0f}".format(frais_pension_vieillesse_emsalaire)
    frais_prestations_familiale_salsalaire_str = "{:,.0f}".format(frais_prestations_familiale_salsalaire)
    assurance_maladie_universelle_str = "{:,.0f}".format(assurance_maladie_universelle)
    retenues_cnss_salarie_str = "{:,.0f}".format(retenues_cnss_salarie)
    salaire_net_str = "{:,.0f}".format(salaire_net)

    # Assigner les chaînes de caractères formatées aux variables correspondantes
    context = {
        'bulletin': bulletin,
        'prime_efficacite': prime_efficacite_str,
        'prime_qualite': prime_qualite_str,
        'frais_travaux_complementaires': frais_travaux_complementaires_str,
        'prime_anciennete': prime_anciennete_str,
        'salaireDeBase': salaireDeBase_str,
        'Salaire_brut': Salaire_brut_str,
        'irpp': irpp_str,
        'tcs': tcs_str,
        'acomptes': acomptes_str,
        'prime_forfaitaire': prime_forfaitaire_str,
        'salaire_net': salaire_net_str,
        'total_primes': total_primes_str,
        'retenues_cnss_employeur': retenues_cnss_employeur_str,
        'frais_risques_professionnel': frais_risques_professionnel_str,
        'frais_prestations_familiales': frais_prestations_familiales_str,
        'frais_pension_vieillesse_emsalaire': frais_pension_vieillesse_emsalaire_str,
        'frais_prestations_familiale_salsalaire': frais_prestations_familiale_salsalaire_str,
        'assurance_maladie_universelle': assurance_maladie_universelle_str,
        "date_debut_formatted": date_debut_formatted,
        "date_fin_formatted": date_fin_formatted,
        "retenues_cnss_salarie": retenues_cnss_salarie_str,
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
            form = FournisseurForm(request.POST,request.FILES)
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
    
    prixUnitaire = fiche_paie.prixUnitaire
    montantL1 = fiche_paie.montantL1
    montantL2 = fiche_paie.montantL2
    montantL3 = fiche_paie.montantL3
    montant = fiche_paie.montant
    acomptes = fiche_paie.acomptes
    difference = fiche_paie.difference

    # Convertir les montants en chaînes de caractères formatées avec des séparateurs de milliers
    prixUnitaire_str = "{:,.0f}".format(prixUnitaire)
    montantL1_str = "{:,.0f}".format(montantL1)
    montantL2_str = "{:,.0f}".format(montantL2)
    montantL3_str = "{:,.0f}".format(montantL3)
    montant_str = "{:,.0f}".format(montant)
    acomptes_str = "{:,.0f}".format(acomptes)
    difference_str = "{:,.0f}".format(difference)

    context = {
        'fiche_paie': fiche_paie,
        'prixUnitaire' : prixUnitaire_str,
        'montantL1' : montantL1_str,
        'montantL2' : montantL2_str,
        'montantL3' : montantL3_str,
        'matieres_L1': matieres_L1,
        'matieres_L2': matieres_L2,
        'matieres_L3': matieres_L3,
        'montant': montant_str,
        'acomptes': acomptes_str,
        'difference': difference_str,
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

    frais_nourriture = fiche_de_charge.frais_nourriture
    frais_de_vie = fiche_de_charge.frais_de_vie
    montant = fiche_de_charge.montant

    frais_nourriture_str = "{:,.0f}".format(frais_nourriture)
    frais_de_vie_str = "{:,.0f}".format(frais_de_vie)
    montant_str = "{:,.0f}".format(montant)

    context = {
        'fiche_de_charge': fiche_de_charge,
        'frais_de_vie' : frais_de_vie_str,
        'frais_nourriture' : frais_nourriture_str,
        'montant' : montant_str,
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
    



@login_required(login_url=settings.LOGIN_URL)
def enregistrer_bulletin_stagiaire(request, id=0):    
    if request.method == "GET":
        if id == 0:
            form = StagiairesForm()
        else:
            bulletin = VersmentSalaire.objects.get(pk=id)
            print(bulletin.date_debut)
            form = StagiairesForm(instance=bulletin)   
        return render(request, 'salaires/enregistrer_bulletin_stagiaire.html', {'form': form})
    else:
        if id == 0:
            form = StagiairesForm(request.POST)
        else:
            bulletin = VersmentSalaire.objects.get(pk=id)
            compte_universite = bulletin.compte_bancaire
            compte_universite.solde_bancaire += bulletin.salaire_net_a_payer + (Decimal(bulletin.frais_risques_professionnel) * Decimal(bulletin.personnel.salaireBrut))
            print(bulletin.salaire_net_a_payer + (Decimal(bulletin.frais_risques_professionnel) * Decimal(bulletin.personnel.salaireBrut)))
            compte_universite.save()
            form = VersmentSalaireForm(request.POST, instance=bulletin)
        if form.is_valid():
            bulletin = form.save(commit=False)
            qualification_professionnelle = 'Stagiaire'
            bulletin.qualification_professionnel = qualification_professionnelle
            date_debut = bulletin.date_debut
            date_fin = bulletin.date_fin
            if date_debut and date_fin and date_debut > date_fin:
                form.add_error('date_fin', "La date de fin ne peut pas être antérieure à la date de début.")
                return render(request, 'salaires/enregistrer_bulletin_stagiaire.html', {'form': form})

            compte_universite = CompteBancaire.objects.first()
            if compte_universite is not None:
                bulletin.compte_bancaire = compte_universite
                bulletin.save()
                deductions = Decimal(bulletin.frais_risques_professionnel) * Decimal(bulletin.personnel.salaireBrut)  
                montant_a_prelever = bulletin.salaire_net_a_payer + deductions 
                compte_universite.solde_bancaire -= float(montant_a_prelever)
                compte_universite.save()
                
                id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
                return redirect('paiement:bulletins_de_paye_stagiaire', id_annee_selectionnee=id_annee_selectionnee)
            else :
                return render(request, 'etudiants/message_erreur.html', {'message': "Le compte bancaire n\'existe pas."})
        else:
            print(form.errors)
            return render(request, 'salaires/enregistrer_bulletin_stagiaire.html', {'form': form})




@login_required(login_url=settings.LOGIN_URL)
def bulletin_de_paye_stagiaire(request, id):
    bulletin = get_object_or_404(VersmentSalaire, id=id)
    fiche_paie = get_object_or_404(VersmentSalaire, id=id)
    salaireDeBase = int(bulletin.personnel.salaireBrut)
    prime_efficacite = int(bulletin.prime_efficacite)
    prime_qualite = int(bulletin.prime_qualite)
    frais_travaux_complementaires = int(bulletin.frais_travaux_complementaires)
    prime_anciennete = int(bulletin.prime_anciennete)
    date_debut_formatted = datetime.strptime(str(bulletin.date_debut), "%Y-%m-%d").strftime("%d %B %Y")
    date_fin_formatted = datetime.strptime(str(bulletin.date_fin), "%Y-%m-%d").strftime("%d %B %Y")

    total_primes = int(bulletin.prime_efficacite + bulletin.prime_qualite + bulletin.frais_travaux_complementaires)
    primes = (
            bulletin.prime_efficacite
            + bulletin.prime_qualite
            + bulletin.frais_travaux_complementaires
            + bulletin.prime_anciennete
    )
    Salaire_brut = int(bulletin.personnel.salaireBrut + primes)
    
    ## pour le salarié
    acomptes = int(bulletin.acomptes)
    prime_forfaitaire = int(bulletin.prime_forfaitaire)
    salaire_net = Decimal(Salaire_brut) 
    bulletin.salaire_net_a_payer = int(salaire_net - bulletin.acomptes) + int(bulletin.prime_forfaitaire) # Conversion en entier
    # Convertir le montant en une chaîne de caractères
    salaire_net_str = "{:,.0f}".format(bulletin.salaire_net_a_payer)
    # Assigner la chaîne de caractères formatée à salaire_net_a_payer
    bulletin.salaire_net_a_payer = salaire_net_str
    assurance_maladie_universelle = int(bulletin.assurance_maladie_universelle * bulletin.personnel.salaireBrut)

    ## pour l'employeur
    frais_risques_professionnel = int(bulletin.frais_risques_professionnel * bulletin.personnel.salaireBrut)
    retenues_cnss_employeur = frais_risques_professionnel+assurance_maladie_universelle

    # Convertir les montants en chaînes de caractères formatées avec des séparateurs de milliers
    prime_efficacite_str = "{:,.0f}".format(prime_efficacite)
    prime_qualite_str = "{:,.0f}".format(prime_qualite)
    frais_travaux_complementaires_str = "{:,.0f}".format(frais_travaux_complementaires)
    prime_anciennete_str = "{:,.0f}".format(prime_anciennete)
    salaireDeBase_str = "{:,.0f}".format(salaireDeBase)
    Salaire_brut_str = "{:,.0f}".format(Salaire_brut)
    acomptes_str = "{:,.0f}".format(acomptes)
    prime_forfaitaire_str = "{:,.0f}".format(prime_forfaitaire)
    total_primes_str = "{:,.0f}".format(total_primes)
    retenues_cnss_employeur_str = "{:,.0f}".format(retenues_cnss_employeur)
    frais_risques_professionnel_str = "{:,.0f}".format(frais_risques_professionnel)
    salaire_net_str = "{:,.0f}".format(salaire_net-assurance_maladie_universelle)
    assurance_maladie_universelle_str = "{:,.0f}".format(assurance_maladie_universelle)

    # Assigner les chaînes de caractères formatées aux variables correspondantes
    context = {
        'bulletin': bulletin,
        'prime_efficacite': prime_efficacite_str,
        'prime_qualite': prime_qualite_str,
        'assurance_maladie_universelle' : assurance_maladie_universelle_str,
        'frais_travaux_complementaires': frais_travaux_complementaires_str,
        'prime_anciennete': prime_anciennete_str,
        'salaireDeBase': salaireDeBase_str,
        'Salaire_brut': Salaire_brut_str,
        'acomptes': acomptes_str,
        'prime_forfaitaire': prime_forfaitaire_str,
        'salaire_net': salaire_net_str,
        'total_primes': total_primes_str,
        'retenues_cnss_employeur': retenues_cnss_employeur_str,
        'frais_risques_professionnel': frais_risques_professionnel_str,
        "date_debut_formatted": date_debut_formatted,
        "date_fin_formatted": date_fin_formatted,
        "fiche_paie": fiche_paie,
    }

    latex_input = 'bulletin_de_paye_stagiaire'
    latex_ouput = 'generated_bulletin_de_paye_stagiaire'
    pdf_file = 'pdf_bulletin_de_paye_stagiaire'

    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    # visualisation du pdf dans le navigateur
    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        return response




def delete_bulletin_stagiaire(request):
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
        bulletin = get_object_or_404(VersmentSalaire, id=bulletin_id)
        bulletin.delete()
    id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
    return redirect('paiement:bulletins_de_paye_stagiaire', id_annee_selectionnee=id_annee_selectionnee)





#---------------------------------Option de filtrage lors de l'impression-----------------------------
def option_impression_frais_scolarite_par_semestre(request):
    """
        Reperer l'id de l'année universitaire courante
        Récuperer le montant des frais de scolarité par semestre
        visualisation du pdf dans le navigateur
    """

    recupmin_max = request.POST.get('min_max')
    separtion_chaine = recupmin_max.split("-")
    recupmin = separtion_chaine[0]
    recupmax = separtion_chaine[1]
    recupsemestre = request.POST.getlist('semestres')



    recuperation_montant_frais_scolarite_min, recuperation_montant_frais_scolarite_max = recupmin,recupmax
    montant_frais_scolarites = CompteEtudiant.objects.filter(solde__gte=recuperation_montant_frais_scolarite_min, solde__lte=recuperation_montant_frais_scolarite_max,)

    buildcontext = {}

    #recuperation du montant d'inscription
    recup_montant_inscription = Frais.objects.all()
    for i in recup_montant_inscription:
        reucp_frais = i.montant_inscription
        recup_frais_scolarite = i.montant_scolarite

    
    # montant_frais_scolarites.filter(etudiant__semestres = semestre)
    id_annee_selectionnee = request.session["id_annee_selectionnee"]

    semestres = []
    for sem in recupsemestre:
        semestre = Semestre.objects.filter(id = sem).get()
        data = []
        for compteEtudiant in montant_frais_scolarites:
            if compteEtudiant.etudiant.semestres.filter(id = sem, annee_universitaire__id = id_annee_selectionnee).exists():
                compteEtudiant.montant_restant = recup_frais_scolarite - compteEtudiant.solde
                data.append(compteEtudiant)

        
        buildcontext[semestre.__str__()] = data

    #context pour l'affichage des semestres
    context ={
        'buildcontext' : buildcontext,
        'recupmin' : recupmin,
        'recupmax' : recupmax,
        'reucp_frais':reucp_frais,
    }
    
    latex_input = 'frais_scolarite_par_semestre'
    latex_input = 'bilan_paiements_annuel'
    latex_ouput = 'generated_bilan_paiements_annuel'
    pdf_file = 'pdf_bilan_paiements_annuel'

    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    # visualisation du pdf dans le navigateur
    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_frais.pdf'
        return response

