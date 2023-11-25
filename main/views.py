import json
from django import forms
from django.http import HttpResponse
from main.pdfMaker import generate_pdf
from django.conf import settings
from main.forms import EnseignantForm, EtudiantForm, EvaluationForm, InformationForm, ProgrammeForm, NoteForm, TuteurForm, UeForm, MatiereForm
from .models import Domaine, Enseignant, Evaluation, DirecteurDesEtudes, Personnel, Information, Matiere, Etudiant, Competence, Note, Comptable, Parcours, Programme, Semestre, Ue, AnneeUniversitaire, Tuteur, Seance
from django.shortcuts import get_object_or_404, redirect, render
from main.helpers import *
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from .resources import EtudiantResource
from tablib import Dataset
from .custom_permission_required import evaluation_permission, show_recapitulatif_note_permission


@login_required(login_url=settings.LOGIN_URL)
def dashboard(request):
    id_annee_selectionnee = request.session.get('id_annee_selectionnee')
    annee_selectionnee = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)
    semestres = annee_selectionnee.get_semestres()
    data = {
        'nb_etudiants': len(Etudiant.objects.filter(semestres__in=semestres).distinct()),
        'nb_enseignants': len(Enseignant.objects.filter(matiere__ue__programme__semestre__in=semestres).distinct()),
        'nb_matieres': len(Matiere.objects.filter(ue__programme__semestre__in=semestres).distinct()),
        'nb_ues': len(Ue.objects.filter(programme__semestre__in=semestres).distinct()),
    }
    return render(request, 'dashboard.html', context=data)

