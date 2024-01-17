import os
from numpy import NaN
import openpyxl
import pandas as pd
from main.helpers import trim_str
from main.models import Charge, Competence, Comptable, CompteBancaire, CompteEtudiant, Conge, DirecteurDesEtudes, Domaine, Enseignant, Etudiant, FicheDePaie, Fournisseur, Frais, Information, Note, Paiement, Personnel, Salaire, Semestre, Tuteur, Ue, Evaluation, Parcours, AnneeUniversitaire, Programme, Matiere
from cahier_de_texte.models import Seance
from main.resources import get_model_by_name, get_resource_by_name
from scripts.factory import clean_data_base
from tablib import Dataset
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from import_export.results import RowResult


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


def get_cell_int_value(value):
    return int(trim_str(value))


def load_maquette(path, annee_selectionnee):
    # Clean ue and programme data
    Ue.objects.filter(
        programme__semestre__annee_universitaire=annee_selectionnee).delete()
    # print(Ue.objects.filter(programme__semestre__annee_universitaire=annee_selectionnee))
    # return
    # Ue.objects.all().delete()
    # Programme.objects.all().delete()
    Programme.objects.filter(
        semestre__annee_universitaire=annee_selectionnee).delete()

    # Upload ues data
    workbook = openpyxl.load_workbook(filename=path)
    semestre = ""
    semestre_ue = {}
    code_ue = {}
    for sheet in workbook:
        semestre = sheet.title.lower()
        semestre_ue[semestre] = []
        for row in sheet.iter_rows(values_only=True):
            if row[0] and row[0] != "libelle":
                libelle = row[0].strip()
                libelle = libelle.replace("  ", " ")
                code = "_".join([mot[0].lower() for mot in libelle.split(' ')])
                code_ue[code] = libelle
                ue = Ue.objects.create(libelle=libelle, type=row[1], niveau=row[2].split(
                    '=')[1], nbreCredits=row[3].split('=')[1], heures=row[4].split('=')[1])
                semestre_ue[semestre].append(ue)

    parcours = Parcours.objects.all().first()
    semestres = annee_selectionnee.semestre_set.all()
    for semestre in semestres:
        programme = Programme.objects.create(
            semestre=semestre, parcours=parcours)
        programme.ues.set(semestre_ue[semestre.libelle.lower()])
    return code_ue


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
            'prenom_cell': 0,
            'nom_cell': 1,
            'evaluations': [],
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
                        semestre = annee.semestre_set.get(
                            libelle=semestre.upper())
                elif "matière:" in firts_row_elt_value:
                    matiere = second_row_elt_value.strip()
                    matiere = Matiere.objects.get(
                        libelle=matiere, ue__programme__semestre=semestre)
                elif 'évaluation' in firts_row_elt_value:
                    # Créer les evaluations
                    if annee and semestre and matiere:
                        print(row)
                        evaluation = Evaluation.objects.create(libelle=trim_str(
                            row[2]), matiere=matiere, semestre=semestre, ponderation=int(trim_str(row[3])), date="2023-11-12")
                        nb_evaluation += 1
                        columns['evaluations'].append({
                            'evaluation': evaluation,
                            'cell': nb_evaluation,
                        })
                    else:
                        raise Exception(
                            "Le format de votre fichier est ivalide !")
                elif firts_row_elt_value != "prénom":
                    nom = str(row[columns['nom_cell']])
                    prenom = str(row[columns['prenom_cell']])
                    try:
                        etudiant = Etudiant.objects.get(
                            nom__icontains=nom, prenom__icontains=prenom)
                        print(etudiant)
                        for evaluataion_data in columns['evaluations']:
                            Note.objects.create(valeurNote=int(trim_str(
                                row[evaluataion_data['cell']])), etudiant=etudiant, evaluation=evaluataion_data['evaluation'])
                    except Exception as e:
                        raise Etudiant.DoesNotExist(
                            f'username = {firts_row_elt_value}')


def run():
    # clean_data_base()
    print("::: Import begining :::::")
    pass
