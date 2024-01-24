import os
import openpyxl
import shutil 
import re

from main.models import Charge, Competence, Comptable, CompteBancaire, CompteEtudiant, Conge, DirecteurDesEtudes, Domaine, Enseignant, Etudiant, FicheDePaie, Fournisseur, Frais, Information, Note, Paiement, Personnel, Salaire, Semestre, Tuteur, Ue, Evaluation, Parcours, AnneeUniversitaire, Programme, Matiere
from cahier_de_texte.models import Seance
from scripts.factory import clean_data_base
from django.db import DataError, transaction
from datetime import datetime, timedelta

BASE_PATH = "media/excel_templates"

def trim_str(string):
    string = str(string).lower()
    string = re.sub(r'\s+', '', string.strip())
    string = re.sub(r'=', '', string)
    return string

def convert_serial_temporel_number_to_date(numero_serie_temporelle):
    # Date de référence d'Excel
    date_reference = datetime(1899, 12, 30)  
    # Ajouter le nombre de jours au format de série temporelle à la date de référence
    date_resultat = date_reference + timedelta(days=numero_serie_temporelle)
    
    return date_resultat

@transaction.atomic
def pre_load_ue_matiere_template_data_by_year(annees):
    folder_path = f"{BASE_PATH}/matieres_templates"
    os.mkdir(folder_path)
    template_path = f"{BASE_PATH}/ues_matieres_tmp.xlsx"
    
    for annee in annees:
        result_name = f"{folder_path}/ues_matieres_{annee}.xlsx"
        wb = openpyxl.load_workbook(filename=template_path)
        template_sheet = wb.active
        ues = Ue.objects.filter(programme__semestre__annee_universitaire__annee=annee.annee)
        new_sheets = []
        for ue in ues:
            new_sheet = wb.copy_worksheet(template_sheet)
            new_sheet.title = ue.codeUE
            new_sheet['A1'] = ue.libelle
            new_sheets.append(new_sheets)
        wb.save(result_name)   
        wb.close()

    shutil.make_archive(folder_path, 'zip', folder_path)
    
    for file_path in os.listdir(folder_path):
        os.remove(folder_path+"/"+file_path)
    os.rmdir(folder_path)
    
    return folder_path+".zip"

@transaction.atomic
def load_matieres_by_year(path, annee, batch_size=100):
    # Utiliser transaction.atomic pour améliorer les performances en effectuant toutes les opérations dans une seule transaction
    Matiere.objects.filter(ue__programme__semestre__annee_universitaire=annee).delete()

    workbook = openpyxl.load_workbook(filename=path)

    # Utiliser prefetch_related pour minimiser les requêtes SQL lors de la récupération des objets Ue
    ues = Ue.objects.filter(codeUE__in=[sheet.title for sheet in workbook]).prefetch_related('matiere_set')
    for ue_sheet in workbook:
        try:
            ue = next(ue for ue in ues if ue.codeUE == ue_sheet.title)
        except StopIteration:
            continue
        matieres_to_create = []
        for i, row in enumerate(ue_sheet.iter_rows(values_only=True, min_row=3, max_col=5)):
            libelle = row[0].strip()
            matieres_to_create.append(Matiere(
                libelle=libelle,
                coefficient=int(trim_str(row[1])),
                minValue=int(trim_str(row[2])),
                heures=int(trim_str(row[3])),
                abbreviation=f"{i+1}{ue.codeUE}",
                ue=ue,
                codematiere=f"{i+1}{ue.codeUE}",
            ))
            
            if len(matieres_to_create) == batch_size:   
                try:
                    Matiere.objects.bulk_create(matieres_to_create)
                except DataError as de:
                    raise de
                matieres_to_create = []

        if matieres_to_create:
            try:
                Matiere.objects.bulk_create(matieres_to_create)
            except DataError as de:
                raise de