@login_required(login_url=settings.LOGIN_URL)
def change_annee_universitaire(request):
    if 'annee_universitaire' in request.GET:
        selected_annee = request.GET.get('annee_universitaire')
        request.session["id_annee_selectionnee"] = selected_annee if selected_annee != "" else request.session["id_annee_selectionnee"]
    return redirect(request.GET.get('origin_path'))


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.view_etudiant")
def etudiants(request):
    id_annee_selectionnee = request.session.get("id_annee_selectionnee")
    role = get_user_role(request)
    annee_universitaire = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)
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
            niveau = AnneeUniversitaire.getNiveau(
                semestres_selected[0].libelle)

    if 'etat' in request.POST:
        etat_id = request.POST.get('etat')
        if etat_id != "" and etat_id != "__all__":
            etat_id = int(etat_id)
            etats_selected = [bool(etat_id)]

    if role:
        if role.name == "etudiant" or role.name == "enseignant" :
            niveau = "Mes camarades"
            if role.name == "enseignant" :
                niveau = "Nos Étudiants"
            etudiants = Etudiant.objects.filter(is_active=True, semestres__in=semestres_selected).distinct()
        elif role.name in ["directeur_des_etudes", "secretaire", "comptable"]:
            niveau = "Nos Étudiants"
            etudiants = Etudiant.objects.filter(
                is_active__in=etats_selected, semestres__in=semestres_selected).distinct()
        elif role.name == "comptable":
            niveau = "Nos Étudiants"
            etudiants = Etudiant.objects.filter(
                is_active__in=etats_selected, semestres__in=semestres_selected).distinct()

    try:
        semestres_selected = semestres_selected.get()
    except:
        semestres_selected = {'id': semestre_id}
    etats_selected = {'id': etat_id}

    # etudiants = Etudiant.objects.filter(
    #     semestres__in=semestres_selected, is_active=True).distinct()
    temp_etudiants = []
    for etudiant in etudiants:
        # sanitized_input = ''.join(
        #     char for char in etudiant.id if char.isalnum() or char in "+-./")
        # input_bytes = sanitized_input.encode()
        temp_etudiants.append({'etudiant': etudiant, 'niveau': etudiant.get_niveau_annee(
            annee_universitaire=annee_universitaire)[0]})

    data = {
        'etudiants': temp_etudiants,
        'semestres': semestres,
        'niveau': niveau,
        'selected_semestre': semestres_selected,
        'etats': etats,
        'selected_etat': etats_selected
    }

    return render(request, 'etudiants/etudiants.html', context=data)


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.change_etudiant")
def etudiants_suspendu(request):
    # Obtenez l'année universitaire courante
    annee_courante = AnneeUniversitaire.static_get_current_annee_universitaire()

    if annee_courante != "-":
        # Obtenez la liste des étudiants pour l'année universitaire courante
        etudiants = Etudiant.objects.filter(
            semestres__annee_universitaire=annee_courante, is_active=False)

    context = {
        'etudiants': etudiants,
        'annee_courante': annee_courante,
    }
    return render(request, 'etudiants/etudiants_suspendu.html', context)


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.view_etudiant")
def detailEtudiant(request, id):  # Retourne le détail d'un etudiant donnée
    etudiant = get_object_or_404(Etudiant, id=id)
    return render(request, "etudiants/detailEtudiant.html", {"etudiant": etudiant})


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.add_etudiant")
def create_etudiant(request, id=0):
    if request.method == "GET":
        if id == 0:
            form = EtudiantForm()
        else:
            etudiant = Etudiant.objects.get(pk=id)
            form = EtudiantForm(instance=etudiant)
        return render(request, 'etudiants/create_etudiant.html', {'form': form})
    else:
        if id == 0:
            form = EtudiantForm(request.POST)
        else:
            etudiant = Etudiant.objects.get(pk=id)
            form = EtudiantForm(request.POST, instance=etudiant)
        if form.is_valid():
            # Ne pas sauvegarder l'étudiant pour le moment
            etudiant = form.save(commit=False)
            etudiant.save()  # Sauvegarder l'étudiant pour générer un ID

            # Trouver l'année universitaire en cours
            annee_universitaire_courante = AnneeUniversitaire.objects.get(
                annee_courante=True)

            # Vérifier si le Semestre 1 (S1) de l'année universitaire courante existe
            try:
                semestre_s1 = annee_universitaire_courante.semestre_set.get(
                    libelle='S1')
            except Semestre.DoesNotExist:
                # Le semestre n'existe pas, nous devons le créer
                semestre_s1 = Semestre(
                    libelle='S1',
                    credits=30,
                    courant=True,  # Vous pouvez définir la valeur correcte ici
                    annee_universitaire=annee_universitaire_courante
                )
                semestre_s1.save()
            # Attacher l'étudiant au Semestre 1 (S1) de l'année universitaire en cours
            etudiant.semestres.add(semestre_s1)
            etudiant.save()  # Enregistrez l'étudiant après l'association    
           # id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
            return redirect('main:etudiants')
        else:
            return render(request, 'etudiants/create_etudiant.html', {'form': form})


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.view_etudiant")
# Cette vue permet d'afficher la liste des étudiants par semestre
def liste_etudiants_par_semestre(request, id_annee_selectionnee):
    role = get_user_role(request)
    annee_universitaire = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)
    current_annee = AnneeUniversitaire.static_get_current_annee_universitaire()
    niveau = ""
    data = {}
    semestre_id = None

    if role.name == "directeur_des_etudes":
        niveau = "IFNTI"
        semestres = annee_universitaire.semestre_set.all()
        semestres_selected = semestres

    if 'semestre' in request.GET:
        semestre_id = request.GET.get('semestre')
        semestres_selected = semestres.filter(pk=semestre_id)

    etudiants = Etudiant.objects.filter(
        semestres__in=semestres_selected, is_active=True).distinct()

    etudiants_insuffisants = []

    # Ajoutez cette partie pour calculer les crédits obtenus par chaque étudiant
    for etudiant in etudiants:
        credits_obtenus = etudiant.credits_obtenus_semestre(
            semestres_selected[0])  # Utilisez le premier semestre sélectionné
        # Créez un attribut pour stocker les crédits obtenus
        etudiant.credits_obtenus = credits_obtenus

    # Ajoutez cette partie pour récupérer le semestre actuel de chaque étudiant
    for etudiant in etudiants:
        semestres_etudiant = etudiant.semestres.filter(
            annee_universitaire=annee_universitaire)
        if semestres_etudiant.exists():
            semestre_actuel = semestres_etudiant.latest('libelle')
            etudiant.semestre_actuel = semestre_actuel
        else:
            etudiant.semestre_actuel = None

    data = {
        'etudiants': etudiants,
        'semestres': semestres,
        'etudiants_insuffisants': etudiants_insuffisants,
        'niveau': niveau,
        'selected_semestre': semestres_selected
    }

    return render(request, 'etudiants/liste_etudiants_par_semestre.html', context=data)


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.change_etudiant")
# Vue permettant le passage des étudiants au semestre suivant dans l'année universitaire courante
def passage_etudiants(request):
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

        # Vérifie combien de semestres l'étudiant est déjà inscrit et le nombre de crédits obtenus
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

            # Vérification du nombre de semestres déjà inscrits ainsi que le nombre de crédits obtenus
            if semestres_deja_inscrits >= 2:
                return render(request, 'etudiants/message_erreur.html', {'message': "Impossible de passer dans plus de deux semestres différents au cours d'une même année universitaire."})

            elif credits_obtenus == 0:
                return render(request, 'etudiants/message_erreur.html', {'message': "L'étudiant ne peut pas passer au semestre suivant avec 0 crédit."})

            # Ajoutez la saisie de la décision du conseil ici
            decision_conseil = request.POST.get(
                'decision_conseil_' + etudiant_id)
            etudiant.decision_conseil = decision_conseil
            etudiant.passer_semestre_suivant = True
            etudiant.save()

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

       # id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
        return redirect('main:etudiants')

    return render(request, 'etudiants/liste_etudiants_par_semestre.html')


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.view_tuteur")
def tuteurs(request):
    # Obtenez l'année universitaire courante
    annee_courante = AnneeUniversitaire.static_get_current_annee_universitaire()

    if annee_courante != "-":
        # Obtenez tous les tuteurs associés aux étudiants de l'année universitaire courante
        tuteurs = Tuteur.objects.all()

    context = {
        'tuteurs': tuteurs,
    }
    return render(request, 'tuteurs/tuteurs.html', context)


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.view_tuteur")
def detailTuteur(request, id):  # Retourne le détail d'un tuteur donnée
    tuteur = get_object_or_404(Tuteur, id=id)
    return render(request, "tuteurs/detailTuteur.html", {"tuteur": tuteur})


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.add_tuteur")
def create_tuteur(request, id=0):  # Création et modification d'un tuteur
    if request.method == "GET":
        if id == 0:
            form = TuteurForm()
        else:
            tuteur = Tuteur.objects.get(pk=id)
            form = TuteurForm(instance=tuteur)
        return render(request, 'tuteurs/create_tuteur.html', {'form': form})
    else:
        if id == 0:
            form = TuteurForm(request.POST)
        else:
            tuteur = Tuteur.objects.get(pk=id)
            form = TuteurForm(request.POST, instance=tuteur)
        if form.is_valid():
            form.save()
            return redirect('main:liste_des_tuteurs')


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.view_matiere")
def matieres(request):
    id_annee_selectionnee = request.session.get("id_annee_selectionnee")
    annee_universitaire = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)
    niveau = "IFNTI"
    semestres = annee_universitaire.semestre_set.all()
    semestres_selected = semestres

    if 'semestre' in request.GET:
        semestre_id = request.GET.get('semestre')
        if semestre_id != "":
            semestres_selected = semestres.filter(pk=semestre_id)

    matieres = Matiere.objects.filter(
        ue__programme__semestre__in=semestres_selected).distinct()

    for matiere in matieres:
        matiere.nb_evaluations = matiere.count_evaluations(
            annee_universitaire, semestres_selected)

    try:
        semestres_selected = semestres_selected.get()
    except:
        semestres_selected = semestres_selected[0]

    data = {
        'matieres': matieres,
        'semestres': semestres,
        'niveau': niveau,
        'selected_semestre': semestres_selected,
    }
    return render(request, 'matieres/matieres.html', context=data)


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.view_matiere")
def detailMatiere(request, id):
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
    if request.method == "GET":
        if id == 0:
            form = MatiereForm()
        else:
            matiere = Matiere.objects.get(pk=id)
            form = MatiereForm(instance=matiere)
        return render(request, 'matieres/create_matiere.html', {'form': form})
    else:
        if id == 0:
            form = MatiereForm(request.POST)
        else:
            matiere = Matiere.objects.get(pk=id)
            form = MatiereForm(request.POST, instance=matiere)
        if form.is_valid():
            form.save()
            #id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
            return redirect('main:matieres_etudiant')


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.view_matiere")
def matiere_semestre(request, semestre):
    # Vue pour récupérer la liste des matières par semestre
    try:
        annee_courante = AnneeUniversitaire.static_get_current_annee_universitaire()
        semestre_obj = Semestre.objects.get(
            libelle=f'S{semestre}', annee_universitaire=annee_courante)
        annee_accademique_courante = AnneeUniversitaire.objects.get(
            annee_courante=True)
        programmes = Programme.objects.filter(semestre=semestre_obj)
        ues = [programme.ue for programme in programmes]
        matieres_semestre = set()
        for ue in ues:
            matieres_semestre.update(ue.matiere_set.all())
        # matieres_semestre = Matiere.objects.filter(ue__semestre=semestre_obj)
        template_name = f'matieres/matiere_semestre{semestre}.html'
        # return HttpResponse("It's Okay")
    except Semestre.DoesNotExist:
        matieres_semestre = []
    context = {
        'matieres_semestre': matieres_semestre
    }
    return render(request, 'matieres/matiere_par_semestre.html', context)


