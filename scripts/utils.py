import openpyxl

from main.models import Semestre, Ue, Evaluation, Parcours, AnneeUniversitaire, Programme, Matiere

CODE_UE = {'p_u_e_i_a': 'Politiques universitaires et intégrité académique', 'e': 'English', 'c_e_e_n': 'Communication et expression numérique', 'm_i': 'Mathématiques II', 'f_d_t_e_s_d_i': "Fondement des TI et systèmes d'exploitation I", 'p_a_e_b_d_d': 'Programmation, algorithmes et bases de données', 'c_e_i_e_e': 'Communication et Insertion en entreprise', 'é': 'Électronique', 'c_o_o_e_b_d_d': 'Conception orientée objet et base de données', 'c_e_d_d_s_w': 'Conception et développement des sites web', 'i_a_d_d': "Introduction au développement d'applications", 's_e_e_i_o_p_s_i_(_i': 'Stage en entreprise II OU Projets spéciaux II (Stage II)', 'c_e_g_d_e': 'Communication et gestion des entreprises', 'i_a_r': 'Introduction aux réseaux', 'i_e_i': 'Informatique embarquée II', 'p_o_o_e_s_d_d': 'Programmation orienté objet et structuration des données', 'a_d_s_e_s_d_i': "Administration de serveur et systèmes d'exploitation II", 'r_e_i_à_l_s_i': 'Réseaux et Introduction à la sécurité informatique', 'c_e_d_d_a': 'Conception et développement des applications', 'i_g': 'Interfaces graphiques', 's_é_e_t': 'Sujets émergents en technologie', 'd_é_e_r_s_d_e': 'Droit, éthique et responsabilité sociale des entreprises', 'c_e_d_d_l': 'Conception et développement des logiciels', 'd_e_d_d_a_w': 'Développement et déploiement des applications web', 'd_e_d_d_a_m': 'Développement et déploiement des applications mobile', 'c_d_c_/_c_c': 'Cours de concentration / Cours complémentaire', 's_d_e_s_(_i': "Stage/Projets d'entreprise et soutenance (Stage III)"}

def clean_evaluation_data():
    Evaluation.objects.all().delete()
    print("Drop all evaluations data ")

#semestre=
#ue=
#programme=
#matiere=
#evaluation = Evaluation(libelle="", ponderation=100, date="", semestre="", matiere, rattrapage=False)

def load_maquette(path):
    # Clean ue and programme data
    Ue.objects.all().delete()
    Programme.objects.all().delete()
    
    # Upload ues data
    workbook = openpyxl.load_workbook(filename=path)
    maquette_sheet = workbook.active
    semestre = ""
    semestre_ue = {}
    code_ue={}
    for row in maquette_sheet.iter_rows(values_only=True):
        if row[0]:
            if "debut_s" in row[0].lower():
                semestre = row[0].lower().split('_')[1]
                semestre_ue[semestre] = []
            elif row[0] != "libelle" and "fin_s" not in row[0].lower():
                libelle = row[0].strip()
                libelle = libelle.replace("  ", " ")
                code  = "_".join([mot[0].lower() for mot in libelle.split(' ')])
                code_ue[code] = libelle
                ue = Ue.objects.create(libelle=libelle, type=row[1], niveau=row[2].split('=')[1], nbreCredits=row[3].split('=')[1], heures=row[4].split('=')[1])
                semestre_ue[semestre].append(ue)
    # Create programme
    annee_universitaires = AnneeUniversitaire.objects.all()
    parcours = Parcours.objects.all().first()
    for anne_universitaire in annee_universitaires:
        semestres = anne_universitaire.semestre_set.all()
        for semestre in semestres:
            programme = Programme.objects.create(semestre=semestre, parcours=parcours)
            programme.ues.set(semestre_ue[semestre.libelle.lower()])
    return code_ue

