import datetime
import json
from django import forms
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from main.pdfMaker import generate_pdf
from django.conf import settings
from main.forms import EnseignantForm, EtudiantForm, EvaluationForm, InformationForm, PersonnelForm, ProgrammeForm, NoteForm, TuteurForm, UeForm, MatiereForm
from scripts.mail_utils import send_email_task
from scripts.utils import export_evaluation_data, load_notes_from_evaluation, pre_load_evaluation_template_data
from .models import Domaine, Enseignant, Evaluation, Personnel, Information, Matiere, Etudiant, Competence, Note, Parcours, Programme, Semestre, Ue, AnneeUniversitaire, Tuteur, Utilisateur
from cahier_de_texte.models import Seance
from planning.models import Planning, SeancePlannifier

from django.shortcuts import get_object_or_404, redirect, render
from main.helpers import *
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import Group
from .resources import EtudiantResource, EnseignantResource
from tablib import Dataset
from .custom_permission_required import evaluation_permission, evaluation_upload_permission, show_recapitulatif_note_permission
from django.contrib import messages
from django.core.cache import cache
from django.core import serializers
from django.core.mail import send_mail
from django.conf import settings
from openpyxl import Workbook

def datetime_serializer(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')
    raise TypeError("Type not serializable")

@login_required(login_url=settings.LOGIN_URL)
def export_excel_evaluation(request, id_matiere, id_semestre):
   
    matiere = get_object_or_404(Matiere, id=id_matiere)
    semestre = get_object_or_404(Semestre, id=id_semestre)
    
    print("semestre",semestre)
    print("mat",matiere)
    #print(evaluations)
    #return HttpResponse("ook")
    
    path=export_evaluation_data(matiere, semestre)
    file_name = path

    with open(file_name, 'rb') as file:
        response = HttpResponse(
            file.read(), content_type="application/force-download")
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(file_name))
        return response
    
@login_required(login_url=settings.LOGIN_URL)
def dashboard(request):
    """
        Vue permettant d'aller sur le tableau de bord

        :param request: L'objet de requête Django.
        :return: Une réponse HTTP avec le tableau de bord et les informations associées.
    """
    #return render(request, 'index.html')

    id_annee_selectionnee = request.session.get('id_annee_selectionnee')
    annee_selectionnee = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)
    semestres = annee_selectionnee.get_semestres()
    if request.user.groups.all().first().name in ['directeur_des_etudes', 'comptable', 'secretaire']:
        tous_les_etudiants = Etudiant.objects.all()
        etudiants = tous_les_etudiants.filter(semestres__in=semestres).distinct()

        tous_les_enseignants = Enseignant.objects.all()
        enseignants = tous_les_enseignants.filter(matiere__ue__programme__semestre__in=semestres).distinct()

        toutes_les_matieres = Matiere.objects.all()
        matieres = toutes_les_matieres.filter(ue__programme__semestre__in=semestres).distinct()

        toutes_les_ues = Ue.objects.all()
        ues = toutes_les_ues.filter(programme__semestre__in=semestres).distinct()
        ues_non_utilise = toutes_les_ues.filter(programme=None)

        data = {
            'nb_etudiants': etudiants.count(),
            'nb_enseignants': enseignants.count(),
            'nb_matieres': matieres.count(),
            'nb_ues': ues.count(),
            'ues_non_utilise': ues_non_utilise,
            'nb_ues_non_utilise': ues_non_utilise.count(),
        }

        return render(request, 'dashboard.html', context=data)

    elif request.user.groups.all().first().name == 'etudiant':
        etudiant = get_object_or_404(Etudiant, user=request.user)
        semestres = etudiant.semestres.filter(
            annee_universitaire=annee_selectionnee)
        event_data = []
        for semestre in semestres:
            planning = Planning.objects.filter(semestre=semestre)

            for plan in planning:
                seances = SeancePlannifier.objects.filter(planning=plan)
                event_data = [{'title': seance.intitule, 'start': seance.date_heure_debut,
                               'end': seance.date_heure_fin, 'url': '/planning/seance/' + str(seance.id) + ''} for seance in seances]
                event_data = json.dumps(
                    event_data, default=datetime_serializer)

        context = {'event_data': event_data}
        return render(request, 'dashboard.html', context)

    elif request.user.groups.all().first().name == 'enseignant':

        enseignant = Enseignant.objects.filter(personnel__user=request.user).get()
        seances = SeancePlannifier.objects.filter(professeur=enseignant)
        event_data = [{'title': seance.intitule, 'start': seance.date_heure_debut,
                       'end': seance.date_heure_fin, 'url': '/planning/seance/' + str(seance.id) + ''} for seance in seances]
        event_data = json.dumps(event_data, default=datetime_serializer)
        context = {'event_data': event_data}
        #return HttpResponse("Hello")
        return render(request, 'dashboard.html', context=context)


def change_annee_universitaire(request):
    """
        Vue permettant de changer l'année scolaire

        :param request: L'objet de requête Django.
        :return: Une redirection HTTP sur l'URL précédente avec l'année scolaire selectionnée .
    """

    if request.POST:
        id_annee_universitaire = request.POST.get('annee_universitaire')
        request.session["id_annee_selectionnee"] = id_annee_universitaire
        new_origin_path = request.POST.get('origin_path')
        return redirect(new_origin_path)


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.view_etudiant")
def etudiants(request):
    """
    Affiche la liste des étudiants en fonction des filtres de semestre et d'état sélectionnés.

    :param request: L'objet de requête Django.
    :return: Une réponse HTTP avec la liste des étudiants et des informations associées.
    """

    # Récupérer l'identifiant de l'année universitaire sélectionnée à partir de la session
    id_annee_selectionnee = request.session.get("id_annee_selectionnee")

    # Récupérer le rôle de l'utilisateur
    role = get_user_role(request)

    # Récupérer l'objet AnneeUniversitaire en fonction de l'identifiant fourni
    annee_universitaire = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)

    # Initialiser des variables
    data = {}
    etats = [{'id': 1, 'value': 'Actif'}, {'id': 0, 'value': 'Suspendue'}]
    etats_selected = [True, False]
    etat_id = "__all__"
    semestres = annee_universitaire.semestre_set.all()
    semestres_selected = semestres
    semestre_id = "__all__"
    niveau = ""

    # Traitement des filtres de semestre
    if 'semestre' in request.POST:
        semestre_id = request.POST.get('semestre')
        if semestre_id != "" and semestre_id != "__all__":
            semestres_selected = semestres.filter(pk=semestre_id)
            niveau = AnneeUniversitaire.getNiveau(
                semestres_selected[0].libelle)

    # Traitement des filtres d'état
    if 'etat' in request.POST:
        etat_id = request.POST.get('etat')
        if etat_id != "" and etat_id != "__all__":
            etat_id = int(etat_id)
            etats_selected = [bool(etat_id)]

    # Logique pour filtrer les étudiants en fonction du rôle de l'utilisateur
    if role:
        if role.name in ["etudiant", "enseignant"]:
            niveau = "Mes camarades"
            if role.name == "enseignant":
                niveau = "Nos Étudiants"

        elif role.name in ["directeur_des_etudes", "secretaire", "comptable"]:
            niveau = "Nos Étudiants"

        elif role.name == "comptable":
            niveau = "Nos Étudiants"

        etudiants = Etudiant.objects.filter(
            is_active__in=etats_selected, semestres__in=semestres_selected).distinct()

    # Gérer les erreurs si aucun semestre n'est sélectionné
    try:
        semestres_selected = semestres_selected.get()
    except:
        semestres_selected = semestres.first()

    etats_selected = {'id': etat_id}

    # Construire une liste temporaire d'étudiants avec des informations de niveau
    temp_etudiants = []
    for etudiant in etudiants:
        temp_etudiants.append({'etudiant': etudiant, 'niveau': etudiant.get_niveau_annee(
            annee_universitaire=annee_universitaire)[0]})

    # Construire le contexte pour le rendu de la page
    data = {
        'etudiants': temp_etudiants,
        'semestres': semestres,
        'niveau': niveau,
        'selected_semestre': semestres_selected,
        'etats': etats,
        'selected_etat': etats_selected
    }

    # Rendre la page avec le contexte
    return render(request, 'etudiants/etudiants.html', context=data)


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.change_etudiant")
def etudiants_suspendu(request):
    """
    Affiche la liste des étudiants suspendus pour l'année universitaire courante.

    :param request: L'objet de requête Django.
    :return: Une réponse HTTP avec la liste des étudiants suspendus.
    """

    # Obtenez l'année universitaire courante
    annee_courante = AnneeUniversitaire.static_get_current_annee_universitaire()

    if annee_courante != "-":
        # Obtenez la liste des étudiants suspendus pour l'année universitaire courante
        etudiants = Etudiant.objects.filter(
            semestres__annee_universitaire=annee_courante, is_active=False)
    else:
        # Si l'année universitaire courante n'est pas définie, initialisez la liste des étudiants comme vide
        etudiants = []

    # Contexte pour le rendu de la page
    context = {
        'etudiants': etudiants,
        'annee_courante': annee_courante,
    }

    # Rendre le modèle avec le contexte
    return render(request, 'etudiants/etudiants_suspendu.html', context)


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.view_etudiant")
def detailEtudiant(request, id):
    """
    Affiche le détail d'un étudiant en fonction de son identifiant.

    :param request: L'objet de requête Django.
    :param id: L'identifiant unique de l'étudiant.
    :return: Une réponse HTTP avec les détails de l'étudiant.
    :raises Http404: Renvoie une erreur 404 si l'étudiant avec l'identifiant spécifié n'est pas trouvé.
    """

    # Récupérer l'objet étudiant en fonction de son identifiant
    etudiant = get_object_or_404(Etudiant, id=id)

    # Contexte pour le rendu de la page
    context = {"etudiant": etudiant}

    # Rendre le modèle avec le contexte
    return render(request, "etudiants/detailEtudiant.html", context)


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.add_etudiant")
def create_etudiant(request, id=0):
    """
    Affiche le formulaire de création ou de modification d'un étudiant.

    :param request: L'objet de requête Django.
    :param id: L'identifiant de l'étudiant à modifier. Par défaut, 0 indique la création d'un nouvel étudiant.
    :return: Une réponse HTTP redirigeant vers la liste des étudiants après création ou modification réussie.
    """

    if request.method == "GET":
        # Gestion de la requête GET
        if id == 0:
            # Création d'un nouveau formulaire pour un nouvel étudiant
            form = EtudiantForm()
        else:
            # Modification d'un étudiant existant, préremplir le formulaire avec les données existantes
            etudiant = Etudiant.objects.get(pk=id)
            form = EtudiantForm(instance=etudiant)
            print(form.initial['datenaissance'])
        return render(request, 'etudiants/create_etudiant.html', {'form': form})
    else:
        # Gestion de la requête POST
        if id == 0:
            # Création d'un nouvel étudiant à partir des données POST
            form = EtudiantForm(request.POST, request.FILES)
        else:
            # Modification d'un étudiant existant avec les données POST
            etudiant = Etudiant.objects.get(pk=id)
            form = EtudiantForm(request.POST, request.FILES, instance=etudiant)

        if form.is_valid():
            # Sauvegarde de l'étudiant pour générer un ID
            etudiant = form.save()
            semestres = form.cleaned_data.get("semestres")
            etudiant.semestres.set(semestres)
            
            #return HttpResponse("Hello")
            # Rediriger vers la liste des étudiants après création ou modification réussie
            return redirect('main:etudiants')
        else:
            # Le formulaire n'est pas valide, réafficher le formulaire avec les erreurs
            return render(request, 'etudiants/create_etudiant.html', {'form': form})

