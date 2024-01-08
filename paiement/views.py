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


@login_required(login_url=settings.LOGIN_URL)
def liste_frais(request, id_annee_selectionnee):

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
    comptable = get_object_or_404(Comptable, id=id)
    return render(request, 'comptables/comptable_detail.html', {'comptable': comptable})


@login_required(login_url=settings.LOGIN_URL)
def comptable_list(request):
    current_annee = AnneeUniversitaire.static_get_current_annee_universitaire()
    comptables = Comptable.objects.filter(is_active=True)
    context = {
        "comptables": comptables,
    }
    return render(request, 'comptables/comptable_list.html', context)


@login_required(login_url=settings.LOGIN_URL)
def comptables_suspendu(request):
    annee_universitaire_courante = AnneeUniversitaire.static_get_current_annee_universitaire()
    comptables = Comptable.objects.filter(is_active=False)
    context = {
        "comptables": comptables,
        "annee_universitaire_courante": annee_universitaire_courante,
    }
    return render(request, 'comptables/comptable_list.html', context)


@login_required(login_url=settings.LOGIN_URL)
def liste_paiements(request, id_annee_selectionnee):
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    paiements = Paiement.objects.filter(annee_universitaire=annee_universitaire)
    context = {
        'annee_universitaire': annee_universitaire,
        'paiements': paiements,
    }
    return render(request, 'paiements/liste_paiements.html', context)


@login_required(login_url=settings.LOGIN_URL)
def enregistrer_paiement(request, id=0):
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

    # Calcul du montant total pour l'étudiant
    montant_verse = paiements.filter(etudiant=etudiant).aggregate(Sum('montant'))['montant__sum'] or 0
    total_frais_courante = frais_etudiant.montant_inscription + frais_etudiant.montant_scolarite if frais_etudiant else 0
    
    # Calcul des arriérés pour l'étudiant
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
    }
    return render(request, 'compte_bancaire/compte_bancaire.html', context)


@login_required(login_url=settings.LOGIN_URL)
def etat_compte_bancaire(request, id_annee_selectionnee, compte_bancaire_id):
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

    return render(request, 'bilan/bilan.html', context)


#Méthode affichant le bilan annuel des paiements des frais scolaires
@login_required(login_url=settings.LOGIN_URL)
def bilan_paiements_annuel(request, id_annee_selectionnee):
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
            bulletin.compte_bancaire = compte_universite
            bulletin.save()
            taxes_cnss = Decimal(bulletin.frais_prestations_familiale_salsalaire) * Decimal(bulletin.personnel.salaireBrut) + Decimal(bulletin.frais_prestations_familiales) * Decimal(bulletin.personnel.salaireBrut) + Decimal(bulletin.frais_risques_professionnel) * Decimal(bulletin.personnel.salaireBrut) + Decimal(bulletin.frais_pension_vieillesse_emsalaire) * Decimal(bulletin.personnel.salaireBrut) 
            deductions = taxes_cnss + bulletin.tcs
            montant_a_prelever = bulletin.salaire_net_a_payer + deductions 
           # print(montant_a_prelever)
            compte_universite.solde_bancaire -= montant_a_prelever
            compte_universite.save()
            
            id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
            return redirect('paiement:bulletins_de_paye', id_annee_selectionnee=id_annee_selectionnee)
        else:
            print(form.errors)
            return render(request, 'salaires/enregistrer_bulletin.html', {'form': form})



def detail_bulletin(request, id):
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
    salaire_net = Salaire_brut - retenues_cnss_personnel

    ## pour l'employeur
    frais_prestations_familiales = bulletin.frais_prestations_familiales * bulletin.personnel.salaireBrut
    frais_risques_professionnel = bulletin.frais_risques_professionnel * bulletin.personnel.salaireBrut
    frais_pension_vieillesse_emsalaire = bulletin.frais_pension_vieillesse_emsalaire * bulletin.personnel.salaireBrut
    retenues_cnss_employeur = frais_prestations_familiales + frais_risques_professionnel + frais_pension_vieillesse_emsalaire

    context = {
        'bulletin' : bulletin,
        'Salaire_brut': Salaire_brut,
        'salaire_net' : salaire_net,
        'total_primes' : total_primes,
        'retenues_cnss_employeur' : retenues_cnss_employeur,
        'frais_risques_professionnel' : frais_risques_professionnel,
        'frais_prestations_familiales' : frais_prestations_familiales,
        'frais_pension_vieillesse_emsalaire' : frais_pension_vieillesse_emsalaire,
        'frais_prestations_familiale_salsalaire' : frais_prestations_familiale_salsalaire,
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
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    paiements_fournisseurs = Fournisseur.objects.filter(annee_universitaire=annee_universitaire)
    context = {
        'annee_universitaire': annee_universitaire,
        'paiements_fournisseurs': paiements_fournisseurs,
    }
    return render(request, 'fournisseurs/liste_paiements_fournisseurs.html', context)



@login_required(login_url=settings.LOGIN_URL)
def enregistrer_paiement_fournisseur(request, id=0):
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
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    fiches = FicheDePaie.objects.filter(annee_universitaire=annee_universitaire)
    context = {
        'annee_universitaire': annee_universitaire,
        'fiches': fiches,
    }
    return render(request, 'fichePaies/fiche_de_paie_list.html', context)


@login_required(login_url=settings.LOGIN_URL)
def enregistrer_fiche_de_paie(request, id=0):
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
            dateDebut = fiche_de_paie.dateDebut
            dateFin = fiche_de_paie.dateFin

            # Vérification de la validité des dates
            if dateDebut and dateFin and dateDebut > dateFin:
                form.add_error('dateFin', "La date de fin ne peut pas être antérieure à la date de début.")
                return render(request, 'fichePaies/create_fiche_de_paie.html', {'form': form})
            
            compte_universite = CompteBancaire.objects.first()
            fiche_de_paie.compte_bancaire = compte_universite
            fiche_de_paie.save()

            compte_universite.solde_bancaire -= fiche_de_paie.montant 
            compte_universite.save()

            id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
            return redirect('paiement:liste_fiches_de_paie', id_annee_selectionnee=id_annee_selectionnee)                                          
        else:
            return render(request, 'fichePaies/create_fiche_de_paie.html', {'form': form})




@login_required(login_url=settings.LOGIN_URL)
def fiche_paie(request, id):
    fiche_paie = get_object_or_404(FicheDePaie, id=id)
    
    context = {
        'fiche_paie': fiche_paie,
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
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    fiches = Charge.objects.filter(annee_universitaire=annee_universitaire)
    context = {
        'annee_universitaire': annee_universitaire,
        'fiches': fiches,
    }
    return render(request, 'charges/liste_fiches_de_prise_en_charge.html', context)



@login_required(login_url=settings.LOGIN_URL)
def enregistrer_fiche_de_prise_en_charge(request, id=0):
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
            fiche_de_charge.compte_bancaire = compte_universite
            fiche_de_charge.save()

            compte_universite.solde_bancaire -= fiche_de_charge.montant 
            compte_universite.save()

            id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
            return redirect('paiement:liste_fiches_de_prise_en_charge', id_annee_selectionnee=id_annee_selectionnee)                                          
        else:
            return render(request, 'charges/create_fiche_de_prise_en_charge.html', {'form': form})


@login_required(login_url=settings.LOGIN_URL)
def fiche_de_charge(request, id):
    fiche_de_charge = get_object_or_404(Charge, id=id)
    
    context = {
        'fiche_de_charge': fiche_de_charge,
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