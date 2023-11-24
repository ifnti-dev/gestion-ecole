from django.shortcuts import get_object_or_404
from main.models import Enseignant, Etudiant, Evaluation, Matiere, Note, Programme, Ue


# MAIN HELPER FUNCTIONS

"""
    Ce fichier correspond à des fonctions (d'aide) pouvant être appelés 
    à n'importe quel endroit de l'application. Dans ce fichier seront 
    donc définies toutes les fonctions qui serviront au développement
"""


def get_user_role(request):
    return request.user.groups.all().first()


def get_authenticate_profile_path(request, id):
    role = get_user_role(request)
    if role:
        role = role.name
        if role == "etudiant":
            return f'main/detail_etudiant/{id}/'
        if role == "enseignant":
            return f'main/enseignant_detail/{id}/'
    return ""


def get_id_authenticate_user_model(request):
    role = get_user_role(request)
    if role:
        role = role.name
        if role == "etudiant":
            return Etudiant.objects.get(user=request.user).id
        if role == "enseignant":
            return Enseignant.objects.get(user=request.user).id
    return 0


# cette fonction retourne de manière formatée l'ensemble des matières d'un ensemble d'UEs
"""
    paramètre(s) : tableau de dictionnaire d'UEs
    retour : tableau de dictionnaire d'UE avec une valeur en plus tableau de dictionnaire de matière
"""


def get_all_ues_matieres(ues_list):
    # ici nous parcourons l'ensemble de nos ue pour récupérer leur ensemble de matières
    for ue in ues_list:
        # nous récupérons l'objet UE en base afin de récupérer les matières
        get_ue = get_object_or_404(Ue, id=ue['id'])
        # création du tableau de dictionnaire de matières
        ue_matieres = get_ue.matiere_set.all()
        # création du tableau de matières de l'UE
        tab_matiere_temp = []
        for matiere in ue_matieres:
            # création des dictionnaires temporaires
            dict_matiere_temp = {'id': matiere.id, 'codematiere': matiere.codematiere, 'libelle': matiere.libelle,
                                 'coefficient': matiere.coefficient, 'minValue': matiere.minValue, 'enseignant': matiere.enseignant, 'is_active': matiere.is_active}
            # ajout des dictionnaires au tableau de matières de l'UE
            tab_matiere_temp.append(dict_matiere_temp)
        # ajout du tableau de matière de l'UE au dictionnaire de l'UE
        ue['matieres'] = tab_matiere_temp
    return ues_list


# cette fonction retourne sous la forme d'un tableau de dictionnaire les evaluations d'une matière
"""
    paramètre(s) : Matiere matiere
    retour : tableau d'évaluations

"""


def get_all_matiere_evaluations(matiere):
    evaluations = matiere.evaluation_set.all()
    evaluations_tab = []
    for evaluation in evaluations:
        # création d'un dictionnaire temporaire et ajout de celui-ci au tableau d'évaluations
        temp_dict_evalution = {'id': evaluation.id, 'libelle': evaluation.libelle,
                               'date': evaluation.date, 'ponderation': evaluation.ponderation}
        evaluations_tab.append(temp_dict_evalution)
    return evaluations_tab


# cette fonction retourne l'ensemble des notes d'une évaluation
"""
    paramètre(s) : Evaluation evaluation
    retour : tableau de notes
"""


def get_evaluation_note(evaluation, etudiant):
    note = Note.objects.filter(etudiant=etudiant, evaluation=evaluation)
    # si pour l'étudiant donné il n'y a pas de note on lui assigne la valeur 0
    if note:
        return note[0].valeurNote
    return 0


# cette fonction permet de calculer la moyenne d'un étudiant dans une matière
"""
    paramètre(s) : Matiere matiere
    retour : Integer moyenne
"""


def get_matiere_moy(matiere, etudiant):
    # récupération de toutes évaluations de la matière
    evaluations = get_all_matiere_evaluations(matiere)
    # print(evaluations)
    notes = []
    # récupération de toutes les notes des évaluation de l'étudiant avec leur podération associée
    # si la matière ne compte pas d'évaluation la moyenne est de zéro par défaut
    if evaluations:
        for evaluation in evaluations:
            temp_dict_note = {}
            temp_dict_note['valeur'] = get_evaluation_note(
                get_object_or_404(Evaluation, id=evaluation['id']), etudiant)
            temp_dict_note['ponderation'] = evaluation['ponderation']
            notes.append(temp_dict_note)
    else:
        return 0

    # calcul de la moyenne
    somme_notes = 0
    somme_ponderations = 0
    for note in notes:
        # somme des notes pondérées
        somme_notes += note['valeur'] * note['ponderation']
        # somme des pondérations
        somme_ponderations += note['ponderation']
    return round(somme_notes / somme_ponderations, 2)


# vérification si l'ue est validée par l'étudiant ou non
"""
    paramètre(s) ; dict UE
    retour : boolean 
"""
# IMPORTANT : le paramètre en entrée correspond à un format de donnée bien défini dans la vue releve_notes()


def valid_UE(ue):
    for matiere in ue['matieres']:
        if matiere['moyenne'] < matiere['minValue']:
            return False
    return True


# calcul de la moyenne de l'UE
"""
    paramètre(s) : dict UE
    retour : None
"""

# IMPORTANT : le paramètre en entrée correspond à un format de donnée bien défini dans la vue releve_notes()


def get_ue_moy(ue):
    somme_moyenne = 0
    somme_coef = 0
    for matiere in ue['matieres']:
        somme_moyenne += float(matiere['moyenne']) * matiere['coefficient']
        somme_coef += matiere['coefficient']
    ue['moyenne'] = round(somme_moyenne / somme_coef, 2)
