from main.pdfMaker import generate_pdf

def genarate_diplome():
    etudiants = [
        # {
        #     "matricule": "3",
        #     "full_name": "SOWOU Mohammed Ognaré",
        #     "date_naiss": "20 Mars 1995",
        #     "lieu_naiss": "Sokodé",
        #     "annee_diplome": "2021-2022",
        #     "date_soutenance": "21-05-2022",
        # },
        # {
        #     "matricule": "Monsieur",
        #     "full_name": "KONDI Abdoul Malik",
        #     "date_naiss": "06 Mai 2002",
        #     "lieu_naiss": "Sotouboua",
        #     "annee_diplome": "2023-2024",
        #     "date_soutenance": "17-02-2024",
        # },
        #  {
        #     "matricule": "Monsieur",
        #     "full_name": "TEOURI Toure-Ydaou Amadou",
        #     "date_naiss": "26 mars 2002",
        #     "lieu_naiss": "Paris",
        #     "annee_diplome": "2023-2024",
        #     "date_soutenance": "17-02-2024",
        # },
        #   {
        #     "matricule": "Monsieur",
        #     "full_name": "TCHASSONA TRAORE Walid",
        #     "date_naiss": "20 Octobre 1997",
        #     "lieu_naiss": "Lomé",
        #     "annee_diplome": "2023-2024",
        #     "date_soutenance": "17-02-2024",
        # },
        # {
        #     "matricule": "Madame",
        #     "full_name": "TCHABANA Malia",
        #     "date_naiss": "29 Avril 2002",
        #     "lieu_naiss": "Tchamba",
        #     "annee_diplome": "2023-2024",
        #     "date_soutenance": "17-02-2024",
        # },
        #{
        #     "matricule": "Monsieur",
        #     "full_name": "ISSA-TOURE Mohamed Abdel-Aziz",
        #     "date_naiss": "09 Novembre 2001",
        #     "lieu_naiss": "Sokodé",
        #     "annee_diplome": "2023-2024",
        #     "date_soutenance": "20-04-2024",
        # },
        # {
        #     "matricule": "Madame",
        #     "full_name": "ADJANAYO Eritayo Simone",
        #     "date_naiss": "28 Octobre 2002",
        #     "lieu_naiss": "Sokodé",
        #     "annee_diplome": "2023-2024",
        #     "date_soutenance": "20-04-2024",
        # },
        # {
        #     "matricule": "Monsieur",
        #     "full_name": "TEOURI Samrou Ablaye",
        #     "date_naiss": "07 Juin 2003",
        #     "lieu_naiss": "Paris",
        #     "annee_diplome": "2023-2024",
        #     "date_soutenance": "20-04-2024",
        # },
        {
            "matricule": "Monsieur",
            "full_name": "TOYI Fabrice Anénafoua",
            "date_naiss": "13 Mai 2003",
            "lieu_naiss": "Sokodé",
            "annee_diplome": "2023-2024",
            "date_soutenance": "20-04-2024",
        },
        # {
        #     "matricule": "Monsieur",
        #     "full_name": "KPABOU Koussoune Isidore",
        #     "date_naiss": "04 Avril 2000",
        #     "lieu_naiss": "Sokodé",
        #     "annee_diplome": "2023-2024",
        #     "date_soutenance": "20-04-2024",
        # },
        # {
        #     "matricule": "Monsieur",
        #     "full_name": "OUPERE N'SEWA Ahlimou",
        #     "date_naiss": "13 Décembre 1995",
        #     "lieu_naiss": "Tchèkèlè",
        #     "annee_diplome": "2023-2024",
        #     "date_soutenance": "20-04-2024",
        # },
        # {
        #     "matricule": "Monsieur",
        #     "full_name": "NGANDEU NDJEUKAM Alhasan",
        #     "date_naiss": "11 Novembre 2002",
        #     "lieu_naiss": "Sokodé",
        #     "annee_diplome": "2023-2024",
        #     "date_soutenance": "20-04-2024",
        # },
    ]
    i = 0
    for etudiant in etudiants:
        i += 1
        context = {
            "etudiant" : etudiant
        }

        latex_input = 'diplome_end'
        latex_ouput = 'generated_diplome'
        pdf_file = f'pdf_diplome_{i}'

        # génération du pdf
        generate_pdf(context, latex_input, latex_ouput, pdf_file)


def run():
    genarate_diplome()