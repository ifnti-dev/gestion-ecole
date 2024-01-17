import datetime
import os
from numpy import NaN
import openpyxl
from main.models import Charge, Competence, Comptable, CompteBancaire, CompteEtudiant, Conge, DirecteurDesEtudes, Domaine, Enseignant, Etudiant, FicheDePaie, Fournisseur, Frais, Information, Note, Paiement, Personnel, Salaire, Semestre, Tuteur, Ue, Evaluation, Parcours, AnneeUniversitaire, Programme, Matiere
from cahier_de_texte.models import Seance
from main.resources import get_model_by_name, get_resource_by_name
from scripts.factory import clean_data_base

import os
import shutil 
from django.db import transaction
import re
import zipfile
import zipfile
import openpyxl

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
def pre_load_ue_matiere_template_data_by_year(annee):
    result_path = 'media/excel_templates/ues_matieres.xlsx'
    file_path = "media/excel_templates/ues_matieres_tmp.xlsx"
    wb = openpyxl.load_workbook(filename=file_path)
    template_sheet = wb.active
    ues = Ue.objects.filter(programme__semestre__annee_universitaire__annee=annee)
    new_sheets = []
    for ue in ues:
        new_sheet = wb.copy_worksheet(template_sheet)
        new_sheet.title = ue.codeUE
        new_sheet['A1'] = ue.libelle
        new_sheets.append(new_sheets)
    wb.save(result_path)   
    wb.close()

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
            print(ue)
        except StopIteration:
            continue

        matieres_to_create = []
        for row in ue_sheet.iter_rows(values_only=True, min_row=3, max_col=5):
            libelle = row[0].strip()
            matieres_to_create.append(Matiere(
                libelle=libelle,
                coefficient=int(trim_str(row[1])),
                minValue=int(trim_str(row[2])),
                heures=int(trim_str(row[3])),
                abbreviation=trim_str(row[4]),
                ue=ue,
            ))

            if len(matieres_to_create) == batch_size:      
                Matiere.objects.bulk_create(matieres_to_create)
                matieres_to_create = []

        if matieres_to_create:
            Matiere.objects.bulk_create(matieres_to_create)

@transaction.atomic
def pre_load_note_ues_template_data(semestre):
    semestre = Semestre.objects.all().last()
    ues = Programme.objects.filter(semestre=semestre).first().ues.all()
    base_path ='media/excel_templates/notes_templates'
    
    os.mkdir(base_path)
        
    for ue in ues:
        path = f'{base_path}/notes_{ue.codeUE}.xlsx'
        wb = openpyxl.load_workbook(filename=f"media/excel_templates/notes_ue_tmplt.xlsx")
        template_sheet = wb.active
        for matiere in ue.matiere_set.all():
            new_sheet = wb.copy_worksheet(template_sheet)
            new_sheet.title = matiere.codematiere+"22"
            new_sheet['B1'].value = ue.libelle
            new_sheet['B2'].value = semestre.annee_universitaire.annee
            new_sheet['B3'].value = semestre.libelle
            new_sheet['B4'].value = matiere.libelle
            etudiants = matiere.get_etudiant_semestre(semestre)
            min_row = 16
            max_row = min_row + len(etudiants)-1
            i = 0
            for row in new_sheet.iter_rows(min_row=min_row, max_row=max_row, max_col=3):
                row[0].value = etudiants[i].nom
                row[1].value = etudiants[i].prenom
                row[2].value = ""
                i += 1
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
                libelle = trim_str(row[0]) # Remplacer les espaces multiples par un seul espace

                # Utiliser get_or_create pour éviter les doublons
                ue, created = Ue.objects.get_or_create(
                    libelle=libelle,
                    type=trim_str(row[1]),
                    niveau=trim_str(row[2]),
                    nbreCredits=trim_str(row[3]),
                    heures=trim_str(row[4])
                )
                semestre_ue[semestre].append(ue)

    parcours = Parcours.objects.all().first()
    semestres = annee.semestre_set.all()

    for semestre in semestres:
        programme = Programme.objects.create(semestre=semestre, parcours=parcours)
        programme.ues.set(semestre_ue[semestre.libelle.lower()])


def run():
    print("::: Import begining :::::")
    pre_load_note_ues_template_data(0)