def ues_etudiants(request):
    role = get_user_role(request)
    id_annee_selectionnee = request.session.get("id_annee_selectionnee")
    annee_universitaire = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)
    semestres = annee_universitaire.semestre_set.all()
    semestres_selected = semestres

    if role.name == "etudiant":
        titre_section = "Mes Ues"
    elif role.name == "enseignant" or role.name == "directeur_des_etudes" or role.name == "secretaire":
        titre_section = "Nos Ues"

    if 'semestre' in request.GET:
        semestre_id = request.GET.get('semestre')
        semestres_selected = semestres.filter(pk=semestre_id)

    matieres = Ue.objects.filter(programme__semestre__in=semestres_selected)

    if len(semestres_selected) == 1:
        semestres_selected = semestres_selected.get()

    data = {
        'ues': matieres,
        'semestres': semestres,
        'titre_section': titre_section,
        'selected_semestre': semestres_selected,
    }
    return render(request, 'ues/ues.html', context=data)


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.view_ue")
def ues(request):
    # Récupérer l'année universitaire courante
    annee_universitaire_courante = AnneeUniversitaire.static_get_current_annee_universitaire()

    if annee_universitaire_courante != "-":
        # Filtrer les UE associées à l'année universitaire courante
        ues_annee_courante = Ue.objects.filter(
            programme__semestre__annee_universitaire=annee_universitaire_courante)
    else:
        ues_annee_courante = []

    return render(request, 'ues/ues.html', {'ues': ues_annee_courante})


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.view_ue")
def detailUe(request, id):
    ue = get_object_or_404(Ue, id=id)
    return render(request, "ues/detailUe.html", {"ue": ue})


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.add_ue")
def create_ue(request, id=0):
    if request.method == "GET":
        if id == 0:
            form = UeForm()
        else:
            ue = Ue.objects.get(pk=id)
            form = UeForm(instance=ue)
        return render(request, 'ues/create_ue.html', {'form': form})
    else:
        if id == 0:
            form = UeForm(request.POST)
        else:
            ue = Ue.objects.get(pk=id)
            form = UeForm(request.POST, instance=ue)
        if form.is_valid():
            form.save()
            return render(request, 'etudiants/message_erreur.html', {'message': "Veuillez le ratacher à gestion maquette."})


@login_required(login_url=settings.LOGIN_URL)
@permission_required("main.view_ue")
def ues_semestre(request, semestre):
    annee_courante = AnneeUniversitaire.static_get_current_annee_universitaire()
    semestre_obj = Semestre.objects.get(
        libelle=semestre, annee_universitaire=annee_courante)
    programmes = Programme.objects.filter(semestre=semestre_obj)
    ues = [programme.ue for programme in programmes]
    context = {"ues": ues}
    return render(request, 'ues/ues_par_semestre.html', context)


# @login_required(login_url=settings.LOGIN_URL)
# @permission_required("main.view_etudiant")
# def etudiants_par_niveau(request, niveau):
#     semestres = set()
#     if niveau == 1:
#         semestres_names = ['S1', 'S2']
#     elif niveau == 2:
#         semestres_names = ['S3', 'S4']
#     elif niveau == 3:
#         semestres_names = ['S5', 'S6']

