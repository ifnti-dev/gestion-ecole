import re
from django.shortcuts import get_object_or_404
from main.models import AnneeUniversitaire, Enseignant, Etudiant, Evaluation, Matiere, Note, Programme, Ue, Semestre
from openpyxl import load_workbook
import os
from datetime import datetime, timedelta
import shutil 

CODE_UE = {
    'p_u_e_i_a': 'Politiques universitaires et intégrité académique', 
    'e': 'English', 
    'c_e_e_n': 'Communication et expression numérique', 
    'm_i_1': 'Mathématiques I',
    'm_i_2': 'Mathématiques II', 
    'f_d_t_e_s_d_i': "Fondement des TI et systèmes d'exploitation I", 
    'p_a_e_b_d_d': 'Programmation, algorithmes et bases de données', 
    'c_e_i_e_e': 'Communication et Insertion en entreprise', 
    'elec': 'Électronique', 
    'c_o_o_e_b_d_d': 'Conception orientée objet et base de données', 
    'c_e_d_d_s_w': 'Conception et développement des sites web', 
    'i_a_d_d': "Introduction au développement d'applications", 
    's_e_e_i_o_p_s_i_(_i': 'Stage en entreprise II OU Projets spéciaux II (Stage II)', 
    'c_e_g_d_e': 'Communication et gestion des entreprises', 
    'i_a_r': 'Introduction aux réseaux', 
    'i_e_i_1': 'Informatique embarquée I', 
    'i_e_i_2': 'Informatique embarquée II',
    'p_o_o_e_s_d_d': 'Programmation orienté objet et structuration des données', 
    'a_d_s_e_s_d_i': "Administration de serveur et systèmes d'exploitation II", 
    'r_e_i_à_l_s_i': 'Réseaux et Introduction à la sécurité informatique', 
    'c_e_d_d_a': 'Conception et développement des applications', 
    'i_g': 'Interfaces graphiques', 
    's_é_e_t': 'Sujets émergents en technologie', 
    'd_é_e_r_s_d_e': 'Droit, éthique et responsabilité sociale des entreprises', 
    'c_e_d_d_l': 'Conception et développement des logiciels', 
    'd_e_d_d_a_w': 'Développement et déploiement des applications web', 
    'd_e_d_d_a_m': 'Développement et déploiement des applications mobile', 
    'c_d_c_/_c_c_1': 'Cours de concentration / Cours complémentaire 1', 
    'c_d_c_/_c_c_2': 'Cours de concentration / Cours complémentaire 2', 
    'c_d_c_/_c_c_3': 'Cours de concentration / Cours complémentaire 3', 
    's_d_e_s_(_i': "Stage/Projets d'entreprise et soutenance (Stage III)"
}

CODE_UE_inverse = {v: k for k, v in CODE_UE.items()}



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

def trim_str(string):
    result = ""
    string = str(string)
    string = string.lower()
    for i in range(len(string)):
        if string[i] != " " and string[i] != "=":
            result += string[i]
    return result

def convertir_format_date(date):
    try:
        # Convertir la chaîne de date en objet datetime
        date_obj = datetime.strptime(date, '%m/%d/%Y')
        
        # Formater la date dans le nouveau format AAAA-MM-JJ
        date = date_obj.strftime('%Y-%m-%d')
        
        return date
    
    except ValueError:
        # Gérer les erreurs si la conversion échoue
        raise ValueError("Format de date invalide")


