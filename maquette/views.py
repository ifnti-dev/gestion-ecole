import zipfile
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from main.helpers import range_folder_file
from main.pdfMaker import generate_pdf
from main.models import AnneeUniversitaire, Programme, Semestre, Ue, Domaine, Parcours
from scripts.utils import backup_models_to_excel, load_data_from_excel, load_maquette, load_matieres, load_notes_from_matiere
from .forms import DataForm, GenerateMaquetteForm, ProgrammeForm
import os
from django.conf import settings
from django.utils.encoding import smart_str

def programmes(request, id_annee_selectionnee):
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    print(annee_universitaire)
    list_parcours = Parcours.objects.all()
    parcours_selected = ""
    if 'parcours' in request.GET:
        parcours_id = request.GET.get('parcours')
        parcours_selected = Parcours.filter(pk=parcours_id)
    else:
        parcours_selected = list_parcours
    programmes = Programme.objects.filter(semestre__annee_universitaire=annee_universitaire, parcours__in=parcours_selected)
    
    try:
        parcours_selected = parcours_selected.get().id
    except:
        parcours_selected = ""
    
    data = {
        'programmes' : programmes,
        'list_parcours' : list_parcours,
        'parcours_selected' : parcours_selected,
    }
    return render(request, 'maquette/programmes.html', context=data)

def add_programme(request, id_annee_selectionnee):
    data = {}
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    if request.POST:
        form = ProgrammeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('maquette:programmes', id_annee_selectionnee=id_annee_selectionnee)
        print(form.errors)
        data['form'] = form
    else:
        data['form'] = ProgrammeForm()
    
    return render(request, 'maquette/create_or_edit.html', context=data)

def edit_programme(request, id, id_annee_selectionnee):
    data = {}
    programme = get_object_or_404(Programme, pk=id)
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    if request.POST:
        form = ProgrammeForm(request.POST, instance=programme)
        if form.is_valid():
            form.save()
            return redirect('maquette:programmes', id_annee_selectionnee=id_annee_selectionnee)
        print(form.errors)
        data['form'] = form
    else:
        data['form'] = ProgrammeForm(instance=programme)
    
    return render(request, 'maquette/create_or_edit.html', context=data)

def delete_programme(request, id, id_annee_selectionnee):
    programme = get_object_or_404(Programme, pk=id)
    programme.delete()
    return redirect('maquette:programmes', id_annee_selectionnee=id_annee_selectionnee)


def data(request):
    id_annee_selectionnee = request.session.get('id_annee_selectionnee')
    if request.method == "POST":
        form = DataForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned_data = form.clean()
            #print(cleaned_data)
            enseignants_excel_file = cleaned_data.get('enseignants_excel_file')
            maquette_excel_file = cleaned_data.get('maquette_excel_file')
            matieres_excel_file = cleaned_data.get('matieres_excel_file')
            notes_excel_file = cleaned_data.get('notes_excel_file')
            database_excel_file = cleaned_data.get('database_excel_file')
            
            
            if maquette_excel_file:
                load_maquette(maquette_excel_file)
            if matieres_excel_file:
                load_matieres(matieres_excel_file)
            if notes_excel_file:
                load_notes_from_matiere(notes_excel_file)
            if database_excel_file:
                extract_path = 'media/tmp/'
                os.makedirs(extract_path, exist_ok=True)
                upload_zip_path = os.path.join(extract_path, database_excel_file.name)
                with open(upload_zip_path, 'wb') as zip_file:
                    for chunk in database_excel_file.chunks():
                        zip_file.write(chunk)
                
                with zipfile.ZipFile(upload_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                    
                os.remove(upload_zip_path)
                 
                files_path = os.listdir(extract_path)
                for path in files_path:
                    path = extract_path+path
                    load_data_from_excel(path)
                    os.remove(path)
                
                os.removedirs(extract_path)
        return redirect('maquette:data')
    data = {
        'form' : DataForm()
    }
    
    return render(request, 'data/index.html', context=data)

def global_backup(request):
    backup_models_to_excel()
    backup_directory = os.path.join(settings.MEDIA_ROOT, 'backup')
    zip_filename = 'backup_database_excel_files.zip'
    zip_path = os.path.join(settings.MEDIA_ROOT, zip_filename)
    zipf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
    for foldername, subfolders, filenames in os.walk(backup_directory):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            arcname = os.path.relpath(file_path, backup_directory)
            zipf.write(file_path, arcname)
    zipf.close()

    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename={smart_str(zip_filename)}'

    with open(zip_path, 'rb') as zip_file:
        response.write(zip_file.read())
        
    os.remove(zip_path)
        
    return response

def generate_maquette(request, id_annee_selectionnee):
    data = {}
    annee_accademique = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    parcours = Parcours.objects.all().first()

    if request.method == "POST":
        form = GenerateMaquetteForm(request.POST)
        if form.is_valid():
            cleaned_data = form.clean()
            semestre = cleaned_data.get('semestre')
            data['form'] = form
            data['maquette_semestres'] = generateDictFromProgrammeData(semestre, parcours, annee_accademique)
            generate_maquette_pdf(data['maquette_semestres'])
            data['pdf_file'] = "/media/pdf/maquette/maquette.pdf"
        else:
            data['form'] = form
    else:
        data['maquette_semestres'] = generateDictFromProgrammeData(None, parcours, annee_accademique)
        generate_maquette_pdf(data['maquette_semestres'])
        data['pdf_file'] = "/media/pdf/maquette.pdf"
        data['form'] = GenerateMaquetteForm(initial={'semestre': Semestre.objects.all()})
        
    return render(request, "maquette/generate_maquette.html", data)

def generateDictFromProgrammeData(semestre, parcours, annee_accademique):
    if semestre:
        semestres = [semestre]
        titre = f' semestre {semestre.libelle} {semestre.annee_universitaire}'
    else:
        semestres = annee_accademique.semestre_set.all()
        titre = ""
    programmes = Programme.objects.filter(parcours=parcours, semestre__in=semestres, semestre__annee_universitaire=annee_accademique)
    ues_list = []
    for programme in programmes:
        for ue in programme.ues.all():
            matires = [matiere.libelle for matiere in ue.matiere_set.all()]
            horaires = [matiere.heures if matiere.heures else 0  for matiere in ue.matiere_set.all()]
            enseignants = []
            for matiere in ue.matiere_set.all():
                if matiere.enseignant:
                    enseignants.append(matiere.enseignant)
                else:
                    enseignants.append("pas de prof")
            #print(enseignants)
            enseignant_principale = ue.enseignant
            ue_dict = {
                    "semestre" : programme.semestre.libelle,
                    "intitule" : ue.libelle,
                    "type_ue" : ue.type,
                    "matieres" : matires,
                    "credit" : ue.nbreCredits,
                    "volumes_horaires" : horaires,
                    "enseignants" : enseignants,
                    "enseignants_principaux" : enseignant_principale,
                }
            
            ues_list.append(ue_dict)
    data={
        "titre" : titre,
        "tatale_credit" : sum([ue["credit"] for ue in ues_list]),
        "totale_volume_horaire" : [sum(sum(ue["volumes_horaires"]) for ue in ues_list)],
        "ues" : ues_list
    }
    return data

def generate_maquette_pdf(context):
    latex_input = 'maquette_generique_template'
    latex_ouput = 'maquette_generique'
    pdf_file = 'maquette'

    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        return response
    