#     etudiants, semestres = Etudiant.get_Ln(semestres=semestres_names)
#     semestres = list(semestres)
#     data = {}
#     data['niveau'] = f'L{niveau}'
#     if etudiants and semestres:
#         data['etudiants'] = etudiants
#         data['semestres'] = semestres
#     return render(request, 'etudiants/listln.html', data)


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
    if request.user.groups.all().first().name not in ['directeur_des_etudes', 'secretaire']:
        return render(request, 'errors_pages/403.html')

    etudiant = get_object_or_404(Etudiant, id=id)

    context = {'etudiant': etudiant, 'niveau': niveau}

    latex_input = 'carte_etudiant'
    latex_ouput = 'generated_carte_etudiant'
    pdf_file = 'pdf_carte_etudiant'

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
def carte_etudiant_all(request, niveau):
    if request.user.groups.all().first().name not in ['directeur_des_etudes', 'secretaire']:
        return render(request, 'errors_pages/403.html')

    id_annee_selectionnee = request.session["id_annee_selectionnee"]
    annee_universitaire = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)

    semestre = Semestre.objects.filter(id=niveau)
    if semestre:
        semestres = [semestre.get().libelle]
    elif niveau == "__all__":
        semestres = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']

    etudiants, semestre = Etudiant.get_Ln(semestres, annee_universitaire=None)
    for etudiant in etudiants:
        etudiant.niveau, _ = etudiant.get_niveau_annee(annee_universitaire)

    # ajout des étudiants dans le dictionnaire
    context = {'etudiants': etudiants, 'niveau': "niveau"}

    latex_input = 'carte_etudiant_all'
    latex_ouput = 'generated_carte_etudiant_all'
    pdf_file = 'pdf_carte_etudiant_all'

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

    if request.user.groups.all().first().name not in ['directeur_des_etudes']:
        return render(request, 'errors_pages/403.html')

    etudiant = get_object_or_404(Etudiant, id=id)

    context = {'etudiant': etudiant}

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
def diplome_etudiant_all(request):
    if request.user.groups.all().first().name not in ['directeur_des_etudes', 'secretaire']:
        return render(request, 'errors_pages/403.html')

    semestres = Semestre.objects.filter(
        libelle="S5") | Semestre.objects.filter(libelle="S6")
    temp = []

    # récupération des étudiants de chaque semestres
    for semestre in semestres:
        for etudiant in semestre.etudiant_set.all():
            # ajout de tout les étudiant du semestre dans un tableau temporaire
            temp.append(etudiant)

    # ajout des étudiants dans le dictionnaire
    context = {'etudiants': temp}

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

    if request.user.groups.all().first().name not in ['directeur_des_etudes', 'secretaire']:
        return render(request, 'errors_pages/403.html')

    etudiant = get_object_or_404(Etudiant, id=id)

    context = {'etudiant': etudiant, 'niveau': niveau}

    # nom des fichiers d'entrée et de sortie
    # ici pour les test le nom se termine en temp pour signifier temporaire
    # ils seront donc à supprimer
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


@login_required(login_url=settings.LOGIN_URL)
# methode générant le relevé de notes de l'étudiant
def releve_notes(request, id, id_semestre):
    if request.user.groups.all().first().name not in ['directeur_des_etudes', 'secretaire', 'etudiant']:
        return render(request, 'errors_pages/403.html')

    etudiant = get_object_or_404(Etudiant, id=id)
    semestre = get_object_or_404(Semestre, id=id_semestre)
    context = {}

    if request.user.groups.all().first().name == 'etudiant':
        if request.user.etudiant and request.user.etudiant != etudiant:
            return render(request, 'errors_pages/403.html')

    # récupération des ues du semestre
    semestre_ues = semestre.get_all_ues()
    ues = []
    for ue in semestre_ues:
        moyenne, validation = etudiant.moyenne_etudiant_ue(ue, semestre)
        ues.append({'ue': ue, 'moyenne': round(
            moyenne, 2), 'validation': validation})

    # calcul du nombre de crédits obtenus par l'étudiant
    credits_obtenus = 0
    for ue in ues:
        if ue['validation'] == True:
            credits_obtenus += ue['ue'].nbreCredits

    context['ues'] = ues
    context['credits_obtenus'] = credits_obtenus
    context['etudiant'] = etudiant
    context['semestre'] = semestre
    context['annee'] = AnneeUniversitaire.static_get_current_annee_universitaire()

    # nom des fichiers d'entrée et de sortie

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

    if request.user.groups.all().first().name not in ['directeur_des_etudes', 'secretaire']:
        return render(request, 'errors_pages/403.html')

    semestre = get_object_or_404(Semestre, id=id_semestre)
    etudiants = semestre.etudiant_set.all().order_by('nom', 'prenom')

    # récupération des ues du semestre
    semestre_ues = semestre.get_all_ues()

    # tableau contenant l'ensemble des relevés de notes
    releves_notes_tab = []

    for etudiant in etudiants:
        # tableau contenant les données correspondant au relevé de notes d'un étudiant
        releve_note = {}
        releve_note['lignes'] = []
        credits_obtenus = 0
        for ue in semestre_ues:
            moyenne, validation = etudiant.moyenne_etudiant_ue(ue, semestre)
            releve_note['lignes'].append(
                {'ue': ue, 'moyenne': round(
                    moyenne, 2), 'validation': validation}
            )
            # calcul de nombre de crédits obtenus
            if validation:
                credits_obtenus += ue.nbreCredits

        releve_note['credits_obtenus'] = credits_obtenus
        releve_note['etudiant'] = etudiant
        releves_notes_tab.append(releve_note)

    context = {}

    context['annee'] = AnneeUniversitaire.static_get_current_annee_universitaire()
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
def releve_notes_detail(request, id, id_semestre):

    if request.user.groups.all().first().name not in ['directeur_des_etudes', 'secretaire', 'etudiant']:
        return render(request, 'errors_pages/403.html')

    semestre = get_object_or_404(Semestre, id=id_semestre)
    etudiant = get_object_or_404(Etudiant, id=id)

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
        'nbre_colonnes': nbre_colonnes,
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