@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.view_etudiant")
def liste_etudiants_par_semestre(request, id_annee_selectionnee):
    """
    Affiche la liste des étudiants pour un semestre sélectionné dans une année universitaire donnée.

    :param request: L'objet de requête Django.
    :param id_annee_selectionnee: L'identifiant de l'année universitaire sélectionnée.
    :return: Une réponse HTTP avec la liste des étudiants et des informations associées.
    """

    # Récupérer le rôle de l'utilisateur
    role = get_user_role(request)

    # Récupérer l'objet AnneeUniversitaire en fonction de l'identifiant fourni
    annee_universitaire = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)

    # Récupérer l'année universitaire actuelle
    current_annee = AnneeUniversitaire.static_get_current_annee_universitaire()
    print("annee c",current_annee)

    # Initialiser des variables
    niveau = ""
    data = {}
    semestre_id = None
    semestres_selected = None

    # Logique pour les directeurs des études
    if role.name == "directeur_des_etudes":
        niveau = "IFNTI"
        semestres = annee_universitaire.semestre_set.all()
        semestres_selected = semestres

    # Vérifier si un semestre est spécifié dans la requête
    if 'semestre' in request.GET:
        semestre_id = request.GET.get('semestre')
        print(semestre_id)
        semestres_selected = semestres.filter(pk=semestre_id)
    
    try:
        programme = Programme.objects.get(semestre=semestres_selected[0])
        print("program",programme)

        # Filtrer les étudiants en fonction des semestres sélectionnés et qui sont actifs
        etudiants = Etudiant.objects.filter(
            semestres__in=semestres_selected, is_active=True).distinct()

        # Initialiser une liste pour les étudiants insuffisants
        etudiants_insuffisants = []
        print("---------------------------------------------------")
       

        # Récupérer le semestre actuel de chaque étudiant dans l'année universitaire
        for etudiant in etudiants:
            semestres_etudiant = etudiant.semestres.filter(annee_universitaire=annee_universitaire, courant=True)
            
            if semestres_etudiant.exists():
                semestre_actuel = semestres_etudiant.first()
                print("semestre actuel",semestre_actuel)
                credits_obtenus = etudiant.credits_obtenus_semestre(semestre=semestre_actuel)
                print(etudiant, " : ", credits_obtenus)
                etudiant.credits_obtenus = credits_obtenus
                etudiant.semestre_actuel = semestre_actuel
            else:
                etudiant.semestre_actuel = None
    except Exception as e:
        print(e)
        etudiants=[]
        etudiants_insuffisants=[]
    # Construire le contexte pour le rendu de la page
    data = {
        'etudiants': etudiants,
        'semestres': semestres,
        'etudiants_insuffisants': etudiants_insuffisants,
        'niveau': niveau,
        'selected_semestre': semestres_selected
    }

    # Rendre la page avec le contexte
    return render(request, 'etudiants/liste_etudiants_par_semestre.html', context=data)

@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.change_etudiant")
# Vue permettant le passage des étudiants au semestre suivant dans l'année universitaire courante
def passage_etudiants(request):
    """
    Gère le passage des étudiants au semestre suivant en fonction des décisions du conseil.

    :param request: L'objet de requête Django.
    :return: Une réponse HTTP redirigeant vers la liste des étudiants après le passage de semestre.
    """

    # Mapping des semestres, indiquant le semestre suivant pour chaque semestre actuel
    semestre_mapping = {
        'S1': 'S2',
        'S2': 'S3',
        'S3': 'S4',
        'S4': 'S5',
        'S5': 'S6',
    }

    if request.method == 'POST':
        annee_univ_courante = AnneeUniversitaire.objects.get(
            annee_courante=True)
        etudiant_ids = request.POST.getlist('passer_semestre_suivant')

        # Itération sur les étudiants sélectionnés pour le passage au semestre suivant
        for etudiant_id in etudiant_ids:
            etudiant = Etudiant.objects.get(id=etudiant_id)

            # Mettre à jour l'attribut passer_semestre_suivant à False
            etudiant.passer_semestre_suivant = False
            etudiant.save()

            semestres_deja_inscrits = etudiant.semestres.filter(
                annee_universitaire=annee_univ_courante).count()
            semestre_actuel = etudiant.semestres.filter(
                annee_universitaire=annee_univ_courante).first()
            credits_obtenus = etudiant.credits_obtenus_semestre(
                semestre_actuel)

            # Vérifier le nombre de semestres déjà inscrits ainsi que le nombre de crédits obtenus
            if semestres_deja_inscrits >= 2:
                return render(request, 'etudiants/message_erreur.html', {'message': "Impossible de passer dans plus de deux semestres différents au cours d'une même année universitaire."})

            elif credits_obtenus == 0:
                return render(request, 'etudiants/message_erreur.html', {'message': "L'étudiant ne peut pas passer au semestre suivant avec 0 crédit."})

            # Récupérer la décision du conseil
            decision_conseil = request.POST.get(
                'decision_conseil_' + etudiant_id)
            etudiant.decision_conseil = decision_conseil
            etudiant.passer_semestre_suivant = True
            etudiant.save()

            # Ajouter l'étudiant au semestre suivant
            semestres = etudiant.semestres.filter(
                annee_universitaire=annee_univ_courante)
            for semestre in semestres:
                if semestre.libelle in semestre_mapping:
                    semestre_suivant = Semestre.objects.get(
                        libelle=semestre_mapping[semestre.libelle], annee_universitaire=annee_univ_courante)
                    etudiant.semestres.add(semestre_suivant)
                    etudiant.semestres.add(semestre)

            # Mettre à jour l'attribut passer_semestre_suivant à False
            etudiant.passer_semestre_suivant = False
            etudiant.save()

        if etudiant_ids:
            etudiant_test = Etudiant.objects.get(id=etudiant_ids[0])
            semestre_actuel = etudiant_test.semestres.first().libelle
            semestre_suivant_test = semestre_mapping.get(semestre_actuel, None)
        else:
            semestre_suivant_test = None

        return redirect('main:etudiants')

    return render(request, 'etudiants/liste_etudiants_par_semestre.html')


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.view_tuteur")
def tuteurs(request):
    """
    Affiche la liste de tous les tuteurs associés aux étudiants de l'année universitaire courante.

    :param request: L'objet de requête Django.
    :return: Une réponse HTTP avec la liste des tuteurs et des informations associées.
    """

    # Obtenez l'année universitaire courante
    annee_courante = AnneeUniversitaire.static_get_current_annee_universitaire()

    # Vérifiez si une année universitaire courante est définie
    if annee_courante != "-":
        # Obtenez tous les tuteurs associés aux étudiants de l'année universitaire courante
        tuteurs = Tuteur.objects.all()
    else:
        # Gérer le cas où aucune année universitaire courante n'est définie
        tuteurs = []

    # Construire le contexte pour le rendu de la page
    context = {
        'tuteurs': tuteurs,
    }

    # Rendre la page avec le contexte
    return render(request, 'tuteurs/tuteurs.html', context)


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.view_tuteur")
def detailTuteur(request, id):
    """
    Affiche les détails d'un tuteur spécifié par son identifiant.

    :param request: L'objet de requête Django.
    :param id: L'identifiant du tuteur dont les détails doivent être affichés.
    :return: Une réponse HTTP avec les détails du tuteur.
    """

    # Récupérer l'objet Tuteur en fonction de l'identifiant fourni
    tuteur = get_object_or_404(Tuteur, id=id)

    # Construire le contexte pour le rendu de la page
    context = {"tuteur": tuteur}

    # Rendre la page avec le contexte
    return render(request, "tuteurs/detailTuteur.html", context)


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.add_tuteur")
def create_tuteur(request, id=0):
    """
    Affiche un formulaire pour créer ou modifier un tuteur et enregistre les données du formulaire.

    :param request: L'objet de requête Django.
    :param id: L'identifiant du tuteur à modifier. Par défaut, id=0 indique la création d'un nouveau tuteur.
    :return: Une réponse HTTP redirigeant vers la liste des tuteurs après la création ou la modification.
    """

    # Vérifier la méthode de la requête (GET ou POST)
    if request.method == "GET":
        # Afficher le formulaire pour la création ou la modification d'un tuteur
        if id == 0:
            form = TuteurForm()
        else:
            tuteur = Tuteur.objects.get(pk=id)
            form = TuteurForm(instance=tuteur)
        return render(request, 'tuteurs/create_tuteur.html', {'form': form})
    else:
        # Traitement des données du formulaire lorsqu'une requête POST est reçue
        if id == 0:
            # Créer un nouveau tuteur
            form = TuteurForm(request.POST)
        else:
            # Modifier un tuteur existant
            tuteur = Tuteur.objects.get(pk=id)
            form = TuteurForm(request.POST, instance=tuteur)

        # Vérifier si le formulaire est valide
        if form.is_valid():
            # Enregistrer les données du formulaire dans la base de données
            form.save()
            # Rediriger vers la liste des tuteurs après la création ou la modification
            return redirect('main:liste_des_tuteurs')


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.view_matiere")
def matieres(request):
    """
    Retourne une page html contenant l'ensemble des matières 

    :param request: L'objet de requête Django.
    :return: Une réponse HTTP redirigeant vers la liste des tuteurs après la création ou la modification.
    """

    id_annee_selectionnee = request.session.get("id_annee_selectionnee")
    annee_universitaire = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)
    niveau = "IFNTI"
    semestres = annee_universitaire.semestre_set.all()
    semestres_selected = semestres
    ue_id = "-1"

    if request.method == "POST":
        semestre_id = request.POST.get('semestre')
        ue_id = request.POST.get('ue')
        if semestre_id != "":
            semestres_selected = semestres.filter(pk=semestre_id)

    programme = semestres_selected[0].programme_set.first()

    if programme:
        ues = programme.ues.all().prefetch_related('matiere_set')
    else:
        ues = []

    matieres = set()
    matieres_ids = ""
    if ue_id == "-1":
        for ue in ues:
            _matieres = ue.matiere_set.all()
            for matiere in _matieres:
                matieres_ids += f"{matiere.id};"
                matiere.nb_evaluations = matiere.count_evaluations(
                    annee_universitaire, semestres_selected)
            matieres.update(_matieres)
        ue = None
        request.session['matieres'] = matieres_ids
    else:
        ue = ues.filter(id=ue_id).first()
        if ue:
            matieres = ue.matiere_set.all()
            for matiere in matieres:
                matiere.nb_evaluations = matiere.count_evaluations(
                    annee_universitaire, semestres_selected)
    try:
        semestres_selected = semestres_selected.get()
    except:
        semestres_selected = semestres_selected[0]

    try:
        selected_ue = ue.id
    except:
        selected_ue = ue_id

    data = {
        'matieres': matieres,
        'semestres': semestres,
        'ues': ues,
        'niveau': niveau,
        'selected_semestre': semestres_selected,
        'selected_ue': selected_ue,
    }

    return render(request, 'matieres/matieres.html', context=data)


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.view_matiere")
def detailMatiere(request, id):
    """
    Retourne une page html donnant les détails d'une matière 

    :param request: L'objet de requête Django.
    :param id: L'identifiant de la matière.
    :return: Une réponse HTTP redirigeant vers la matière.
    """
    matiere = get_object_or_404(Matiere, id=id)
    seances = Seance.objects.filter(matiere=matiere)
    heures = 0
    for seance in seances:
        heure = seance.date_et_heure_fin - seance.date_et_heure_debut
        heures += heure.total_seconds()/3600

    return render(request, "matieres/detailMatiere.html", {"matiere": matiere, "heures": heures})


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.add_matiere")
def create_matiere(request, id=0):
    """
    Retourne une page html permettant de créer ou modifier une matière 

    :param request: L'objet de requête Django.
    :param id: L'identifiant de la matière. Par défaut, id=0 indique la création d'une nouvelle matière.

    :return: Une réponse HTTP redirigeant vers le formulaire de crétion ou de modification d'une matière.
    """
    id_annee_selectionnee = request.session.get('id_annee_selectionnee')
    annee_universitaire = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)
    ues = Ue.objects.filter(
        programme__semestre__annee_universitaire=annee_universitaire)
    if request.method == "GET":
        if id == 0:
            form = MatiereForm()
            form.set_ue(ues)
        else:
            matiere = Matiere.objects.get(pk=id)
            form = MatiereForm(instance=matiere)
            form.set_ue(ues)
        print(Enseignant.objects.all())
        return render(request, 'matieres/create_matiere.html', {'form': form})
    else:
        if id == 0:
            form = MatiereForm(request.POST)
            form.set_ue(ues)
            message = "a été ajouté"
        else:
            matiere = Matiere.objects.get(pk=id)
            form = MatiereForm(request.POST, instance=matiere)
            form.set_ue(ues)
            message = "a été mis a jour"
        if form.is_valid():
            matiere = form.save()
            messages.success(
                request, f"La matière {matiere.libelle} {message} !")
            return redirect('main:matieres_etudiant')
        return render(request, 'matieres/create_matiere.html', {'form': form})

