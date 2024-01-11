from jinja2 import Environment
from latex import build_pdf

from pathlib import Path, os

from os.path import dirname, abspath

from projet_ifnti.settings import BASE_DIR

def generate_pdf(context, input_file, output_file, pdf_file) :
    '''INSTANCIATION D’UN NOUVEL ENVIRONNEMENT AVEC DES OPTIONS DE BALISES PERSONNALISÉES'''
    
    j2_env = Environment(variable_start_string="\VAR{",
    variable_end_string="}",block_start_string="\BLOCK{",
    block_end_string="}", comment_start_string="\COMMENT{",
    comment_end_string="}")

    '''DECLARATION DE FICHIER'''
    #fichier à lire contenant le template avec les balises
    
    fichier_in = open("media/latex/" + str(input_file) + ".tex", 'r')
    
    #fichier en sortie accueillant les donnéesfournies
    
    fichier_out = open("media/out/" + str(output_file) + ".tex", 'w')
    template = fichier_in.read() #lecture du template
    monContext = context
    monContext["image_path"] =  os.path.join(BASE_DIR, 'media') + '/images/templates_assets/' #dirname(abspath(__file__)) + "/out/images/"
    monContext["pdf_path"] =  os.path.join(BASE_DIR, 'media') + '/pdf/'
    '''APPLICATION DE L’ENVIRONNEMENT EDITE SUR LE TEMPLATE'''

    
    j2_template = j2_env.from_string(template)
    
    # écriture dans le fichier en sortie
    
    fichier_out.write(j2_template.render(monContext))
    fichier_out.close()
    mon_pdf = build_pdf(open("media/out/" + str(output_file) + ".tex", 'r'))
    mon_pdf.save_to("media/pdf/" + str(pdf_file) + '.pdf')
    
    '''FERMETURE DE CANAUX'''
    
    fichier_in.close()