# relevé de note détailé de tous les élèves du semestre
@login_required(login_url=settings.LOGIN_URL)
def releve_notes_details_all(request, id_semestre):

    if request.user.groups.all().first().name not in ['directeur_des_etudes', 'secretaire']:
        return render(request, 'errors_pages/403.html')

    semestre = get_object_or_404(Semestre, id=id_semestre)
    etudiants = semestre.etudiant_set.all()

    nbre_colonnes = 2

    colonnes = '|c|c|'

    semestre_ues = semestre.get_all_ues()

    colonnes += 'c|' * len(semestre_ues)

    nbre_colonnes += len(semestre_ues)

    nbre_ues = len(semestre_ues)

    # récupération du nombre de matières par ue

    for ue in semestre_ues:
        # ajout des colonnes correspondant aux matières
        nbre_matieres = len(ue.matiere_set.all())
        colonnes += 'c|' * nbre_matieres
        nbre_colonnes += nbre_matieres

    # récupératon des données pour chaque lignes du relevé
    lignes_releve = []
    # boucle sur chaque étudiant piour constituer la ligne associée à l'étudiant
    for etudiant in etudiants:
        ligne = {}
        ligne['etudiant'] = etudiant
        # tableau contenant l'ensemble des UEs de l'étudiant
        ues = []
        # boucle sur chaque UE suivies par l'étudiant pour calculersa mmoyenne et sa moyenne dans chaque matières
        for ue in semestre_ues:
            # tableau contenant l'ensemble des matières suivies par l'étudiant
            matieres = []
            nbre_matieres = len(ue.matiere_set.all())
            for matiere in ue.matiere_set.all():
                # récupération des matières de l'ue et la moyenne de l'étudiant dans celles-ci
                matieres.append({'matiere': matiere, 'moyenne_matiere': round(
                    etudiant.moyenne_etudiant_matiere(matiere, semestre)[0], 2)})
            ues.append({'ue': ue, 'moyenne': round(etudiant.moyenne_etudiant_ue(ue, semestre)[
                       0], 2), 'matieres_ue': matieres, 'nbre_matieres': nbre_matieres + 1})
        ligne['ues'] = ues
        lignes_releve.append(ligne)

    context = {
        'nbre_ues': nbre_ues,
        'nbre_colonnes': nbre_colonnes,
        'colonnes': colonnes,
        'lignes': lignes_releve,
        'nbre_lignes': len(lignes_releve)
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
# methode générant le récapitulatif des notes du semestre
def recapitulatif_notes(request, id_matiere, id_semestre):
    print(request.user.groups.all().first().name)
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

    semestre = get_object_or_404(Semestre, pk=id_semestre)
    matiere = get_object_or_404(Matiere, pk=id_matiere)
    etudiants = semestre.etudiant_set.all()
    data = {
        'evaluations': matiere.evaluation_set.all(),
        'etudiants': [],
        'matiere': matiere,
        'semestre': semestre,
    }

    for etudiant in etudiants:
        moyenne, a_valider = etudiant.moyenne_etudiant_matiere(
            matiere, semestre)
        data['etudiants'].append({
            'full_name': etudiant.full_name(),
            'notes': etudiant.notes_etudiant_matiere(matiere, semestre),
            'moyenne': moyenne,
            'a_valider': a_valider,
        })

    return render(request, 'evaluations/recapitulatifs_des_notes.html', context=data)


@login_required(login_url=settings.LOGIN_URL)
def evaluations_etudiant(request, id_matiere, id_etudiant):
    """
    Affiche la liste des évaluations d'un étudiant
    """
    id_annee_selectionnee = request.session["id_annee_selectionnee"]
    matiere = get_object_or_404(Matiere, pk=id_matiere)
    etudiant = get_object_or_404(Etudiant, pk=id_etudiant)
    annee_universitaire = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)

    if 'semestre' in request.GET and request.GET.get('semestre') != "":
        id = request.GET.get('semestre')
        semestre = get_object_or_404(Semestre, pk=id)
    else:
        semestre = matiere.get_semestres(annee_universitaire, '__all__')[0]

    evaluations = Evaluation.objects.filter(
        matiere=matiere, semestre=semestre, rattrapage__in=[True, False])

    evaluations_dict = []
    for evaluation in evaluations:
        data = {
            'id': evaluation.id,
            'date': evaluation.date,
            'libelle': evaluation.libelle,
            'ponderation': evaluation.ponderation,
            'note': evaluation.note_set.get(etudiant=etudiant).valeurNote,
        }

        evaluations_dict.append(data)

    semestres = etudiant.semestres.all()
    data = {
        'annee_courrante': '',
        'matiere': matiere,
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
    annee_universitaire = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)
    if 'semestre' in request.GET and request.GET.get('semestre') != "":
        id = request.GET.get('semestre')
        semestre = get_object_or_404(Semestre, pk=id)
    else:
        semestre = Semestre.objects.filter(
            annee_universitaire=annee_universitaire, libelle="S1")
        if semestre:
            semestre = semestre.get()
    semestres = [semestre]

    evaluations = Evaluation.objects.filter(
        matiere=matiere, semestre__in=semestres, rattrapage__in=[True, False])
    semestres = matiere.get_semestres(
        annee_selectionnee=annee_universitaire, type='__all__')

    data = {
        'matiere': matiere,
        'evaluations': evaluations,
        'semestres': semestres,
        'selected_semestre': semestre,
    }
    return render(request, 'evaluations/index.html', data)