@permission_required("main.delete_matiere")
def delete_matiere(request, id_matiere):
    matiere = get_object_or_404(Matiere, pk=id_matiere)
    messages.success(
        request, f"La matière {matiere.libelle} a été supprimer !")
    matiere.delete()
    return redirect('main:matieres_etudiant')


def ues(request):
    """
    Retourne une page html affichant l'ensemble des UEs d'un utilisateur en fonction de son rôle et du semestre selectioné s'il existe. 

    :param request: L'objet de requête Django.


    :return: Une réponse HTTP redirigeant vers l'ensemble des UEs.
    """
    role = get_user_role(request)
    id_annee_selectionnee = request.session.get("id_annee_selectionnee")
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    semestres = annee_universitaire.semestre_set.all()
    semestres_selected = semestres

    if role.name == "etudiant":
        titre_section = "Mes Ues"
    elif role.name == "enseignant" or role.name == "directeur_des_etudes" or role.name == "secretaire":
        titre_section = "Nos Ues"

    if 'semestre' in request.GET and request.GET.get('semestre') != "":
        semestre_id = request.GET.get('semestre')
        semestres_selected = semestres.filter(pk=semestre_id)
        ues = Ue.objects.filter(programme__semestre__in=semestres_selected)
    else:
        ues = Ue.objects.filter(semestre__annee_universitaire=annee_universitaire)


    if len(semestres_selected) == 1:
        semestres_selected = semestres_selected.get()

    data = {
        'ues': ues,
        'semestres': semestres,
        'titre_section': titre_section,
        'selected_semestre': semestres_selected,
    }
    return render(request, 'ues/ues.html', context=data)



@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.view_ue")
def detailUe(request, id):
    """
    Affiche les détails d'une Unité d'Enseignement (UE) spécifiée par son identifiant.

    :param request: L'objet de requête Django.
    :param id: L'identifiant de l'UE dont les détails doivent être affichés.
    :return: Une réponse HTTP avec les détails de l'UE.
    """

    # Récupérer l'objet UE en fonction de l'identifiant fourni
    ue = get_object_or_404(Ue, id=id)

    # Construire le contexte pour le rendu de la page
    context = {"ue": ue}

    # Rendre la page avec les détails de l'UE
    return render(request, "ues/detailUe.html", context)


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.add_ue")
def create_ue(request, id=0):
    """
    Affiche un formulaire pour créer ou modifier une Unité d'Enseignement (UE) et enregistre les données du formulaire.

    :param request: L'objet de requête Django.
    :param id: L'identifiant de l'UE à modifier. Par défaut, id=0 indique la création d'une nouvelle UE.
    :return: Une réponse HTTP avec un message d'erreur ou le formulaire pour créer ou modifier une UE.
    """

    id_annee_selectionnee = request.session["id_annee_selectionnee"]
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)

    # Vérifier la méthode de la requête (GET ou POST)
    if request.method == "GET":
        # Afficher le formulaire pour la création ou la modification d'une UE
        if id == 0:
            form = UeForm()
        else:
            ue = Ue.objects.get(pk=id)
            form = UeForm(instance=ue)
            
        form.fields['semestre'].queryset = Semestre.objects.filter(annee_universitaire=annee_universitaire)
        return render(request, 'ues/create_ue.html', {'form': form})
    else:
        # Traitement des données du formulaire lorsqu'une requête POST est reçue
        if id == 0:
            # Créer une nouvelle UE
            form = UeForm(request.POST)
            message = "bien ajouter Veuillez le rattacher à un programme."
        else:
            # Modifier une UE existante
            ue = Ue.objects.get(pk=id)
            message = "bien mise à jour"
            form = UeForm(request.POST, instance=ue)

        # Vérifier si le formulaire est valide
        if form.is_valid():
            # Enregistrer les données du formulaire dans la base de données
            ue = form.save(commit=False)
            #ue.annee_universitaire = annee_universitaire
            ue.save()
            #print(ue.annee_universitaire)
            # Afficher un message d'erreur spécifique pour inciter à attacher l'UE à la gestion maquette
            messages.success(request, f"La matière {ue.libelle} {message} !")
            return redirect('main:ues')
        else:
            print(form.errors)
            return render(request, 'ues/create_ue.html', {'form': form})




"""
    Pour la génération des documents pdf, la méthode generate_pdf 
    permet de générer tout type de document et prend en paramètre:
        * le contexte
        * le nom du fichier latex servant de template
        * le nom du fichier latex qui sera généré en sortie
        * le nom du fichier pdf qui sera généré en sortie
        ( pour les fichiers ne pas mentionner l'extension )
"""

@login_required(login_url=settings.LOGIN_URL)
# methode générant la carte de l'étudiant
def carte_etudiant(request, id, niveau):
    from projet_ifnti.settings import BASE_DIR

    """
    Permet de générer sous format pdf la carte étudiante d'un étudiant

    :param request: L'objet de requête Django.
    :param id: Identifiant de l'étudiant
    :param niveau: Le niveau de l'étudiant (L1, L2, L3)
    :type niveau: str

    :return: Une réponse HTTP affichant le pdf de la carte étudiante générée.
    """

    id_annee_selectionnee = request.session["id_annee_selectionnee"]
    annee_universitaire = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)

    if request.user.groups.all().first().name not in ['directeur_des_etudes', 'secretaire']:
        return render(request, 'errors_pages/403.html')

    etudiant = get_object_or_404(Etudiant, id=id)
    in_format = "%Y-%m-%d"
    out_format = "%d-%m-%Y"

    etudiant.datenaissance = etudiant.datenaissance if etudiant.datenaissance else ""
    etudiant.photo = "/".join(etudiant.photo_passport.__str__().split('/')[1:]) if etudiant.photo_passport and etudiant.photo_passport != "" else "photo_passports/default.png"
    etudiant.photo = os.path.join(BASE_DIR, 'media') + '/images/' + etudiant.photo

    context = {'etudiant': etudiant, 'niveau': niveau, 'annee': str(
        annee_universitaire.annee) + '-' + str(annee_universitaire.annee + 1)}

    latex_input = 'carte_etudiant'
    latex_ouput = 'generated_carte_etudiant'
    pdf_file = 'carte_etudiant_' + str(etudiant.id)
    


    # génération du pdf
    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    # visualisation du pdf dans le navigateur
    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        return response


@login_required(login_url=settings.LOGIN_URL)
# methode générant la carte des étudiants d'un niveau
@permission_required("main.delete_matiere")
def carte_etudiant_all(request, niveau):
    from projet_ifnti.settings import BASE_DIR
    """
    Génére les cartes étudiantes de tout les étudiants d'un niveau donné
    :param request: L'objet de requête Django.
    :param niveau: Le niveau des étudiants (L1, L2, L3).
    :type niveau: str

    :return: Une réponse HTTP affichant le pdf des cartes étudiantes générées.
    """
    if request.user.groups.all().first().name not in ['directeur_des_etudes', 'secretaire']:
        return render(request, 'errors_pages/403.html')

    id_annee_selectionnee = request.session["id_annee_selectionnee"]
    annee_universitaire = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)
    annee_suiv = int(annee_universitaire.annee) + 1

    semestre = Semestre.objects.filter(id=niveau)
    if semestre:
        semestres = [semestre.get().libelle]
    elif niveau == "__all__":
        semestres = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']

    etudiants = semestre.get().etudiant_set.all().order_by('nom', 'prenom')
    for etudiant in etudiants:
        etudiant.niveau, _ = etudiant.get_niveau_annee(annee_universitaire)
        in_format = "%Y-%m-%d"
        out_format = "%d-%m-%Y"

        # if etudiant.datenaissance:
        #     date_formatee = datetime.strptime(
        #         str(etudiant.datenaissance), in_format).strftime(out_format)
        # else:
        #     date_formatee = 'None'

        etudiant.datenaissance = etudiant.datenaissance if etudiant.datenaissance else ""
        etudiant.photo = "/".join(etudiant.photo_passport.__str__().split('/')[1:]) if etudiant.photo_passport and etudiant.photo_passport != "" else "photo_passports/default.png"
        etudiant.photo = os.path.join(BASE_DIR, 'media') + '/images/' + etudiant.photo
        print(etudiant.photo)
        #default.png
    #return HttpResponse("Hello")

    nbre_pages = len(etudiants) // 9

    # ajout des étudiants dans le dictionnaire
    context = {'etudiants': etudiants, 'annee': str(
        annee_universitaire.annee) + '-' + str(annee_universitaire.annee + 1), 'niveau': "niveau",  'nbre_pages': nbre_pages}

    for etudiant in etudiants:
        latex_input = 'carte_etudiant'
        latex_ouput = 'generated_carte_etudiant'
        pdf_file = 'carte_etudiant_' + str(etudiant.id)

        temp_context = {'etudiant': etudiant, 'niveau': niveau, 'annee': str(
            annee_universitaire.annee) + '-' + str(annee_suiv)}

        # génération du pdf
        generate_pdf(temp_context, latex_input, latex_ouput, pdf_file)

    latex_input = 'cartes_rassemblees'
    latex_ouput = 'generated_cartes_rassemblees'
    pdf_file = 'pdf_carte_etudiant_rassemblees'

    # génération du pdf
    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    # visualisation du pdf dans le navigateur
    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        return response
    
  
@login_required(login_url=settings.LOGIN_URL)
# methode générant le diplome de l'étudiant
def diplome_etudiant(request, id):
    """
    Génére le diplome d'un étudiant
    :param request: L'objet de requête Django.
    :param id: L'identifiant de l'étudiant.

    :return: Une réponse HTTP affichant le pdf du diplome étudiant généré.
    """

    if request.user.groups.all().first().name not in ['directeur_des_etudes']:
        return render(request, 'errors_pages/403.html')

    date_deliberation = datetime.now()
    date_deliberation = str(date_deliberation.day) + '-' + \
        str(date_deliberation.month) + '-' + str(date_deliberation.year)

    etudiant = get_object_or_404(Etudiant, id=id)
    in_format = "%Y-%m-%d"
    out_format = "%d-%m-%Y"

    if etudiant.datenaissance:
        date_formatee = datetime.strptime(
            str(etudiant.datenaissance), in_format).strftime(out_format)
    else:
        date_formatee = 'None'
    etudiant.datenaissance = date_formatee

    id_annee_selectionnee = request.session["id_annee_selectionnee"]
    annee_universitaire = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)

    context = {'etudiant': etudiant, 'annee': str(
        annee_universitaire.annee) + '-' + str(annee_universitaire.annee + 1), 'date_deliberation': date_deliberation}

    latex_input = 'diplome'
    latex_ouput = 'generated_diplome'
    pdf_file = 'pdf_diplome'

    # génération du pdf
    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    # visualisation du pdf dans le navigateur
    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        return response


@login_required(login_url=settings.LOGIN_URL)
# methode générant le diplome de l'étudiant
@permission_required("main.delete_matiere")
def diplome_etudiant_all(request):
    """
    Génére le diplome des étudiants de L3.
    :param request: L'objet de requête Django.

    :return: Une réponse HTTP affichant le pdf du diplomes étudiants générés.
    """
    if request.user.groups.all().first().name not in ['directeur_des_etudes', 'secretaire']:
        return render(request, 'errors_pages/403.html')

    semestres = Semestre.objects.filter(
        libelle="S5") | Semestre.objects.filter(libelle="S6")
    temp = []

    in_format = "%Y-%m-%d"
    out_format = "%d-%m-%Y"
    date_deliberation = datetime.now()
    date_deliberation = date_deliberation.day() + '-' + date_deliberation.month() + \
        '-' + date_deliberation.year()

    # récupération des étudiants de chaque semestres
    for semestre in semestres:
        for etudiant in semestre.etudiant_set.all():
            # ajout de tout les étudiant du semestre dans un tableau temporaire
            etudiant.niveau, _ = etudiant.get_niveau_annee(annee_universitaire)
            in_format = "%Y-%m-%d"
            out_format = "%d-%m-%Y"

            if etudiant.datenaissance:
                date_formatee = datetime.strptime(
                    str(etudiant.datenaissance), in_format).strftime(out_format)
            else:
                date_formatee = 'None'
            etudiant.datenaissance = date_formatee
            temp.append(etudiant)

    # ajout des étudiants dans le dictionnaire
    context = {'etudiants': temp, 'date_deliberation': date_deliberation}

    latex_input = 'diplome_all'
    latex_ouput = 'generated_diplome_all'
    pdf_file = 'pdf_diplome_all'

    # génération du pdf
    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    # visualisation du pdf dans le navigateur
    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        return response