@transaction.atomic
def pre_load_note_ues_template_data(semestre):
    try:
        programme = semestre.programme_set.all().get()
    except Exception:
        raise Programme.DoesNotExist
    ues = programme.ues.all()  
    etudiants = semestre.etudiant_set.all()
    base_path ='media/excel_templates/notes_templates'
    
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    path_part = f'{semestre.libelle}_{semestre.annee_universitaire}'
    for ue in ues:
        path = f'{base_path}/notes_{ue.codeUE}_{path_part}.xlsx'
        wb = openpyxl.load_workbook(filename=f"media/excel_templates/notes_ue_tmplt.xlsx")
        template_sheet = wb.active
        print("::::::::::::::: ", ue.codeUE)
        for matiere in ue.matiere_set.all():
            print(matiere.codematiere)
            new_sheet = wb.copy_worksheet(template_sheet)
            new_sheet.title = matiere.codematiere
            new_sheet['B1'].value = ue.libelle
            new_sheet['B2'].value = semestre.annee_universitaire.annee
            new_sheet['B3'].value = semestre.libelle
            new_sheet['B4'].value = matiere.libelle
            min_row = 17
            max_row = min_row + len(etudiants)-1
            for i, row in enumerate(new_sheet.iter_rows(min_row=min_row, max_row=max_row, max_col=3)):
                row[0].value = f"{etudiants[i].id} | {etudiants[i].nom}"
                row[1].value = etudiants[i].prenom
                row[2].value = ""
        wb.save(path)
        wb.close()
        
    shutil.make_archive(base_path, 'zip', base_path)
    
    for file_path in os.listdir(base_path):
        os.remove(base_path+"/"+file_path)
    os.rmdir(base_path)
    
    return base_path+".zip"

@transaction.atomic
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
    
    workbook = openpyxl.load_workbook(path)
    
    for sheet in workbook:
        matiere = sheet.title
        try:
            matiere = ue.matiere_set.get(codematiere=matiere)
        except Matiere.DoesNotExist:
            continue
        
        min_row = 7
        max_row = 13
        
        for row in sheet.iter_rows(min_row=min_row, max_row=max_row, values_only=True):
            if row[3]:
                try:
                    evaluation_date = convert_serial_temporel_number_to_date(int(trim_str(row[1])))
                except ValueError as v:
                    raise v
                evaluation_name = str(row[2])
                evaluation_ponderation = int(trim_str(row[1]))
                cell_A_n = trim_str(row[0])
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

        min_row = 17
        max_row = sheet.max_row

        for row in sheet.iter_rows(min_row=min_row, max_row=max_row ,values_only=True):
            matricule, _ = str(row[0]).split('|')

            try:
                matricule = trim_str(matricule).upper()
                etudiant = semestre.etudiant_set.get(id=matricule)
            except Exception as e:
                raise Etudiant.DoesNotExist(f'ID = {matricule}')
            for key in evaluations:
                data = evaluations[key]
                index = data[0]
                evaluation = data[1]
                valeur = trim_str(row[index])
                if evaluation and len(valeur) > 0:
                    valeur = int(valeur)
                    Note.objects.create(valeurNote=valeur, etudiant=etudiant, evaluation=evaluation)

@transaction.atomic
def pre_load_evaluation_template_data(matiere, semestre):
    path = 'media/excel_templates/evaluation_tmp.xlsx'
    
    wb = openpyxl.load_workbook(filename="media/excel_templates/evaluations.xlsx")
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
    
    os.remove(path)

@transaction.atomic
def load_notes_from_evaluation(path, matiere=None, semestre=None):
    # Charger le fichier excel des différentes notes d'une matière
    wb = openpyxl.load_workbook(path)
    
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