@login_required(login_url=settings.LOGIN_URL)
def createNotesByEvaluation(request, id_matiere, rattrapage, id_semestre):
    """
    Affiche un formulaire de création d'une évaluation et ensuite d'une note :model:`main.Note` selon la matière.
    """
    # Rechercher la matière
    matiere = get_object_or_404(Matiere, pk=id_matiere)
    annee_universitaire = AnneeUniversitaire.static_get_current_annee_universitaire()
    semestre = get_object_or_404(Semestre, pk=id_semestre)
    if matiere.dans_semestre(semestre):
        # Chercher les étudiants qui suivent la matière
        if rattrapage:
            etudiants = matiere.get_etudiants_en_rattrapage()
        else:
            if not matiere.is_available_to_add_evaluation(semestre):
                return redirect('main:evaluations', id_matiere=matiere.id)
            etudiants = semestre.etudiant_set.all()

        # NoteFormSet = forms.modelformset_factory(
        #     Note, form=NoteForm, extra=len(etudiants))
        NoteFormSet = forms.inlineformset_factory(
            parent_model=Evaluation,
            model=Note,
            form=NoteForm,
            extra=len(etudiants),
            can_delete=False,
            min_num=0,
            validate_min=True,
        )
        queryset = Note.objects.none()

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
                return redirect('main:evaluations', id_matiere=matiere.id)
        else:
            evaluation_form = EvaluationForm()
            initial_etudiant_note_data = [
                {'etudiant': etudiant.id, 'etudiant_full_name': etudiant} for etudiant in etudiants]
            note_form_set = NoteFormSet(
                initial=initial_etudiant_note_data, queryset=queryset)
        data = {
            'evaluation_form': evaluation_form,
            'notes_formset': note_form_set,
            'matiere': matiere,
            'ponderation_possible': matiere.ponderation_restante(semestre),
            'rattrapage': rattrapage,
            'old_path': request.path,
        }
        return render(request, 'notes/create_or_edit_note.html', context=data)
    return redirect('main:evaluations', id_matiere=matiere.id)