@login_required(login_url=settings.LOGIN_URL)
# methode générant le certificat scolaire de l'étudiant
def certificat_scolaire(request, id, niveau):
    """
    Génére l'attestation de scolaritée d'un étudiant
    :param request: L'objet de requête Django.
    :param id: L'identifiant de l'étudiant.
    :param niveau: Le niveau de l'étudiant.

    :return: Une réponse HTTP affichant le pdf de l'attestation de scolarité de l'étudiant générée.
    """
    id_annee_selectionnee = request.session["id_annee_selectionnee"]
    annee_universitaire = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)

    if request.user.groups.all().first().name not in ['directeur_des_etudes', 'secretaire']:
        return render(request, 'errors_pages/403.html')

    etudiant = get_object_or_404(Etudiant, id=id)

    in_format = "%Y-%m-%d"
    out_format = "%d-%m-%Y"

    if etudiant.datenaissance:
        date_formatee = datetime.strptime(
            str(etudiant.datenaissance), in_format).strftime(out_format)
    else:
        date_formatee = 'None'

    context = {'etudiant': etudiant, 'niveau': niveau,
               'annee': annee_universitaire.annee, 'date_naissance': date_formatee}

    # nom des fichiers d'entrée et de sortie
    latex_input = 'template_certificat_scolarite'
    latex_ouput = 'generated_template_certificat_scolarite'
    pdf_file = 'pdf_template_certificat_scolarite'

    # génération du pdf
    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    # visualisation du pdf dans le navigateur
    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        return response
#---------------------------------------------------------------------------------------------------------------------------------

@login_required(login_url=settings.LOGIN_URL)
def attestation_scolarite(request, id, niveau):
    id_annee_selectionnee = request.session["id_annee_selectionnee"]
    annee_universitaire = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)

    if request.user.groups.all().first().name not in ['directeur_des_etudes', 'secretaire']:
        return render(request, 'errors_pages/403.html')

    etudiant = get_object_or_404(Etudiant, id=id)

    in_format = "%Y-%m-%d"
    out_format = "%d-%m-%Y"

    if etudiant.datenaissance:
        date_formatee = datetime.strptime(
            str(etudiant.datenaissance), in_format).strftime(out_format)
    else:
        date_formatee = 'None'

    context = {'etudiant': etudiant, 'niveau': niveau,
               'annee': annee_universitaire.annee, 'date_naissance': date_formatee}

    # nom des fichiers d'entrée et de sortie
    latex_input = 'template_attestation_scolarite'
    latex_ouput = 'generated_template_attestation_scolaire'
    pdf_file = 'pdf_template_attestation_scolaire'

    # génération du pdf
    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    # visualisation du pdf dans le navigateur
    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        return response
    
#---------------------------------------------------------------------------------------------------------------------------------
@login_required(login_url=settings.LOGIN_URL)
def attestation_diplome(request, id, niveau):
    id_annee_selectionnee = request.session["id_annee_selectionnee"]
    annee_universitaire = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)

    if request.user.groups.all().first().name not in ['directeur_des_etudes', 'secretaire']:
        return render(request, 'errors_pages/403.html')

    etudiant = get_object_or_404(Etudiant, id=id)

    in_format = "%Y-%m-%d"
    out_format = "%d-%m-%Y"

    if etudiant.datenaissance:
        date_formatee = datetime.strptime(
            str(etudiant.datenaissance), in_format).strftime(out_format)
    else:
        date_formatee = 'None'

    context = {'etudiant': etudiant, 'niveau': niveau,
               'annee': annee_universitaire.annee, 'date_naissance': date_formatee}

    # nom des fichiers d'entrée et de sortie
    latex_input = 'template_attestation_diplome'
    latex_ouput = 'generated_template_attestation_diplome'
    pdf_file = 'pdf_template_attestation_diplome'

    # génération du pdf
    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    # visualisation du pdf dans le navigateur
    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        return response
    
#-------------------------------------------------------------------------------------------------------------------------------------

@login_required(login_url=settings.LOGIN_URL)
# methode générant le relevé de notes de l'étudiant
def releve_notes(request, id_etudiant, id_semestre):
    """
    Génére le relevé de notes semestriel d'un étudiant
    :param request: L'objet de requête Django.
    :param id: L'identifiant de l'étudiant.
    :param id_semestre: L'identifiant du semestre.

    :return: Une réponse HTTP affichant le pdf du relevé de notes généré.
    """
    if request.user.groups.all().first().name not in ['directeur_des_etudes', 'secretaire', 'etudiant']:
        return render(request, 'errors_pages/403.html')

    etudiant = get_object_or_404(Etudiant, id=id_etudiant)
    semestre = get_object_or_404(Semestre, id=id_semestre)
    context = {}

    if request.user.groups.all().first().name == 'etudiant':
        if request.user.etudiant and request.user.etudiant != etudiant:
            return render(request, 'errors_pages/403.html')

    # récupération des ues du semestre
    semestre_ues = semestre.get_all_ues()
    ues = []
    avec_rattrapage = True
    for ue in semestre_ues:
        moyenne, validation, anneeValidation = etudiant.moyenne_etudiant_ue(
            ue, semestre, avec_rattrapage)
      
        matieres_libelles = ', '.join(ue.matiere_set.all().values_list('libelle', flat=True))
            
        ues.append({'ue': ue, 'moyenne': round(
            moyenne, 2), 'validation': validation, 'anneeValidation': anneeValidation, 'matieres_libelles': matieres_libelles})

    # calcul du nombre de crédits obtenus par l'étudiant
    credits_obtenus = 0
    for ue in ues:
        if ue['validation'] == True:
            credits_obtenus += ue['ue'].nbreCredits

    context['ues'] = ues
    context['credits_obtenus'] = credits_obtenus
    context['etudiant'] = etudiant
    context['semestre'] = semestre
    context['annee'] = semestre.annee_universitaire

    in_format = "%Y-%m-%d"
    out_format = "%d-%m-%Y"
    if etudiant.datenaissance:
        date_formatee = datetime.strptime(
            str(etudiant.datenaissance), in_format).strftime(out_format)
    else:
        date_formatee = 'None'
    context['date_naissance'] = date_formatee
    # if request.user.groups.all().first().name == 'directeur_des_etudes':
    #     context['directeur'] = request.user.utilisateur.nom + ' ' + request.user.prenom

    # nom des fichiers d'entrée et de sortie
    print("Hello Releve de notes")
    latex_input = 'releve_notes'
    latex_ouput = 'generated_releve_notes'
    pdf_file = 'pdf_releve_notes'

    # génération du pdf
    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    # visualisation du pdf dans le navigateur
    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        return response


@login_required(login_url=settings.LOGIN_URL)
# methode générant le relevé de notes des étudiants de tout un semestre
def releve_notes_semestre(request, id_semestre):
    """
    Génére les relevés de notes des étudiants du semestre
    :param request: L'objet de requête Django.
    :param id_semestre: L'identifiant du semestre.

    :return: Une réponse HTTP affichant le pdf des relevés de notes générés.
    """
    if request.user.groups.all().first().name not in ['directeur_des_etudes', 'secretaire']:
        return render(request, 'errors_pages/403.html')

    semestre = get_object_or_404(Semestre, id=id_semestre)
    etudiants = semestre.etudiant_set.filter(is_active=True).order_by('nom', 'prenom')

    # récupération des ues du semestre
    semestre_ues = semestre.get_all_ues()

    # tableau contenant l'ensemble des relevés de notes
    releves_notes_tab = []
    avec_rattrapage = True
    for etudiant in etudiants:
        # tableau contenant les données correspondant au relevé de notes d'un étudiant
        releve_note = {}
        releve_note['lignes'] = []
        credits_obtenus = 0
        for ue in semestre_ues:
            moyenne, validation, anneeValidation = etudiant.moyenne_etudiant_ue(
                ue, semestre, avec_rattrapage)
                        
            matieres_libelles = ', '.join(ue.matiere_set.all().values_list('libelle', flat=True))
                
            releve_note['lignes'].append(
                {'ue': ue, 'moyenne': round(
                    moyenne, 2), 'validation': validation, 'anneeValidation': anneeValidation, 'matieres_libelles': matieres_libelles}
            )

            # calcul de nombre de crédits obtenus
            if validation:
                credits_obtenus += ue.nbreCredits

        in_format = "%Y-%m-%d"
        out_format = "%d-%m-%Y"
        if etudiant.datenaissance:
            date_formatee = datetime.strptime(
                str(etudiant.datenaissance), in_format).strftime(out_format)
        else:
            date_formatee = 'None'

        releve_note['date_naissance'] = date_formatee
        releve_note['credits_obtenus'] = credits_obtenus
        releve_note['etudiant'] = etudiant
        releves_notes_tab.append(releve_note)

    context = {}

    context['annee'] = semestre.annee_universitaire
    context['releves_notes'] = releves_notes_tab
    context['semestre'] = semestre

    # nom des fichiers d'entrée et de sortie
    latex_input = 'releve_notes_semestre'
    latex_ouput = 'generated_releve_notes_semestre'
    pdf_file = 'pdf_releve_notes_semestre'

    # génération du pdf
    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    # visualisation du pdf dans le navigateur
    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        return response


@login_required(login_url=settings.LOGIN_URL)
# methode générant le relevé détaillé d'un étudiant
def releve_notes_detail(request, id_etudiant, id_semestre):
    """
    Génére le relevé de notes détaillé par matière d'un étudiant au cours d'un semestre.
    :param request: L'objet de requête Django.
    :param id: L'identifiant de l'étudiant.
    :param id_semestre: L'identifiant du semestre.

    :return: Une réponse HTTP affichant le pdf du relevé de notes généré.
    """
    if request.user.groups.all().first().name not in ['directeur_des_etudes', 'secretaire', 'etudiant']:
        return render(request, 'errors_pages/403.html')

    semestre = get_object_or_404(Semestre, id=id_semestre)
    etudiant = get_object_or_404(Etudiant, id=id_etudiant)

    if request.user.groups.all().first().name == 'etudiant':
        if request.user.etudiant and request.user.etudiant != etudiant:
            return render(request, 'errors_pages/403.html')

    nbre_colonnes = 2

    # variable contenant le nombre de colonnes

    colonnes = '|c|c|'

    semestre_ues = semestre.get_all_ues()

    colonnes += 'c|' * len(semestre_ues)

    nbre_colonnes += len(semestre_ues)

    nbre_ues = len(semestre_ues)

    # récupération du nombre de matières par ue
    data_releve = []
    for ue in semestre_ues:
        # ajout des colonnes correspondant aux matières
        nbre_matieres = len(ue.matiere_set.all())
        colonnes += 'c|' * nbre_matieres
        nbre_colonnes += nbre_matieres
        matieres = []
        for matiere in ue.matiere_set.all():
            # récupération des matières de l'ue et la moyenne de l'étudiant dans celles-ci
            matieres.append({'matiere': matiere, 'moyenne_matiere': round(
                etudiant.moyenne_etudiant_matiere(matiere, semestre)[0], 2)})

        data_releve.append({'ue': ue, 'moyenne': round(etudiant.moyenne_etudiant_ue(
            ue, semestre)[0], 2), 'matieres_ue': matieres, 'nbre_matieres': nbre_matieres + 1})

    context = {
        'nbre_ues': nbre_ues,
        'nbre_colonnes': nbre_colonnes+1,
        'colonnes': colonnes,
        'data_releve': data_releve,
        'etudiant': etudiant
    }

    # jai besoin dun dictionnaire qui pour chaque etudiant , regroupe son prenom , son nom et chacune des moyennes de chacune de ses matieres
    # un dictionnaire qui qui a le nombre de matiere par ue et le libelle de cette ue
    # un tableau des libelle de chacune des matiere
    # une donnee longueur tableau qui est le nombre de matiere total pour les ue + 2

    # context = {'releves_notes': releve_notes_details, 'semestre' : semestre, 'nbreUes' : len(releve_notes_details)}

    # nom des fichiers d'entrée et de sortie

    latex_input = 'synthese_semestre'
    latex_ouput = 'generated_synthese_semestre'
    pdf_file = 'pdf_synthese_semestre'

    # génération du pdf
    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    # visualisation du pdf dans le navigateur
    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        return response


