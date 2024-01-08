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


def convert_serial_temporel_number_to_date(numero_serie_temporelle):
    date_reference = datetime(1899, 12, 30)  # Date de référence d'Excel

    # Ajouter le nombre de jours au format de série temporelle à la date de référence
    date_resultat = date_reference + timedelta(days=numero_serie_temporelle)

    return date_resultat

def preLoadEvaluationTemplateData(matiere, semestre):
    path = 'media/excel_templates/evaluation_tmp.xlsx'
    
    try:
        os.remove(path)
    except:
        pass
    
    wb = load_workbook(filename="media/excel_templates/evaluations.xlsx")
    ws = wb.active
    ws['B1'].value = semestre.annee_universitaire.annee
    ws['B2'].value = semestre.libelle
    ws['B3'].value = matiere.libelle
    ws['B5'].value = ""
    ws['B6'].value = ""
    ws['B7'].value = ""
    
    etudiants = matiere.get_etudiant_semestre(semestre)
    
    min_row = 10
    max_row = min_row + len(etudiants)
    
    i = 0
    for row in ws.iter_rows(min_row=min_row, max_row=max_row-1, max_col=3):
        row[0].value = etudiants[i].nom
        row[1].value = etudiants[i].prenom
        row[2].value = ""
        i += 1
    wb.save(path)

def pre_load_note_ues_template_data(semestre):
    
    semestre = Semestre.objects.all().first()
    ues = Programme.objects.filter(semestre=semestre).first().ues.all()
    base_path ='media/excel_templates/notes_templates'
    for ue in ues:
        code_ue = CODE_UE_inverse[ue.libelle]
        path = f'{base_path}/notes_{code_ue}.xlsx'
        try:
            os.remove(path)
        except:
            pass
        wb = load_workbook(filename=f"media/excel_templates/notes_ue.xlsx")
        source = wb.active
        source['B1'] = code_ue
        for matiere in ue.matiere_set.all():
            new_sheet = wb.copy_worksheet(source)
            new_sheet.title = matiere.libelle.lower()
            new_sheet['B1'].value = semestre.annee_universitaire.annee
            new_sheet['B2'].value = semestre.libelle
            new_sheet['B3'].value = matiere.libelle
            # etudiants = matiere.get_etudiant_semestre(semestre)
            # min_row = 16
            # max_row = min_row + len(etudiants)-1
            # i = 0
            # for row in new_sheet.iter_rows(min_row=min_row, max_row=max_row, max_col=3):
            #     row[0].value = etudiants[i].nom
            #     row[1].value = etudiants[i].prenom
            #     row[2].value = ""
            #     i += 1
        
        wb.save(path)
    zip_path = base_path+".zip"
    try:
        os.remove(zip_path)
    except Exception as e:
        pass
    arrchived = shutil.make_archive(base_path, 'zip', base_path)
    return zip_path

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

def load_notes_from_evaluation(path, matiere=None, semestre=None):
    # Charger le fichier excel des différentes notes d'une matière
    wb = load_workbook(path)
    
    # Parcourir les evaluations
    for sheet in wb:
        columns = {
            'nom_cell' : 0,
            'prenom_cell' : 1,
            'evaluations' : [],
        }
        ws = sheet
        
        annee = str(ws['B1'].value)
        if not semestre:
            semestre = str(ws['B2'].value)
            matiere = Matiere.objects.get(libelle=matiere)
        if not matiere:
            annee = AnneeUniversitaire.objects.get(annee=annee)
            matiere = str(ws['B3'].value)
            semestre = Semestre.objects.get(libelle=semestre, annee_universitaire__id=annee.id)
        
        rattrapage = str(ws['B4'].value).lower() != "oui"
        evaluation_date = convert_serial_temporel_number_to_date(ws['B5'].value)
        evaluation_name = str(ws['B6'].value)
        evaluation_ponderation = int(str(ws['B7'].value))
        
        #evaluation_date = evaluation_date.date()
        print(evaluation_date, " ", "")
        
        if matiere.ponderation_restante() - evaluation_ponderation >= 0:
            evaluation, _ = Evaluation.objects.get_or_create(
                    libelle=evaluation_name, 
                    ponderation=evaluation_ponderation,
                    date=evaluation_date,
                    semestre=semestre,
                    matiere=matiere,
                    rattrapage=rattrapage,
                )
            
            etudiants = matiere.get_etudiant_semestre(semestre)
        
            min_row = 10
            max_row = min_row + len(etudiants)
            
            for row in sheet.iter_rows(min_row=min_row, max_row=max_row-1, max_col=3, values_only=True):
                etudiant = etudiants.get(nom__contains=row[0], prenom__contains=row[1])
                if Note.objects.filter(etudiant=etudiant, evaluation=evaluation):
                    continue
                
                Note.objects.create(valeurNote=int(row[2]), etudiant=etudiant, evaluation=evaluation)

        else:
            raise Exception(f"Erreur de pondération pour l'évaluation : {evaluation_name} ")


def load_notes_from_ue_file(path, ue, semestre):
    Evaluation.objects.filter(semestre=semestre).delete()
    
    evaluations = {
        "evaluation1" : [2, None],
        "evaluation2" : [3, None],
        "evaluation3" : [4, None],
        "evaluation4" : [5, None],
        "evaluation5" : [6, None],
        "evaluation6" : [7, None],
        "evaluation7" : [8, None],
        "rattrapage" : [9, None],
    }
    
    workbook = load_workbook(path)
    
    for sheet in workbook:
        matiere = sheet.title
        matiere = Matiere.objects.get(libelle=matiere)
        
        min_row = 6
        max_row = 13
        
        for row in sheet.iter_rows(min_row=min_row, max_row=max_row ,values_only=True):
            if row[3].value:
                evaluation_date = convert_serial_temporel_number_to_date(int(trim_str(row[1].value)))
                evaluation_name = str(row[2].value)
                evaluation_ponderation = int(trim_str(row[1].value))
                cell_A_n = trim_str(row[0].value)
                rattrapage = cell_A_n == "rattrapage"
                evaluation, _ = Evaluation.objects.get_or_create(
                    libelle=evaluation_name, 
                    ponderation=evaluation_ponderation,
                    date=evaluation_date,
                    semestre=semestre,
                    matiere=matiere,
                    rattrapage=rattrapage,
                )
                evaluations[cell_A_n][1] = evaluation

        min_row = 15
        max_row = 30
        
        for row in sheet.iter_rows(min_row=min_row, max_row=max_row ,values_only=True):
            nom = str(row[0])
            prenom = str(row[1])
            try:
                etudiant = Etudiant.objects.get(nom__icontains=nom, prenom__icontains=prenom)
                print(etudiant)
                for data_evaluation in evaluations:
                    index = data_evaluation[0]
                    evaluation = data_evaluation[1]
                    Note.objects.create(valeurNote=int(trim_str(row[index])), etudiant=etudiant, evaluation=evaluation)
            except Exception as e:
                raise Etudiant.DoesNotExist(f'Nom = {nom} | Prénom = {prenom}')