@transaction.atomic         
def load_maquette(path, annee):
    Ue.objects.filter(programme__semestre__annee_universitaire=annee).delete()
    Programme.objects.filter(semestre__annee_universitaire=annee).delete()
    workbook = openpyxl.load_workbook(filename=path)

    semestre_ue = {}

    for sheet in workbook:
        semestre = sheet.title.lower()
        semestre_ue[semestre] = []

        for row in sheet.iter_rows(values_only=True):
            if row[0] and row[0] != "libelle":
                libelle = row[0].strip()
                libelle = libelle.replace("  ", " ")
                ue, _ = Ue.objects.get_or_create(libelle=libelle, type=row[1], niveau=row[2].split('=')[1], nbreCredits=row[3].split('=')[1], heures=row[4].split('=')[1])
                semestre_ue[semestre].append(ue)

    parcours = Parcours.objects.all().first()
    semestres = annee.semestre_set.all()

    for semestre in semestres:
        programme = Programme.objects.create(
            semestre=semestre, parcours=parcours)
        programme.ues.set(semestre_ue[semestre.libelle.lower()])

@transaction.atomic
def load_matieres(path):
    # Clean matières data
    Matiere.objects.all().delete()
    workbook = openpyxl.load_workbook(filename=path)
    for ue_sheet in workbook:
        ue = Ue.objects.filter(libelle=CODE_UE[ue_sheet.title]).get()
        for row in ue_sheet.iter_rows(values_only=True):
            if row[0] and row[0] != "libelle" and 'nom:' not in trim_str(row[0]).lower():
                libelle = row[0].strip()
                libelle = libelle.replace("  ", " ")
                
                Matiere.objects.create(
                            libelle=libelle,
                            coefficient=get_cell_int_value(row[1]),
                            minValue=get_cell_int_value(row[2]),
                            heures=get_cell_int_value(row[3]),
                            ue=ue
                            )

@transaction.atomic
def load_notes_from_matiere(path):
    Evaluation.objects.all().delete()
    # Charger le fichier excel des différentes notes d'une matière
    workbook = openpyxl.load_workbook(path)
    
    # Initialiser les variable de base
    annee = None
    semestre = None
    matiere = None
    
    for sheet in workbook:
        columns = {
            'prenom_cell' : 0,
            'nom_cell' : 1,
            'evaluations' : [],
        }
        nb_evaluation = columns['nom_cell']
        for row in sheet.iter_rows(values_only=True):
            if row[0]:
                firts_row_elt_value = trim_str(row[0])
                second_row_elt_value = row[1]
                if "annee:" in firts_row_elt_value:
                    annee = trim_str(second_row_elt_value)
                    annee = AnneeUniversitaire.objects.get(annee=annee)
                elif "semestre:" in firts_row_elt_value:
                    if annee:
                        semestre = trim_str(second_row_elt_value)
                        print(semestre)
                        semestre = annee.semestre_set.get(libelle=semestre.upper())
                elif "matière:" in firts_row_elt_value:
                    matiere = second_row_elt_value.strip()
                    matiere = Matiere.objects.get(libelle=matiere, ue__programme__semestre=semestre)
                elif 'évaluation' in firts_row_elt_value:
                    # Créer les evaluations 
                    if annee and semestre and matiere:
                        print(row)
                        evaluation = Evaluation.objects.create(libelle=trim_str(row[2]), matiere=matiere, semestre=semestre, ponderation=int(trim_str(row[3])), date="2023-11-12")
                        nb_evaluation += 1
                        columns['evaluations'].append({ 
                                                        'evaluation' : evaluation,
                                                        'cell' : nb_evaluation,
                                                        })
                    else:
                        raise Exception("Le format de votre fichier est ivalide !")
                elif firts_row_elt_value != "prénom":
                        nom = str(row[columns['nom_cell']])
                        prenom = str(row[columns['prenom_cell']])
                        try:
                            etudiant = Etudiant.objects.get(nom__icontains=nom, prenom__icontains=prenom)
                            print(etudiant)
                            for evaluataion_data in columns['evaluations']:
                                Note.objects.create(valeurNote=int(trim_str(row[evaluataion_data['cell']])), etudiant=etudiant, evaluation=evaluataion_data['evaluation'])
                        except Exception as e:
                            raise Etudiant.DoesNotExist(f'username = {firts_row_elt_value}')

def run():
    #clean_data_base()
    print("::::: Import begining :::::")
    pre_load_ue_matiere_template_data_by_year(AnneeUniversitaire.objects.all())
    