@login_required(login_url=settings.LOGIN_URL)
def releve_notes_details_all(request, id_semestre, avec_rattrapage=None):

    avec_rattrapage = True if avec_rattrapage else False
    
    if request.user.groups.all().first().name not in ['directeur_des_etudes', 'secretaire']:
        return render(request, 'errors_pages/403.html')

    semestre = get_object_or_404(Semestre, id=id_semestre)
    etudiants = semestre.etudiant_set.filter(is_active=True).order_by('nom', 'prenom')

    nbre_colonnes = 2

    colonnes = '|l|l|'

    semestre_ues = semestre.get_all_ues()

    colonnes += 'c|' * len(semestre_ues)

    nbre_colonnes += len(semestre_ues)

    nbre_ues = len(semestre_ues)

    # récupération du nombre de matières par ue

    for ue in semestre_ues:
        # ajout des colonnes correspondant aux matières
        nbre_matieres = ue.matiere_set.all().count()
        colonnes += 'c|' * nbre_matieres
        colonnes += 'c|c|'
        nbre_colonnes += nbre_matieres+1

    # récupératon des données pour chaque lignes du relevé
    lignes_releve = []
    # boucle sur chaque étudiant piour constituer la ligne associée à l'étudiant
    for etudiant in etudiants:
        ligne = {}
        ligne['etudiant'] = etudiant
        # tableau contenant l'ensemble des UEs de l'étudiant
        ues = []
        # boucle sur chaque UE suivies par l'étudiant pour calculersa mmoyenne et sa moyenne dans chaque matières
        total_credit = 0
        for ue in semestre_ues:
            # tableau contenant l'ensemble des matières suivies par l'étudiant
            matieres = []
            nbre_matieres = len(ue.matiere_set.all())
            for matiere in ue.matiere_set.all():
                # récupération des matières de l'ue et la moyenne de l'étudiant dans celles-ci
                moyenne, _, _ = etudiant.moyenne_etudiant_matiere(matiere, semestre, avec_rattrapage)
                matieres.append({'matiere': matiere, 'moyenne_matiere': format(moyenne, '.2f')})
            moyenne, a_valider, _ = etudiant.moyenne_etudiant_ue(ue, semestre, avec_rattrapage)
            credit = ue.nbreCredits if a_valider else 0
            total_credit += credit
            # credit = str(credit) + ":" + str(ue.minValue)
            ues.append({'credit': credit, 'ue': ue, 'moyenne': format(moyenne, '.2f'), 'matieres_ue': matieres, 'nbre_matieres': nbre_matieres + 2, "total_credit": total_credit})
            
        ligne['ues'] = ues
        lignes_releve.append(ligne)
    print(colonnes)
    # return HttpResponse('Hello')
    context = {
        'semestre' : semestre,
        'nbre_ues': nbre_ues,
        'nbre_colonnes': nbre_colonnes,
        'colonnes': colonnes,
        'lignes': lignes_releve,
        'nbre_lignes': len(lignes_releve),
        'is_rattrapage': avec_rattrapage
    }

    # nom des fichiers d'entrée et de sortie

    latex_input = 'synthese_semestre_all'
    latex_ouput = 'generated_synthese_semestre_all'
    pdf_file = 'pdf_synthese_semestre_all'

    # génération du pdf
    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    # visualisation du pdf dans le navigateur
    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        return response

@login_required(login_url=settings.LOGIN_URL)
def bilan_annuelle(request, id_semestre, avec_rattrapage=None):

    avec_rattrapage = True if avec_rattrapage else False
    avec_rattrapage = True
    
    if request.user.groups.all().first().name not in ['directeur_des_etudes', 'secretaire']:
        return render(request, 'errors_pages/403.html')

    
    etudiants = Etudiant.objects.filter(is_active=True, semestres__id=id_semestre).order_by('nom', 'prenom')

    _semestre = Semestre.objects.get(pk=id_semestre)
    if _semestre.libelle in ["S1", "S2"]:
        semestres = Semestre.objects.filter(libelle__in=["S1", "S2"], annee_universitaire=_semestre.annee_universitaire)
        semestre_libelle = ["S1", "S2"]
    elif _semestre.libelle in ["S3", "S4"]:
        semestres = Semestre.objects.filter(libelle__in=["S3", "S4"], annee_universitaire=_semestre.annee_universitaire)
        semestre_libelle =  ["S3", "S4"]
    elif _semestre.libelle in ["S5", "S6"]:
        semestres = Semestre.objects.filter(libelle__in=["S5", "S6"], annee_universitaire=_semestre.annee_universitaire)
        semestre_libelle = ["S5", "S6"]
        

    # boucle sur chaque étudiant piour constituer la ligne associée à l'étudiant
    for etudiant in etudiants:
        total_credit = 0
        for semestre in semestres:
            semestre_ues = semestre.get_all_ues()
            total_credit_semestre = 0
            for ue in semestre_ues:
                _, a_valider, _ = etudiant.moyenne_etudiant_ue(ue, semestre, avec_rattrapage)
                credit = ue.nbreCredits if a_valider else 0
                total_credit += credit
                total_credit_semestre += credit
            if semestre.libelle == semestre_libelle[0]:
                etudiant.credit1 = total_credit_semestre
            elif semestre.libelle == semestre_libelle[1]:
                etudiant.credit2 = total_credit_semestre
                
        etudiant.total_credit = total_credit
        
    context = {
        'niveau' : f"{AnneeUniversitaire.getNiveau(semestre.libelle)} {semestre.annee_universitaire}",
        'etudiants': etudiants,
        'semestres_libelle' : semestre_libelle,
        'is_rattrapage': avec_rattrapage,
    }

    # nom des fichiers d'entrée et de sortie
    latex_input = 'synthese_annuelle'
    latex_ouput = 'generated_synthese_annuelle'
    pdf_file = 'pdf_synthese_annuelle'

    # génération du pdf
    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    # visualisation du pdf dans le navigateur
    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        return response


@login_required(login_url=settings.LOGIN_URL)
def recapitulatif_notes(request, id_matiere, id_semestre):
    """
    Génére le recaptitulatif des notes au cours d'un semestre dans une matière donnée.
    :param request: L'objet de requête Django.
    :param id_semestre: L'identifiant du semestre.
    :param id_matiere: L'identifiant de la mamtière.

    :return: Une réponse HTTP affichant le pdf du récapitulatif des notes de la matière.
    """

    if request.user.groups.all().first().name not in ['enseignant', 'directeur_des_etudes']:
        return render(request, 'errors_pages/403.html')

    matiere = get_object_or_404(Matiere, id=id_matiere)

    if matiere.enseignant == None:
        return render(request, 'errors_pages/403.html')

    if request.user.groups.all().first().name == 'enseignant':
        if matiere.enseignant.user.id != request.user.id:
            return render(request, 'errors_pages/403.html')

    semestre = get_object_or_404(Semestre, id=id_semestre)
    context = {}

    etudiants = semestre.etudiant_set.all()

    liste_etudiants = []
    for etudiant in etudiants:
        liste_etudiants.append(
            {'etudiant': etudiant, 'moyenne': etudiant.moyenne_etudiant_matiere(matiere, semestre)[0]})

    context['annee'] = semestre.annee_universitaire
    context['liste_etudiants'] = liste_etudiants
    context['matiere'] = matiere
    context['semestre'] = semestre

    # nom des fichiers d'entrée et de sortie

    latex_input = 'recapitulatif_ue'
    latex_ouput = 'generated_recapitulatif_ue'
    pdf_file = 'pdf_recapitulatif_ue'

    # génération du pdf
    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    # visualisation du pdf dans le navigateur
    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        return response

def recapitulatifs_des_notes_par_etudiant(request, id_semestre):
    """
    Affiche une page affichant l'ensemble des matières suivies au cours d'un semestre par l'étudiant, pour pouvoir choisir le récapitulatif de la matière recherchée.
    :param request: L'objet de requête Django.
    :param id_semestre: L'identifiant du semestre.
    :param id_matiere: L'identifiant de la mamtière.

    :return: Une réponse HTTP affichant une page html de contenant les matières.
    """
    semestre = get_object_or_404(Semestre, pk=id_semestre)
    user = get_object_or_404(get_user_model(), pk=request.user.pk)
    etudiant = Etudiant.objects.get(user=user)
    data = {
        'matieres': etudiant.moyenne_etudiant_matieres(semestre),
        'etudiant': etudiant
    }
    return render(request, 'evaluations/recapitulatifs_des_notes_etudiant.html', context=data)

@show_recapitulatif_note_permission("show_recapitulatif")
def recapitulatifs_des_notes_par_matiere(request, id_semestre, id_matiere):
    id_annee = request.session.get("id_annee_selectionnee")
    annee_selectionnee = get_object_or_404(AnneeUniversitaire, pk=id_annee)

    semestre = get_object_or_404(Semestre, pk=id_semestre)

    if semestre.annee_universitaire.id == annee_selectionnee.id:
        matiere = get_object_or_404(Matiere, pk=id_matiere)

        etudiants = []
        _etudiants = semestre.etudiant_set.all()
        print('etudiants : ')
        print(_etudiants)
        for etudiant in _etudiants:
            moyenne, a_valider, _ = etudiant.moyenne_etudiant_matiere(
                matiere, semestre)
            etudiants.append({
                'full_name': etudiant.full_name(),
                'notes': etudiant.notes_etudiant_matiere(matiere, semestre),
                'moyenne': moyenne,
                'a_valider': a_valider,
            })

        data = {
            'evaluations': matiere.evaluation_set.all(),
            'etudiants': etudiants,
            'matiere': matiere,
            'semestre': semestre,
        }

        return render(request, 'evaluations/recapitulatifs_des_notes.html', context=data)

    return HttpResponseNotFound(render(request, 'errors_pages/404.html'))


@login_required(login_url=settings.LOGIN_URL)
def evaluations_etudiant(request, id_matiere, id_etudiant):
    """
    Affiche la liste des évaluations d'un étudiant
    """
    id_annee_selectionnee = request.session["id_annee_selectionnee"]
    matiere = get_object_or_404(Matiere, pk=id_matiere)
    etudiant = get_object_or_404(Etudiant, pk=id_etudiant)
    annee_selectionnee = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)
    semestres_etudiants = list(etudiant.semestres.all())
    semestres_matiere = matiere.get_semestres(
        annee_universitaire=annee_selectionnee, type="__all__")
    etudiant_dans_classe = True
    if len(semestres_etudiants) > len(semestres_matiere):
        etudiant_dans_classe = semestres_matiere in semestres_etudiants
    else:
        etudiant_dans_classe = semestres_etudiants in semestres_matiere

    if not etudiant_dans_classe:
        return HttpResponseForbidden(render(request, 'errors_pages/403.html'))

    if 'semestre' in request.GET and request.GET.get('semestre') != "":
        id = request.GET.get('semestre')
        semestre = get_object_or_404(Semestre, pk=id)
    else:
        semestre = matiere.get_semestres(annee_selectionnee, '__all__')[0]

    evaluations = Evaluation.objects.filter(
        matiere=matiere, semestre=semestre, rattrapage__in=[True, False])

    evaluations_dict = []
    for evaluation in evaluations:
        try:
            note = evaluation.note_set.get(etudiant=etudiant).valeurNote
        except Exception as e:
            note = -1

        data = {
            'id': evaluation.id,
            'date': evaluation.date,
            'libelle': evaluation.libelle,
            'ponderation': evaluation.ponderation,
            'note': note,
        }

        evaluations_dict.append(data)

    semestres = etudiant.semestres.all()
    matiere_ids = request.session.get('matieres')
    matiere_ids = matiere_ids.split(";")
    matiere_ids.remove('')
    matieres = Matiere.objects.filter(pk__in=matiere_ids)

    data = {
        'annee_courrante': '',
        'matiere': matiere,
        'matieres': matieres,
        'evaluations': evaluations_dict,
        'semestres': semestres,
        'selected_semestre': semestre,
    }
    return render(request, 'evaluations/index_etudiants.html', data)