@login_required(login_url=settings.LOGIN_URL)
def editeNoteByEvaluation(request, id):
    """
    Affiche un formulaire d'édition d'une note :model:`main.Note`.
    """
    # Rechercher l'evaluation
    evaluation = get_object_or_404(Evaluation, pk=id)
    matiere = evaluation.matiere
    semestre = evaluation.semestre
    # Définir la class NoteFormSet
    NoteFormSet = forms.inlineformset_factory(
        parent_model=Evaluation,
        model=Note,
        form=NoteForm,
        extra=0,
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
            return redirect('main:evaluations', id_matiere=matiere.id)
    else:
        evaluation_form = EvaluationForm(instance=evaluation)
        # Créer une instance de d'ensemble de formulaire selon notre queryset
        note_form_set = NoteFormSet(instance=evaluation)
        for form in note_form_set:
            etudiant = Etudiant.objects.filter(
                id=form.initial['etudiant']).get()
            form.initial['etudiant_full_name'] = etudiant

    data = {
        'evaluation_form': evaluation_form,
        'notes_formset': note_form_set,
        'matiere': matiere,
        'rattrapage': evaluation.rattrapage,
        'ponderation_possible': matiere.ponderation_restante(semestre=semestre)+evaluation.ponderation,
    }

    return render(request, 'notes/create_or_edit_note.html', context=data)


@login_required(login_url=settings.LOGIN_URL)
def deleteEvaluation(request, id):
    """
    Supprime une evaluation :model:`main.Note`.

    **Context**

    ``evaluation``
        une instance du :model:`main.Note`.
    """
    evaluation = get_object_or_404(Evaluation, pk=id)
    matiere = evaluation.matiere
    evaluation.delete()
    return redirect('main:evaluations', id_matiere=matiere.id)

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
        notification ={"message":"Informations modifier avec succés.","type":"succes"}
        context = {"utilisateur": user,"notification": notification,  'page_is_not_profil' : False,} 
        return render(request, "connexion/edit_profil.html",context)
    
    else:
        user=request.user
        return render(request, "connexion/edit_profil.html",{"utilisateur": user, 'page_is_not_profil' : False,})


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
            notification ={"message":"Mot de passe modifier avec succés.","type":"succes"}
        else :
            notification={"message":" Le nouveau mot de passe et sa confirmation ne concordent pas","type":"erreur"}
    else :
        notification={"message":"Ancien mot de passe incorrect","type":"erreur"}
    return render(request, "connexion/edit_profil.html",{"notification": notification,  'page_is_not_profil' : False,})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('login-username')
        password = request.POST.get('login-password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('/')
        else:
            return render(request, "connexion/login.html", {'error': 'Identifiants invalides'})

    return render(request, "connexion/login.html")


def recuperation_mdp(request):
    if request.method == "POST":
        username = request.POST.get('username')
        notification = {
            "message": "Cet utilisateur n'existe pas", "type": "erreur"}
        try:
            user = get_user_model().objects.get(username=username)
        except:
            user = None

        if user is None:
            return render(request, "connexion/reminder.html", {"notification": notification})

        else:
            password = get_user_model().objects.make_random_password()
            user.set_password(password)
            user.save()
            data = {
                "service_id": 'service_fsp0sli',
                "template_id": 'template_mdp',
                "user_id": '-0Y7bdMio60EQTeR-',
                "template_params": {
                    "user_mail": user.email,
                    "password": password,
                    "user_name": user.username + ' ' + user.first_name + ' ' + user.last_name
                }

            }
            notify = "succes"
            notify = json.dumps(notify)
            jsondata = json.dumps(data)
            notification = {"message": "Mot de passe modifié avec succes , il vous sera envoyé sur votre adresse mail ,veuillez vous connecter à votre adresse  " +
                            user.email + " pour recuper votre mot de passe temporaire", "type": "succes"}

            return render(request, "connexion/reminder.html", {"notification": notification, "formData": jsondata, "notify": notify})

    return render(request, "connexion/reminder.html")


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

            #id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
            return redirect('main:enseignants')

        else:
            return render(request, "enseignants/create_enseignant.html", {'form': form})


@login_required(login_url=settings.LOGIN_URL)
def enseignants(request):
    id_annee_selectionnee = request.session.get("id_annee_selectionnee")
    role = get_user_role(request)
    annee_universitaire = get_object_or_404(
        AnneeUniversitaire, pk=id_annee_selectionnee)
    enseignants = Enseignant.objects.filter(
        annee_universitaire=annee_universitaire, is_active=True)
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
        if role.name == "etudiant" or role.name == "enseignant" :
            niveau = "Mes enseignants"
            if role.name == "enseignant":
                niveau = "Mes collegues"
            enseignants = Enseignant.objects.filter(
                is_active=True, matiere__ue__programme__semestre__in=semestres_selected).distinct()
        elif role.name == "directeur_des_etudes" or role.name == "comptable" :
            if role.name == "comptable":
                niveau = "Mes collegues"
            niveau = "Nos Enseignants"
            if semestre_id == "__all__":
                enseignants = Enseignant.objects.filter(
                    is_active__in=etats_selected)
            else:
                enseignants = Enseignant.objects.filter(
                    is_active__in=etats_selected, matiere__ue__programme__semestre__in=semestres_selected).distinct()

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
def liste_informations_enseignants(request, id_annee_selectionnee):
    annee_universitaire = AnneeUniversitaire.objects.get(
        pk=id_annee_selectionnee)
    informations_enseignants = Information.objects.filter(
        enseignant__annee_universitaire=annee_universitaire)
    context = {
        'annee_universitaire': annee_universitaire,
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

            id_annee_selectionnee = AnneeUniversitaire.static_get_current_annee_universitaire().id
            return redirect('main:liste_informations_enseignants', id_annee_selectionnee=id_annee_selectionnee)

        else:
            return render(request, "informations/enregistrer_informations.html", {'form': form})


@login_required(login_url=settings.LOGIN_URL)
# Cette vue affiche la liste des semestre courants
def semestres(request):
    annee_universitaire_courante = AnneeUniversitaire.static_get_current_annee_universitaire()
    semestres = Semestre.objects.filter(
        annee_universitaire=annee_universitaire_courante)
    context = {
        "semestres": semestres,
        "annee_universitaire_courante": annee_universitaire_courante,
    }
    return render(request, 'semestres/semestres.html', context)


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


# Cette vue permet d'importer les données via un fichier excel
def importer_les_donnees(request):
    if request.method == 'POST':
        if 'myfile' not in request.FILES:
            return render(request, 'etudiants/message_erreur.html', {'message': "Aucun fichier sélectionné."})
        # Assurez-vous d'importer votre ressource EtudiantResource
        etudiants_resource = EtudiantResource()
        dataset = Dataset()
        etudiant = request.FILES['myfile']

        try:
            imported_data = dataset.load(etudiant.read(), format='xlsx')
            for data in imported_data:
                etudiant = Etudiant(
                    nom=data[0],
                    prenom=data[1],
                    sexe=data[2],
                    datenaissance=data[3],
                    lieunaissance=data[4],
                    contact=data[5],
                    email=data[6],
                    adresse=data[7],
                    prefecture=data[8],
                    is_active=data[9],
                    carte_identity=data[10],
                    nationalite=data[11],
                    user=data[12],
                    photo_passport=data[13],
                    id=data[14],
                    seriebac1=data[15],
                    seriebac2=data[16],
                    anneeentree=data[17],
                    anneebac1=data[18],
                    anneebac2=data[19],
                    etablissementSeconde=data[20],
                    francaisSeconde=data[21],
                    anglaisSeconde=data[22],
                    mathematiqueSeconde=data[23],
                    etablissementPremiere=data[24],
                    francaisPremiere=data[25],
                    anglaisPremiere=data[26],
                    mathematiquePremiere=data[27],
                    etablissementTerminale=data[28],
                    francaisTerminale=data[29],
                    anglaisTerminale=data[30],
                    mathematiqueTerminale=data[31],
                    delegue=data[32],
                    passer_semestre_suivant=data[33],
                    decision_conseil=data[34],
                    profil=data[35]
                )
                etudiant.save()

                # Trouvez l'année universitaire en cours
                annee_universitaire_courante = AnneeUniversitaire.objects.get(
                    annee_courante=True)

                # Attachez l'étudiant au Semestre 1 (S1) de l'année universitaire en cours
                semestre_s1 = annee_universitaire_courante.semestre_set.get(
                    libelle='S1')
                etudiant.semestres.add(semestre_s1)

                semestres_data = data[36:]
                for semestre_data in semestres_data:
                    try:
                        semestre = Semestre.objects.get(libelle=semestre_data)
                        etudiant.semestres.add(semestre)
                    except Semestre.DoesNotExist:
                        # Gérer cette situation si le semestre n'existe pas
                        print(f"Le semestre '{semestre_data}' n'existe pas.")
                return render(request, 'etudiants/message_erreur.html', {'message': "Données importées avec succès."})

        except Exception as e:
            return render(request, 'etudiants/message_erreur.html', {'message': "Erreur lors de l'importation du fichier Excel."})

    return render(request, 'etudiants/importer.html')


# Cette vue permet d'importer les données etudiants via un fichier xlsx
def importer_data(request):
    if request.method == 'POST':
        if 'myfile' not in request.FILES:
            return render(request, 'etudiants/message_erreur.html', {'message': "Aucun fichier sélectionné."})

        etudiants_resource = EtudiantResource()
        dataset = Dataset()
        etudiant = request.FILES['myfile']

        imported_data = list(dataset.load(etudiant.read(), format='xlsx'))

        for data in imported_data[1:112]:
            print(data[0], data[2], data[3], data[4], data[5], data[6], data[7], data[28],
                  data[29], data[30], data[31], data[32], data[33], data[34], data[35])
            etudiant = Etudiant(
                anneeentree=data[0],
                nom=data[2],
                prenom=data[3],
                # datenaissance=data[4],
                lieunaissance=data[5],
                sexe=data[6],
                anneebac2=data[7],
                contact=data[1],
                email=data[29],
                adresse=data[30],
                user=data[32],
                photo_passport=data[33],
                id=data[34],
                is_active=True,
            )
            try:
                etudiant.save()
                print(etudiant.user.username)
                annee_universitaire = AnneeUniversitaire.objects.get(
                    annee=etudiant.anneeentree)

                semestres_data = data[8]
                if semestres_data == "L1":
                    # Si "L1"
                    semestre_s1 = annee_universitaire.semestre_set.get(
                        libelle='S1')
                    semestre_s2 = annee_universitaire.semestre_set.get(
                        libelle='S2')
                    etudiant.semestres.add(semestre_s1, semestre_s2)
                elif semestres_data == "S3":
                    # Si "S3"
                    semestre_s1 = annee_universitaire.semestre_set.get(
                        libelle='S1')
                    semestre_s2 = annee_universitaire.semestre_set.get(
                        libelle='S2')
                    etudiant.semestres.add(semestre_s1, semestre_s2)

                    annee_entree_plus_un = etudiant.anneeentree + 1
                    annee_universitaire_plus_un = AnneeUniversitaire.objects.get(
                        annee=annee_entree_plus_un)

                    semestre_s3 = annee_universitaire_plus_un.semestre_set.get(
                        libelle='S3')
                    etudiant.semestres.add(semestre_s3)
                elif semestres_data == "L2":
                    # Si "L2"
                    semestre_s1 = annee_universitaire.semestre_set.get(
                        libelle='S1')
                    semestre_s2 = annee_universitaire.semestre_set.get(
                        libelle='S2')
                    etudiant.semestres.add(semestre_s1, semestre_s2)

                    annee_entree_plus_un = etudiant.anneeentree + 1
                    annee_universitaire_plus_un = AnneeUniversitaire.objects.get(
                        annee=annee_entree_plus_un)

                    semestre_s3 = annee_universitaire_plus_un.semestre_set.get(
                        libelle='S3')
                    semestre_s4 = annee_universitaire_plus_un.semestre_set.get(
                        libelle='S4')
                    etudiant.semestres.add(semestre_s3, semestre_s4)
                elif semestres_data == "S5":
                    # Si "S5"
                    semestre_s1 = annee_universitaire.semestre_set.get(
                        libelle='S1')
                    semestre_s2 = annee_universitaire.semestre_set.get(
                        libelle='S2')
                    etudiant.semestres.add(semestre_s1, semestre_s2)

                    annee_entree_plus_un = etudiant.anneeentree + 1
                    annee_universitaire_plus_un = AnneeUniversitaire.objects.get(
                        annee=annee_entree_plus_un)

                    semestre_s3 = annee_universitaire_plus_un.semestre_set.get(
                        libelle='S3')
                    semestre_s4 = annee_universitaire_plus_un.semestre_set.get(
                        libelle='S4')
                    etudiant.semestres.add(semestre_s3, semestre_s4)

                    annee_entree_plus_deux = etudiant.anneeentree + 2
                    annee_universitaire_plus_deux = AnneeUniversitaire.objects.get(
                        annee=annee_entree_plus_deux)

                    semestre_s5 = annee_universitaire_plus_deux.semestre_set.get(
                        libelle='S5')
                    etudiant.semestres.add(semestre_s5)
                elif semestres_data == "L3":
                    # Si "L3"
                    semestre_s1 = annee_universitaire.semestre_set.get(
                        libelle='S1')
                    semestre_s2 = annee_universitaire.semestre_set.get(
                        libelle='S2')
                    etudiant.semestres.add(semestre_s1, semestre_s2)

                    annee_entree_plus_un = etudiant.anneeentree + 1
                    annee_universitaire_plus_un = AnneeUniversitaire.objects.get(
                        annee=annee_entree_plus_un)

                    semestre_s3 = annee_universitaire_plus_un.semestre_set.get(
                        libelle='S3')
                    semestre_s4 = annee_universitaire_plus_un.semestre_set.get(
                        libelle='S4')
                    etudiant.semestres.add(semestre_s3, semestre_s4)

                    annee_entree_plus_deux = etudiant.anneeentree + 2
                    annee_universitaire_plus_deux = AnneeUniversitaire.objects.get(
                        annee=annee_entree_plus_deux)

                    semestre_s5 = annee_universitaire_plus_deux.semestre_set.get(
                        libelle='S5')
                    semestre_s6 = annee_universitaire_plus_deux.semestre_set.get(
                        libelle='S6')
                    etudiant.semestres.add(semestre_s5, semestre_s6)
                else:
                    # Sinon, attachez l'étudiant au Semestre 1 (S1) de l'année universitaire en cours
                    semestre_s1_courant = annee_universitaire.semestre_set.get(
                        libelle='S1')
                    etudiant.semestres.add(semestre_s1_courant)
            except Exception as e:
                pass

        return render(request, 'etudiants/message_erreur.html', {'message': "Données importées avec succès."})

    return render(request, 'etudiants/importer.html')