def load_matieres(path):
    # Clean matières data
    Matiere.objects.all().delete()
    workbook = openpyxl.load_workbook(filename=path)
    for ue_sheet in workbook:
        ue = Ue.objects.filter(libelle=CODE_UE[ue_sheet.title]).get()
        for row in ue_sheet.iter_rows(values_only=True):
           if row[0] and row[0] != "libelle":
                libelle = row[0].strip()
                libelle = libelle.replace("  ", " ")
                matiere = Matiere.objects.create(
                            libelle=libelle,
                            coefficient=row[1].split('=')[1],
                            minValue=row[2].split('=')[1],
                            heures=row[3].split('=')[1],
                            ue=ue
                            )

def run():
    file_path = "/home/enseignant/malik/ifnti-gestion/media/excel/notesS4-2021-2022.xlsx"
    path = "/home/enseignant/malik/ifnti-gestion/web/media/excel/data/maquette_general_2022_2023.xlsx"
    # print(load_maquette(path))
    # return
    path = "/home/enseignant/malik/ifnti-gestion/web/media/excel/data/maquette_S1_2022_2023.xlsx"
    load_matieres(path)
    return
    # Créer ou récupérer le programme
    # Ouvrerture du classeur Excel
    workbook = openpyxl.load_workbook(file_path)
    semestre = Semestre.objects.all().first()
    for sheet in workbook:
        print(f':::::::::::::::::::::::::::::{sheet.title}:::::::::::::::::::::::::::::::')
        if sheet.title.lower() in ["entreprise"]:
            # Créer les Ues
            # Ajouter les ues au programme
            max_row = sheet.max_row
            columns = {
                'evaluations' : [],
                'nom' : -1,
                'prénom' : -1,
            }
            ###---  itérer sur le tableau des notes ----###
            for row in sheet.iter_rows(values_only=True, max_row=max_row//2):
                #print(row)
                if "UE" in row:
                    # Créer ou récupérer les matière
                    print(row)
                    matieres_names = get_row_value(row, ['ue'])
                    columns['evaluations'] = { matiere : [] for matiere in matieres_names }
                    
                elif "Nom" in row:
                    # Créer ou récupérer les evaluations
                    evaluations_names = get_row_key_value(row)
                    evaluations_names = [('prénom', 0), ('nom', 1), ('contrat_note_1', 2), ('contrat_note_2', 3), ('Partiel', 4), ('Moyenne', 5), ('salaire_note_1', 6), ('Moyenne', 7), ('Rattrapage', 8)]
                    for i in range(len(evaluations_names)):
                        if 'note' in evaluations_names[i][0]:
                            data = evaluations_names[i][0].split("_")
                            name = "_".join(data[1:3])
                            #evaluation = Evaluation.objects.get_or_create()
                            columns['evaluations'][data[0]].append((name, evaluations_names[i][1]))
                        elif 'nom' == evaluations_names[i][0]:
                            columns['nom'] = evaluations_names[i][1]
                        elif 'prénom' == evaluations_names[i][0]:
                            columns['prénom'] = evaluations_names[i][1]
                    # Créer les evaluations
                    print(columns)
                else:
                    pass
                    # index_nom = columns['nom']
                    # index_prenom = columns['prénom']
                    # print(row[index_nom], " ", row[index_prenom])
                    # for matiere_name in columns['evaluations']:
                    #     # Ajouter des notes aux évaluations
                    #     # Créer ou récupérer l' étudiants
                    #     for evaluation, index in columns['evaluations'][matiere_name]:
                    #         note = row[index]
                    #         print(evaluation, " ", note)
                
            print("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            ###---  itérer sur le tableau des rattrapages ----###

            for row in sheet.iter_rows(values_only=True, min_row=max_row//2, max_row=max_row):
                #print(row)
                if "UE" in row:
                    # Créer ou récupérer les matière
                    pass 
                elif "Nom" in row:
                    # Créer ou récupérer les evaluations
                    pass
                else:
                    # Créer les notes
                    pass


def get_row_value(row, exculd_list):
    return [ cell.lower() for cell in row if cell and cell.lower() not in exculd_list]

def get_row_key_value(row):
    return [ (row[i], i)  for i in range(len(get_row_value(row, []))) ]

