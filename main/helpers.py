import re
from django.shortcuts import get_object_or_404
from main.models import AnneeUniversitaire, Enseignant, Etudiant, Evaluation, Matiere, Note, Programme, Ue, Semestre
from openpyxl import load_workbook
import os
from datetime import datetime, timedelta
import shutil 



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

def get_authenticate_user_model(request):
    role = get_user_role(request)
    if role:
        role = role.name
        if role == "etudiant":
            return Etudiant.objects.get(user=request.user)
        if role == "enseignant":
            return Enseignant.objects.get(user=request.user)
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

def genarate_username(nom, prenom):
    return ""

def get_user_by_username(username):
    pass

def get_etudiant_by_user(user):
    pass