@login_required(login_url=settings.LOGIN_URL)
@evaluation_permission('main.view_evaluation')
def evaluations(request, id_matiere):
    """
    Affiche la liste des évaluations d'une matière donnée :model:`main.Matiere`.
    """
    id_annee_selectionnee = request.session["id_annee_selectionnee"]
    matiere = Matiere.objects.get(pk=id_matiere)
    annee_selectionnee = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    semestres = matiere.get_semestres(annee_universitaire=annee_selectionnee, type='__all__')
    
    if 'semestre' in request.GET and request.GET.get('semestre') != "":
        id = request.GET.get('semestre')
        semestre = get_object_or_404(Semestre, pk=id)
    else:
        semestre = semestres[0]

    if 'type' in request.GET and request.GET.get('type') in ['0', '1']:
        selected_type = request.GET.get('type')
        types_evaluations = [bool(int(selected_type))]
    else:
        selected_type = ""
        types_evaluations = [True, False]
    

    semestres = [semestre]

    evaluations = Evaluation.objects.filter(matiere=matiere, semestre__in=semestres, rattrapage__in=types_evaluations)
    
    url_path = "/main/evaluations/upload/" + \
        str(matiere.id) + "/" + str(semestre.id) + "/"

    matiere_ids = request.session.get('matieres')
    matiere_ids = matiere_ids.split(";")
    matiere_ids.remove('')
    matieres = Matiere.objects.filter(pk__in=matiere_ids)

    data = {
        'matiere': matiere,
        'matieres': matieres,
        'evaluations': evaluations,
        'semestres': semestres,
        'selected_semestre': semestre,
        'selected_type': selected_type,
        'url_path': url_path,
    }
    return render(request, 'evaluations/index.html', data)


@login_required(login_url=settings.LOGIN_URL)
@evaluation_permission('main.add_evaluation')
def createNotesByEvaluation(request, id_matiere, rattrapage, id_semestre):
    """
    Affiche un formulaire de création d'une évaluation et ensuite d'une note :model:`main.Note` selon la matière.
    """
    matiere = get_object_or_404(Matiere, pk=id_matiere)
    annee_universitaire = AnneeUniversitaire.static_get_current_annee_universitaire()
    semestre = get_object_or_404(Semestre, pk=id_semestre)
    if matiere.dans_semestre(semestre):
        if not rattrapage and not matiere.is_available_to_add_evaluation(semestre):
            return redirect('main:evaluations', id_matiere=matiere.id)
        else:
            etudiants = semestre.etudiant_set.filter(is_active=True).order_by("nom")
            if rattrapage:
                etudiants_qui_doivent_rattraper = matiere.get_etudiants_en_rattrapage()
            else:
                etudiants_qui_doivent_rattraper = []


        NoteFormSet = forms.inlineformset_factory(
            parent_model=Evaluation,
            model=Note,
            form=NoteForm,
            extra=len(etudiants),
            can_delete=False,
            min_num=0,
            validate_min=True,
        )

        if request.method == 'POST':
            evaluation_form = EvaluationForm(request.POST)
            evaluation_form.set_max_ponderation(
                matiere.ponderation_restante(semestre=semestre))
            evaluation_form.set_rattrapage(rattrapage)
            note_form_set = NoteFormSet(request.POST)
            if evaluation_form.is_valid() and note_form_set.is_valid():
                evaluation = evaluation_form.save(commit=False)
                evaluation.matiere = matiere
                evaluation.semestre = semestre
                evaluation.save()
                notes = note_form_set.save(commit=False)
                for note in notes:
                    note.evaluation = evaluation
                    note.save()
                message = f"""
                Bonjour chers étudiants, Votre note de {evaluation.matiere}
                a été saisi. Veuillez les consulter !
                Merci.
                """

                # emails = [etudiant.email for etudiant in etudiants]

                # send_email_task.delay(
                #     subject="Assignation de note des étudiants",
                #     message=message,
                #     email_address=emails,
                # )
                messages.success(
                    request, f"L 'évaluation {evaluation.libelle} a été ajouter.")
                return redirect('main:evaluations', id_matiere=matiere.id)
        else:
            queryset = Note.objects.none()
            evaluation_form = EvaluationForm()
            initial_etudiant_note_data = [{'etudiant': etudiant.id, 'etudiant_full_name': etudiant.full_name()} for etudiant in etudiants]
            note_form_set = NoteFormSet(initial=initial_etudiant_note_data, queryset=queryset)
            for form in note_form_set:
                if form.initial.get('etudiant') in etudiants_qui_doivent_rattraper:
                    form.fields['etudiant_full_name'].widget.attrs.update({'class':'form-control note_set-etudiant_full_name bg-danger'})
            
        data = {
            'evaluation_form': evaluation_form,
            'notes_formset': note_form_set,
            'matiere': matiere,
            'ponderation_possible': matiere.ponderation_restante(semestre),
            'rattrapage': rattrapage,
            'semestre': semestre,
            'etudiants_qui_doivent_rattraper' : etudiants_qui_doivent_rattraper,
        }
        
        return render(request, 'notes/create_or_edit_note.html', context=data)
    return redirect('main:evaluations', id_matiere=matiere.id)


@login_required(login_url=settings.LOGIN_URL)
@evaluation_permission('main.edit_evaluation')
def editeNoteByEvaluation(request, id):
    """
    Affiche un formulaire d'édition d'une note :model:`main.Note`.
    """

    evaluation = get_object_or_404(Evaluation, pk=id)
    matiere = evaluation.matiere
    semestre = evaluation.semestre
    
    etudiants = semestre.etudiant_set.filter(is_active=True)
    if evaluation.rattrapage:
        etudiants_qui_doivent_rattraper = matiere.get_etudiants_en_rattrapage()
        print(len(etudiants_qui_doivent_rattraper))
    else:
        etudiants_qui_doivent_rattraper = []
    etudiants_dans_evaluation = evaluation.etudiants.all()
    nouveaux_etudiants = etudiants.difference(etudiants_dans_evaluation)
    for etudiant in nouveaux_etudiants:
        Note.objects.create(evaluation=evaluation, etudiant=etudiant)

    NoteFormSet = forms.inlineformset_factory(
        parent_model=Evaluation,
        model=Note,
        form=NoteForm,
        extra=len(nouveaux_etudiants),
        can_delete=False,
        min_num=0,
        validate_min=True,
    )

    if request.method == 'POST':
        evaluation_form = EvaluationForm(request.POST, instance=evaluation)
        note_form_set = NoteFormSet(request.POST, instance=evaluation)
        evaluation_form.set_max_ponderation(
            matiere.ponderation_restante(semestre=semestre))
        evaluation_form.set_rattrapage(evaluation.rattrapage)
        if evaluation_form.is_valid() and note_form_set.is_valid():
            evaluation = evaluation_form.save(commit=False)
            evaluation.matiere = matiere
            evaluation.save()
            notes = note_form_set.save(commit=False)
            for note in notes:
                note.evaluation = evaluation
                note.save()

            messages.success(
                request, f"L 'évaluation {evaluation.libelle} a été mise à jours.")
            return redirect('main:evaluations', id_matiere=matiere.id)
    else:
        evaluation_form = EvaluationForm(instance=evaluation)
        # Créer une instance de d'ensemble de formulaire selon notre queryset
        initial_etudiant_note_data = [
            {'etudiant': etudiant.id, 'etudiant_full_name': etudiant.full_name()} for etudiant in nouveaux_etudiants]
        notes_queryset = evaluation.note_set.all().order_by('etudiant__nom')
        note_form_set = NoteFormSet(
            instance=evaluation, queryset=notes_queryset)
        for form in note_form_set:
            etudiant = Etudiant.objects.filter(id=form.initial.get('etudiant')).get()
            form.initial['etudiant_full_name'] = etudiant.full_name()
            if form.initial.get('etudiant') in etudiants_qui_doivent_rattraper:
                    form.fields['etudiant_full_name'].widget.attrs.update({'class':'form-control note_set-etudiant_full_name bg-danger'})
            

    data = {
        'evaluation_form': evaluation_form,
        'notes_formset': note_form_set,
        'matiere': matiere,
        'rattrapage': evaluation.rattrapage,
        'semestre': evaluation.semestre,
        'ponderation_possible': matiere.ponderation_restante(semestre=semestre)+evaluation.ponderation,
    }

    return render(request, 'notes/create_or_edit_note.html', context=data)


@login_required(login_url=settings.LOGIN_URL)
@evaluation_permission('main.delete_evaluation')
def deleteEvaluation(request, id):
    """
        Supprime une evaluation :model:`main.Note`.

        **Context**

        ``evaluation``
            une instance du :model:`main.Note`.
    """
    evaluation = get_object_or_404(Evaluation, pk=id)
    matiere = evaluation.matiere
    messages.success(
        request, f"L 'évaluation {evaluation.libelle} a été suprimmer.")
    evaluation.delete()
    return redirect('main:evaluations', id_matiere=matiere.id)


@login_required(login_url=settings.LOGIN_URL)
@evaluation_upload_permission('main.upload_evaluation')
def uploadEvaluation(request, id_matiere, id_semestre):
    matiere = get_object_or_404(Matiere, pk=id_matiere)
    semestre = get_object_or_404(Semestre, pk=id_semestre)

    if request.method == "POST":
        if 'file' in request.FILES:
            file = request.FILES.get('file')
            try:
                load_notes_from_evaluation(file, matiere, semestre)
                messages.success(request, "L'evaluation a été chargé !")
            except ValueError as ve:
                messages.error(request, str(ve))
            except Exception as e:
                messages.error(request, e)
        return redirect('main:evaluations', id_matiere=id_matiere)

    file_name = pre_load_evaluation_template_data(matiere, semestre)
    with open(file_name, 'rb') as file:
        response = HttpResponse(
            file.read(), content_type="application/force-download")
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(
            os.path.basename(file_name))
        return response


@login_required(login_url=settings.LOGIN_URL)
def affectation_matieres_professeur(request):
    if request.user.groups.all().first().name not in ['directeur_des_etudes']:
        return render(request, 'errors_pages/403.html')
    enseignants_filtrer = Enseignant.objects.all()
    matieres = Matiere.objects.all()

    if request.method == "POST":
        enseignant_id = request.POST.get("enseignant")
        enseignant_choisi = get_object_or_404(Enseignant, id=enseignant_id)
        matieres_selectionnees = request.POST.getlist("matieres[]")
        coefficient_choisi = request.POST.getlist("coefficients[]")

        for index, matiere in enumerate(matieres_selectionnees):
            matiere_obj = Matiere.objects.get(libelle=matiere)
            coefficient = float(coefficient_choisi[index])
            matiere_obj.enseignant = enseignant_choisi
            matiere_obj.coefficient = coefficient
            matiere_obj.save()

        return render(request, "matieres/liste_matieres.html", {"matieres": matieres})

    else:
        matieres_filtrer = Matiere.objects.filter(enseignant=None)
        context = {'enseignants': enseignants_filtrer,
                   'matieres': matieres_filtrer}
        return render(request, "matieres/affectation_professeur.html", context)


@login_required(login_url=settings.LOGIN_URL)
def liste_matieres_professeur(request):
    if request.user.groups.all().first().name not in ['directeur_des_etudes']:
        return render(request, 'errors_pages/403.html')
    matieres = Matiere.objects.all()

    return render(request, "matieres/liste_matieres.html", {"matieres": matieres})


@login_required(login_url=settings.LOGIN_URL)
def affectation_ues_professeur(request):
    if request.user.groups.all().first().name not in ['directeur_des_etudes']:
        return render(request, 'errors_pages/403.html')
    enseignants_filtrer = Enseignant.objects.all()
    ues = Ue.objects.all()

    if request.method == "POST":
        enseignant_id = request.POST.get("enseignant")
        enseignant_choisi = get_object_or_404(Enseignant, id=enseignant_id)
        ues_selectionnees = request.POST.getlist("ues[]")

        for index, ue in enumerate(ues_selectionnees):
            ue_obj = Ue.objects.get(libelle=ue)
            ue_obj.enseignant = enseignant_choisi
            ue_obj.save()

        return render(request, "ues/liste_ues.html", {"ues": ues})

    else:
        ues_filtrer = Ue.objects.filter(enseignant=None)
        context = {'enseignants': enseignants_filtrer,
                   'ues': ues_filtrer}
        return render(request, "ues/affectation_ues.html", context)


@login_required(login_url=settings.LOGIN_URL)
def liste_ues_professeur(request):
    if request.user.groups.all().first().name not in ['directeur_des_etudes']:
        return render(request, 'errors_pages/403.html')
    ues = Ue.objects.all()

    return render(request, "ues/liste_ues.html", {"ues": ues})


@login_required(login_url=settings.LOGIN_URL)
def retirer_professeur(request, id):
    if request.user.groups.all().first().name not in ['directeur_des_etudes']:
        return render(request, 'errors_pages/403.html')
    matiere = get_object_or_404(Matiere, pk=id)
    matiere.enseignant = None
    matiere.save()

    return redirect('/main/liste_matieres_professeur')


@login_required(login_url=settings.LOGIN_URL)
def retirer_professeur_ue(request, id):
    if request.user.groups.all().first().name not in ['directeur_des_etudes']:
        return render(request, 'errors_pages/403.html')
    ue = get_object_or_404(Ue, pk=id)
    ue.enseignant = None
    ue.save()

    return redirect('/main/liste_ues_professeur')


@login_required(login_url=settings.LOGIN_URL)
def modifier_coefficient(request, matiere_id, coefficient):
    if request.user.groups.all().first().name not in ['directeur_des_etudes']:
        return render(request, 'errors_pages/403.html')
    matiere = get_object_or_404(Matiere, pk=matiere_id)
    matiere.coefficient = coefficient
    matiere.save()

    return redirect('/main/liste_matieres_professeur')


def boite_a_suggestion(request):
    return render(request, "boite_suggestion.html")


@login_required(login_url=settings.LOGIN_URL)
def profil(request):
    data = {
        'utilisateur': request.user,
        'page_is_not_profil': False,
    }
    return render(request, "connexion/profil.html", data)


@login_required(login_url=settings.LOGIN_URL)
def edit_profil(request):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("nom")
        last_name = request.POST.get("prenom")
        user = request.user
        user.username = username
        user.first_name = first_name
        user.last_name = last_name

        user.save()
        notification = {
            "message": "Informations modifier avec succés.", "type": "succes"}
        context = {"utilisateur": user, "notification": notification,
                   'page_is_not_profil': False, }
        return render(request, "connexion/edit_profil.html", context)

    else:
        user = request.user
        return render(request, "connexion/edit_profil.html", {"utilisateur": user, 'page_is_not_profil': False, })

@login_required(login_url=settings.LOGIN_URL)
def changer_mdp(request):
    old = request.POST.get("old_password")
    new = request.POST.get("password")
    confirm = request.POST.get("password-confirm")
    user = authenticate(request, username=request.user.username, password=old)
    if user:
        if new == confirm:
            user.set_password(new)
            user.save()
            notification = {
                "message": "Mot de passe modifier avec succés.", "type": "succes"}
        else:
            notification = {
                "message": " Le nouveau mot de passe et sa confirmation ne concordent pas", "type": "erreur"}
    else:
        notification = {
            "message": "Ancien mot de passe incorrect", "type": "erreur"}
    return render(request, "connexion/edit_profil.html", {"notification": notification,  'page_is_not_profil': False, })

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            user_groups = user.groups.all()
            is_etudiant = bool(user_groups.filter(name="etudiant"))
            is_directeur_des_etudes = bool(
                user_groups.filter(name="directeur_des_etudes"))
            is_enseignant = bool(user_groups.filter(name="enseignant"))
            is_secretaire = bool(user_groups.filter(name="secretaire"))
            is_comptable = bool(user_groups.filter(name="comptable"))
            

            has_model = False
            if is_etudiant:
                try:
                    etudiant = Etudiant.objects.get(user=user)
                    id_auth_model = etudiant.id
                    request.session['id_auth_model'] = id_auth_model
                    request.session['profile_path'] = f'main/detail_etudiant/{id_auth_model}/'
                    has_model = True
                except Exception as e:
                    pass
            else:
                try:
                    personnel = user.personnel
                    id_auth_model = personnel.id
                    print("Hello")
                    print(personnel)

                    # if is_enseignant:
                    #     id_auth_model = Enseignant.objects.get(user=user).id
                    #     request.session['profile_path'] = f'main/detail_etudiant/{id_auth_model}/'
                    print(id_auth_model)
                    request.session['id_auth_model'] = id_auth_model
                    has_model = True
                except Exception as e:
                    pass
            if has_model or (user.is_superuser and is_directeur_des_etudes):
                login(request, user)
                request.session['is_directeur_des_etudes'] = is_directeur_des_etudes
                request.session['is_etudiant'] = is_etudiant
                request.session['is_enseignant'] = False if is_directeur_des_etudes else is_enseignant
                request.session['is_secretaire'] = False if is_directeur_des_etudes else is_secretaire
                request.session['is_comptable'] = False if is_directeur_des_etudes else is_comptable
                return redirect('/')
            return render(request, "connexion/login.html", {'error': 'Identifiants invalides'})

        return render(request, "connexion/login.html", {'error': 'Identifiants invalides'})

    return render(request, "connexion/login.html")

def recuperation_mdp(request):
    if request.method == "POST":
        username_or_email = request.POST.get('username_or_email')

        notification = {
            "message": "Cet utilisateur n'existe pas", "type": "erreur"}

        users = get_user_model().objects.filter(username=username_or_email) | get_user_model().objects.filter(email=username_or_email)

        if not users:
            messages.error(request, "Votre identifiant est invalide !")
            return redirect('main:reminder')
        
        user = users.first()

        password = get_user_model().objects.make_random_password()
        user.set_password(password)
        user.save()

        message = f"""
        Bonjour M. {user.first_name} {user.last_name}, votre mot de passe a été modier par
        ce qui suit : {password}. Une fois que vous serez connecté a votre compte n'oublier pas le
        modifier.
        Bonne journnée :) ! 
        """

        messages.success(
            request, "Mot de passe modifier ! Un mail vous a été envoyé sur votre compte outlook ! ")

        send_email_task.delay(
            subject="Alert récupération de mot de passe !",
            message=message,
            email_address=[user.email],
        )

        return redirect('main:reminder')

    return render(request, "connexion/reminder.html")

@login_required(login_url=settings.LOGIN_URL)
def change_role(request, id_role):
    user = request.user
    user_groups = user.groups.all()
    role = user_groups.get(id=id_role)

    is_directeur_des_etudes = role.name == "directeur_des_etudes"
    is_enseignant = role.name == "enseignant"
    is_secretaire = role.name == "secretaire"
    is_comptable = role.name == "comptable"

    request.session['is_directeur_des_etudes'] = is_directeur_des_etudes
    request.session['is_enseignant'] = False if is_directeur_des_etudes else is_enseignant
    request.session['is_secretaire'] = False if is_directeur_des_etudes else is_secretaire
    request.session['is_comptable'] = False if is_directeur_des_etudes else is_comptable
    return redirect('/')

@login_required(login_url=settings.LOGIN_URL)
def logout_view(request):
    logout(request)
    return render(request, "connexion/login.html")

    ##### Enseignant #####

@login_required(login_url=settings.LOGIN_URL)
def create_enseignant(request, id=0):
    if request.method == "GET":
        if id == 0:
            form = EnseignantForm()
        else:
            enseignant = Enseignant.objects.get(pk=id)
            form = EnseignantForm(instance=enseignant)
        return render(request, "enseignants/create_enseignant.html", {'form': form})
    else:
        if id == 0:
            form = EnseignantForm(request.POST)
        else:
            enseignant = Enseignant.objects.get(pk=id)
            form = EnseignantForm(request.POST, instance=enseignant)
        if form.is_valid():
            form.save()
            # id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
            return redirect('main:enseignants')

        else:
            return render(request, "enseignants/create_enseignant.html", {'form': form})

# Cette vue permet d'importer les données enseignants via un fichier excel de foemat xlsx
def importer_les_enseignants(request):
    if request.method == 'POST':
        if 'myfile' not in request.FILES:
            return render(request, 'etudiants/message_erreur.html', {'message': "Aucun fichier sélectionné."})

        enseignants_resource = EnseignantResource()
        dataset = Dataset()
        enseignant = request.FILES['myfile']

        try:
            imported_data = dataset.load(enseignant.read(), format='xlsx')
            for data in imported_data:
                lieunaissance = data[5] if data[5] else "Inconnu"
                nationalite = data[12] if data[12] else "Togolaise"
                salaireBrut = data[16] if data[16] else '0'
                nbreJrsCongesRestant = data[18] if data[18] else '0'
                nbreJrsConsomme = data[19] if data[19] else '0'
                specialite = data[21] if data[21] else "Inconnu"

                enseignant = Enseignant(
                    personnel_ptr=data[0],
                    nom=data[1],
                    prenom=data[2],
                    sexe=data[3],
                    datenaissance=data[4],
                    lieunaissance=lieunaissance,
                    contact=data[6],
                    email=data[7],
                    adresse=data[8],
                    prefecture=data[9],
                    is_active=data[10],
                    carte_identity=data[11],
                    nationalite=nationalite,
                    user=data[13],
                    profil=data[14],
                    id=data[15],
                    salaireBrut=salaireBrut,
                    dernierdiplome=data[17],
                    nbreJrsCongesRestant=nbreJrsCongesRestant,
                    nbreJrsConsomme=nbreJrsConsomme,
                    type=data[20],
                    specialite=specialite,
                )
                enseignant.save()
            return render(request, 'etudiants/message_erreur.html', {'message': "Données importées avec succès."})

        except Exception as e:
            return render(request, 'etudiants/message_erreur.html', {'message': "Erreur lors de l importation du fichier Excel."})
    return render(request, 'enseignants/importer.html')

@login_required(login_url=settings.LOGIN_URL)
def enseignants(request):
    id_annee_selectionnee = request.session.get("id_annee_selectionnee")
    role = get_user_role(request)
    annee_universitaire = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)
    enseignants = Enseignant.objects.filter(personnel__user__is_active=True)
    data = {}
    etats = [{'id': 1, 'value': 'Actif'}, {'id': 0, 'value': 'Suspendue'}]
    etats_selected = [True, False]
    etat_id = "__all__"
    semestres = annee_universitaire.semestre_set.all()
    semestres_selected = semestres
    semestre_id = "__all__"

    if 'semestre' in request.POST:
        semestre_id = request.POST.get('semestre')
        if semestre_id != "" and semestre_id != "__all__":
            semestres_selected = semestres.filter(pk=semestre_id)

    if 'etat' in request.POST:
        etat_id = request.POST.get('etat')
        if etat_id != "" and etat_id != "__all__":
            etat_id = int(etat_id)
            etats_selected = [bool(etat_id)]

    if role:
        if role.name == "etudiant" or role.name == "enseignant":
            niveau = "Mes enseignants"
            if role.name == "enseignant":
                niveau = "Mes collegues"
            enseignants = Enseignant.objects.filter(
                personnel__is_active=True, matiere__ue__programme__semestre__in=semestres_selected).distinct()
        elif role.name == "directeur_des_etudes" or role.name == "comptable":
            if role.name == "comptable":
                niveau = "Mes collegues"
            niveau = "Nos Enseignants"
            if semestre_id == "__all__":
                enseignants = Enseignant.objects.filter(
                    personnel__user__is_active__in=etats_selected)
            else:
                enseignants = Enseignant.objects.filter(
                    personnel__user__is_active__in=etats_selected, matiere__ue__programme__semestre__in=semestres_selected).distinct()

    semestres_selected = {'id': semestre_id}
    etats_selected = {'id': etat_id}

    data = {
        'enseignants': enseignants,
        'niveau': niveau,
        'semestres': semestres,
        'selected_semestre': semestres_selected,
        'etats': etats,
        'selected_etat': etats_selected,
    }

    return render(request, 'enseignants/enseignants.html', context=data)

@login_required(login_url=settings.LOGIN_URL)
def enseignant_inactif(request):
    enseignants = Enseignant.objects.filter(is_active=False)
    return render(request, 'enseignants/enseignants.html', {'enseignants': enseignants})

@login_required(login_url=settings.LOGIN_URL)
def enseignant_detail(request, id):
    enseignant = Enseignant.objects.get(id=id)
    return render(request, 'enseignants/enseignant_detail.html', {'enseignant': enseignant})

@login_required(login_url=settings.LOGIN_URL)
def certificat_travail(request, id):
    information = get_object_or_404(Information, id=id)
    context = {'information': information}

    # nom des fichiers d'entrée et de sortie
    latex_input = 'certificat_travail'
    latex_ouput = 'generated_certificat_travail'
    pdf_file = 'pdf_certificat_travail'

    # génération du pdf
    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    # visualisation du pdf dans le navigateur
    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        return response

@login_required(login_url=settings.LOGIN_URL)
def liste_informations_enseignants(request):
    informations_enseignants = Information.objects.all()
    context = {
        'informations_enseignants': informations_enseignants,
    }
    return render(request, 'informations/information_list.html', context)

@login_required(login_url=settings.LOGIN_URL)
def enregistrer_informations(request, id=0):
    if request.method == "GET":
        if id == 0:
            form = InformationForm()
        else:
            information = Information.objects.get(pk=id)
            form = InformationForm(instance=information)
        return render(request, "informations/enregistrer_informations.html", {'form': form})
    else:
        if id == 0:
            form = InformationForm(request.POST)
        else:
            information = Information.objects.get(pk=id)
            form = InformationForm(request.POST, instance=information)
        if form.is_valid():
            information = form.save(commit=False)
            directeur = DirecteurDesEtudes.objects.get(user=request.user)
            information.directeur = directeur

            dateDebut = information.dateDebut
            dateFin = information.dateFin

            # Vérification de la validité des dates
            if dateDebut and dateFin and dateDebut > dateFin:
                form.add_error(
                    'dateFin', "La date de fin ne peut pas être antérieure à la date de début.")
                return render(request, "informations/enregistrer_informations.html", {'form': form})

            form.save()

            return redirect('main:liste_informations_enseignants')

        else:
            return render(request, "informations/enregistrer_informations.html", {'form': form})

@login_required(login_url=settings.LOGIN_URL)
# Cette vue affiche la liste des semestre courants
def semestres(request):

    id_annee_selectionnee = request.session.get('id_annee_selectionnee')
    annee_selectionnee = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)

    semestres = Semestre.objects.filter(annee_universitaire=annee_selectionnee)
    context = {
        "semestres": semestres,
    }
    return render(request, 'semestres/semestres.html', context)

@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.view_personnel")
def personnels(request):
    listespersonnelles = Personnel.objects.all()
    print(listespersonnelles)
    return render(request, "employes/index.html", {'listespersonnelles' : listespersonnelles})

@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.add_personnel")
def create_personnel(request):
    data = {}
    roles = Group.objects.all()
    if request.method == "POST":
        form = PersonnelForm(request.POST)
        form.fields['roles'].queryset = roles
        if form.is_valid():
            personnel = form.save()
            inputs_data = form.clean()
            type_enseignant = inputs_data.get('type')
            speliatite_enseignant = inputs_data.get('specialite')
            groups = inputs_data.get('roles')
            personnel.assign_groups(groups)
            personnel.bind_enseignant(type_enseignant, speliatite_enseignant)
            return redirect('main:personnels')
        data['form'] = form
    else:
        data['form'] = PersonnelForm()  
        data['form'].fields['roles'].queryset = roles
        
    return render(request, 'employes/create_or_edit.html', context=data)

@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.update_personnel")
def update_personnel(request, id):
    data = {}
    personnel = get_object_or_404(Personnel, pk=id)
    enseignant = personnel.get_enseignant()
    roles = Group.objects.all()
    if request.method == "POST":
        form = PersonnelForm(request.POST, instance=personnel)
        form.fields['roles'].queryset = roles
        if form.is_valid():
            personnel = form.save()
            inputs_data = form.clean()
            type_enseignant = inputs_data.get('type')
            speliatite_enseignant = inputs_data.get('specialite')
            groups = inputs_data.get('roles')
            personnel.assign_groups(groups)
            personnel.bind_enseignant(type_enseignant, speliatite_enseignant)
            return HttpResponse("Hello2")
            return redirect('main:personnels')
        data['form'] = form
    else:
        data['form'] = PersonnelForm(instance=personnel)  
        data['form'].fields['roles'].queryset = roles
        data['form'].fields['roles'].initial = list(personnel.user.groups.values_list('pk', flat=True))
        if enseignant:
            data['form'].fields['type'].initial = enseignant.type
            data['form'].fields['specialite'].initial = enseignant.specialite
        
    return render(request, 'employes/create_or_edit.html', context=data)

@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.delete_personnel")
def delete_personnel(request, id):
    personnel = get_object_or_404(Personnel, pk=id)
    personnel.delete()
    return redirect('main:personnels')


@login_required(login_url=settings.LOGIN_URL)
# Cette vue permet de clôturer les semestres
def cloturer_semestre(request, semestre_id):
    semestre = get_object_or_404(Semestre, id=semestre_id)
    semestre.courant = False
    semestre.save()
    return redirect('/main/semestres')


@login_required(login_url=settings.LOGIN_URL)
# Cette vue permet de réactiver un semestre déjà clôtuté
def reactiver_semestre(request, semestre_id):
    semestre = get_object_or_404(Semestre, id=semestre_id)
    semestre.courant = True
    semestre.save()
    return redirect('/main/semestres')


@login_required(login_url=settings.LOGIN_URL)
# Cette fonction permet d'afficher la liste des étudiants attché à un semestre
def historique_semestre(request, semestre_id):
    current_annee = AnneeUniversitaire.static_get_current_annee_universitaire()
    semestre = Semestre.objects.filter(
        label=semestre_id, annee_universitaire=current_annee).get()
    # Obtenez tous les étudiants liés à ce semestre
    etudiants = semestre.etudiant_set.all()
    # Obtenez toutes les matières liées à ce semestre
    matieres = Matiere.objects.filter(ue__semestre=semestre)
    # Obtenez toutes les évaluations liées à ce semestre
    evaluations = Evaluation.objects.filter(matiere__ue__semestre=semestre)
    # Obtenez toutes les notes liées à ce semestre
    notes = Note.objects.filter(evaluation__matiere__ue__semestre=semestre)

    context = {
        'semestre': semestre,
        'etudiants': etudiants,
        'matieres': matieres,
        'evaluations': evaluations,
        'notes': notes,
    }

    return render(request, 'semestres/historique_semestre.html', context)


def export(request):
    etudiants_resource = EtudiantResource()
    dataset = etudiants_resource.export()
    response = HttpResponse(
        dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="persons.xls"'
    return response


#####
def ajout_semestre_etudiant(niveau, promotion, annees):
    annee_universitaire = annees.get(annee=promotion)
    if niveau == "L1":
        semestre_s1 = annee_universitaire.semestre_set.get(libelle='S1')
        semestre_s2 = annee_universitaire.semestre_set.get(libelle='S2')
        return semestre_s1, semestre_s2
    return []
    # elif niveau == "L2":
    #     # Si "L2"
    #     # ajout des semestres de L1(S1 et S2)
    #     semestre_s1 = annee_universitaire.semestre_set.get(libelle='S1')
    #     semestre_s2 = annee_universitaire.semestre_set.get(
    #                         libelle='S2')
    #     etudiant.semestres.add(semestre_s1, semestre_s2)
    #     annee_entree_plus_un = etudiant.anneeentree + 1
    #     annee_universitaire_plus_un = all_annees.get(annee=annee_entree_plus_un)
    #     # ajout des semestres de L2(S3 et S4)
    #     semestre_s3 = annee_universitaire_plus_un.semestre_set.get(
    #     libelle='S3')                
                
    #     semestre_s4 = annee_universitaire_plus_un.semestre_set.get(
    #     libelle='S4')
    #     etudiant.semestres.add(semestre_s3,semestre_s4)
    # elif niveau == "L3":
    #     # Si "L3"
    #     #ajout des semestres de L1(S1 et S2)
    #     semestre_s1 = annee_universitaire.semestre_set.get(
    #     libelle='S1')
    #     semestre_s2 = annee_universitaire.semestre_set.get(
    #                         libelle='S2')
    #     etudiant.semestres.add(semestre_s1, semestre_s2)
    #     # ajout des semestres de L2
    #     annee_entree_plus_un = etudiant.anneeentree + 1
    #     annee_universitaire_plus_un = all_annees.get(
    #     annee=annee_entree_plus_un)

    #     semestre_s3 = annee_universitaire_plus_un.semestre_set.get(
    #                         libelle='S3')
    #     semestre_s4 = annee_universitaire_plus_un.semestre_set.get(
    #     libelle='S4')
    #     etudiant.semestres.add(semestre_s3, semestre_s4)
                        
    #     #ajout des semestres de L3(S5 et S6)
    #     annee_entree_plus_deux = etudiant.anneeentree + 2
    #     annee_universitaire_plus_deux = all_annees.get(
    #     annee=annee_entree_plus_deux)

    #     semestre_s5 = annee_universitaire_plus_deux.semestre_set.get(
    #                         libelle='S5')
    #     semestre_s6 = annee_universitaire_plus_deux.semestre_set.get(
    #                         libelle='S6')
    #     etudiant.semestres.add(semestre_s5, semestre_s6)
    # else:
    #     # Sinon, attachez l'étudiant au Semestre 1 (S1) de l'année universitaire en cours
    #     semestre_s1_courant = annee_universitaire.semestre_set.get(
    #                     libelle='S1')
    #     etudiant.semestres.add(semestre_s1_courant)

    

# Cette vue permet d'importer les données etudiants via un fichier xlsx
def importer_data(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            messages.error(request, "Vous devez selectionner un fichier")
            return redirect('main:create_etudiant')

        etudiants_resource = EtudiantResource()
        dataset = Dataset()
        etudiant = request.FILES['file']

        imported_data = list(dataset.load(etudiant.read(), format='xlsx'))

        annees = AnneeUniversitaire.objects.all().prefetch_related('semestre_set')

    
        for data in imported_data[1:112]:
            promotion=data[0]
            nom=data[1]
            prenom=data[2]
            datenaissance=data[3]
            lieunaissance=data[4]
            sexe=data[5]
            anneebac2=data[6]
            contact=data[9]
            adresse=data[10]
            niveau = data[7]
            is_active=True

            if nom == None and prenom == None:
                continue
            
            #print(prenom, ";", nom)
            username = (nom + prenom).lower()
            username = username.replace(" ", "")
            print(username)
            print(datenaissance.__str__())

            if datenaissance is None:
                # datenaissance = datetime(2024, 12, 12)
                pass
            else:
                datenaissance = datenaissance.__str__()
                if "/" in datenaissance:
                    datenaissance_array = datenaissance.split('/')
                    datenaissance = datetime(int(datenaissance_array[2]), int(datenaissance_array[1]),int(datenaissance_array[0]))
                    print("/")
                    print(datenaissance_array)
                else:
                    datenaissance_array = datenaissance.split('-')
                    datenaissance_array[2] = datenaissance_array[2][:2]
                    datenaissance = datetime(int(datenaissance_array[0]), int(datenaissance_array[1]),int(datenaissance_array[2]))
                    print(datenaissance_array)                

            # return HttpResponse("o")
            try:
                etudiant = Etudiant.objects.get(user__username=username)
                # etudiant = Etudiant.objects.get(user__username__contains=nom.lower())
                semestres = ajout_semestre_etudiant(niveau, promotion, annees)
                etudiant.semestres.set(semestres)
                etudiant.save()
                print(etudiant)
            except Exception as e:
                print("Etudiant n'existe pas. ")
                print(e)
                etudiant = Etudiant.objects.create(
                    anneeentree=promotion,
                    nom=nom,
                    prenom=prenom,
                    datenaissance=datenaissance,
                    lieunaissance=lieunaissance,
                    sexe=sexe,
                    anneebac2=anneebac2,
                    contact=contact,
                    adresse=adresse,
                    is_active=is_active,
                )
                semestres = ajout_semestre_etudiant(niveau, promotion, annees)
                etudiant.semestres.set(semestres)
                print(semestres)   
      
        messages.success(request, "Donnée importer avec succes !")
        return redirect('main:etudiants')
