import zipfile
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from main.pdfMaker import generate_pdf
from main.models import AnneeUniversitaire, CorrespondanceMaquette, Matiere, Programme, Semestre, Ue, Domaine, Parcours
from maquette.custom_permission_required import data_permission
from scripts.utils import load_maquette, load_matieres_by_year, load_notes_from_ue_file, pre_load_note_ues_template_data, pre_load_ue_matiere_template_data_by_year
from .forms import CorrespondanceMaquetteForm, GenerateMaquetteForm, ProgrammeForm, DomaineForm, ParcoursForm
import os
from django.contrib import messages
from django.db import DataError, IntegrityError
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required


@login_required(login_url=settings.LOGIN_URL)
def programmes(request):
    id_annee_selectionnee = request.session.get('id_annee_selectionnee')
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
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

@login_required(login_url=settings.LOGIN_URL)
def add_programme(request):
    data = {}
    id_annee_selectionnee = request.session.get('id_annee_selectionnee')
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    if request.POST:
        form = ProgrammeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('maquette:programmes')
        data['form'] = form
    else:
        data['form'] = ProgrammeForm()
    
    return render(request, 'maquette/create_or_edit.html', context=data)

@login_required(login_url=settings.LOGIN_URL)
def edit_programme(request, id):
    data = {}
    id_annee_selectionnee = request.session.get('id_annee_selectionnee')
    programme = get_object_or_404(Programme, pk=id)
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=id_annee_selectionnee)
    if request.POST:
        form = ProgrammeForm(request.POST, instance=programme)
        if form.is_valid():
            form.save()
            return redirect('maquette:programmes')
        data['form'] = form
    else:
        data['form'] = ProgrammeForm(instance=programme)
    
    return render(request, 'maquette/create_or_edit.html', context=data)

@login_required(login_url=settings.LOGIN_URL)
def delete_programme(request, id):
    id_annee_selectionnee = request.session.get('id_annee_selectionnee')
    programme = get_object_or_404(Programme, pk=id)
    programme.delete()
    return redirect('maquette:programmes')

@login_required(login_url=settings.LOGIN_URL)
def correspondances(request):
    if request.method == "POST":
        if 'form_id' in request.POST and request.POST.get('form_id') != '-1':
            correspondance = get_object_or_404(CorrespondanceMaquette, pk=request.POST.get('form_id'))
            form = CorrespondanceMaquetteForm(request.POST, instance=correspondance)
        else:
            form = CorrespondanceMaquetteForm(request.POST)
            
        if form.is_valid():
            form.save()
            form = CorrespondanceMaquetteForm()
            request.POST = None
    else:
        form = CorrespondanceMaquetteForm()
        request.POST = None
            
    data = {
        'form': form,
        'correspondances' : CorrespondanceMaquette.objects.all(),
        'ues' : Ue.objects.all(),
        'matieres' : Matiere.objects.all(),
    }
    return render(request, 'maquette/correspondances.html', context=data)

@login_required(login_url=settings.LOGIN_URL)
def delete_correspondance(request, id):
    correspondance = get_object_or_404(CorrespondanceMaquette, pk=id)
    correspondance.delete()
    return redirect('maquette:correspondances')

@login_required(login_url=settings.LOGIN_URL)
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
    programmes = Programme.objects.filter(parcours=parcours, semestre__in=semestres, semestre__annee_universitaire=annee_accademique).prefetch_related('ues')
    semestres_data = []
    for programme in programmes:
        ues = programme.ues.all().prefetch_related('matiere_set')
        semestre_data = {
            "semsetre" : programme.semestre,
            "ues" : ues,
            "ues_length" : ues.count(),
        }
        
        semestres_data.append(semestre_data)
    
    data={
        "titre" : titre,
        "semestres_data" : semestres_data
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

@login_required(login_url=settings.LOGIN_URL)
def domaines(request):
    domaines =Domaine.objects.all()
    
    data = {
        'domaines' : domaines,
    }
    return render(request, 'domaines/list.html', context=data)

@login_required(login_url=settings.LOGIN_URL)
def add_domaine(request):
    data = {}
    if request.POST:
        form = DomaineForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('maquette:domaines')
        data['form'] = form
    else:
        data['form'] = DomaineForm()
    
    return render(request, 'domaines/create_or_edit.html', context=data)

@login_required(login_url=settings.LOGIN_URL)
def edit_domaine(request, id):
    data = {}
    domaine = get_object_or_404(Domaine, pk=id)
    if request.POST:
        form = DomaineForm(request.POST, instance=domaine)
        if form.is_valid():
            form.save()
            return redirect('maquette:domaines')
        data['form'] = form
    else:
        data['form'] = DomaineForm(instance=domaine)
    
    return render(request, 'domaines/create_or_edit.html', context=data)

@login_required(login_url=settings.LOGIN_URL)
def delete_domaine(request, id):
    domaine = get_object_or_404(Domaine, pk=id)
    domaine.delete()
    return redirect('maquette:domaines')

@login_required(login_url=settings.LOGIN_URL)
def parcours(request, id_domaine):
    domaine = get_object_or_404(Domaine, pk=id_domaine)
    parcours = domaine.parcours_set.all()
    data = {
        'parcours_list' : parcours,
        'domaine': domaine,
    }
    return render(request, 'parcours/list.html', context=data)

@login_required(login_url=settings.LOGIN_URL)
def add_parcours(request, id_domaine):
    domaine = get_object_or_404(Domaine, pk=id_domaine)
    data = {}
    if request.POST:
        form = ParcoursForm(request.POST)
        if form.is_valid():
            parcours = form.save(commit=False)
            parcours.domaine = domaine
            parcours.save()
            return redirect('maquette:parcours', id_domaine=domaine.id)
        data['form'] = form
    else:
        data['form'] = ParcoursForm()
    
    return render(request, 'parcours/create_or_edit.html', context=data)

@login_required(login_url=settings.LOGIN_URL)
def edit_parcours(request, id):
    data = {}
    parcours = get_object_or_404(Parcours, pk=id)
    if request.POST:
        form = ParcoursForm(request.POST, instance=parcours)
        if form.is_valid():
            form.save()
            return redirect('maquette:parcours', id_domaine=parcours.domaine.id)
        data['form'] = form
    else:
        data['form'] = ParcoursForm(instance=parcours)
    
    return render(request, 'domaines/create_or_edit.html', context=data)

@login_required(login_url=settings.LOGIN_URL)
def delete_parcours(request, id):
    parcours = get_object_or_404(Parcours, pk=id)
    parcours.delete()
    return redirect('maquette:domaines')

@login_required(login_url=settings.LOGIN_URL)
@data_permission('view_data')
def data(request):
    return render(request, 'data/index.html')

@login_required(login_url=settings.LOGIN_URL)
def upload_note(request):
    if request.POST:
        if 'file' in request.FILES :
            message = ""
            files = request.FILES.getlist('file')
            for file in files:
                full_data = str(file).split('_')
                try:
                    code_ue = full_data[1]
                    semestre = full_data[2]
                    annee_selectionnee = int(full_data[3].split('-')[0])
                except Exception as e:
                    messages.error(request, "Votre fichier n'est pas sous le format notes_code_Sn_20xx-20xy")
                    break
                annee_selectionnee = AnneeUniversitaire.objects.get(annee=annee_selectionnee)
                ue = Ue.objects.get(codeUE=code_ue)
                semestre = annee_selectionnee.semestre_set.get(libelle=semestre)
                load_notes_from_ue_file(file, ue, semestre)
        else:
            messages.info(request, "Vous devez séléctionner un fichier ! ")
        return redirect('maquette:data')
        
    annee = request.GET.get('annee_universitaire')
    annee = AnneeUniversitaire.objects.filter(pk=annee).first()
    semestres  = annee.semestre_set.all().prefetch_related('programme_set').prefetch_related('etudiant_set')
    zip_path = pre_load_note_ues_template_data(semestres)
    with open(zip_path, 'rb') as zip_file:
        response = HttpResponse(zip_file.read(), content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(zip_path))
        return response

@login_required(login_url=settings.LOGIN_URL)
def upload_maquette(request):
    if request.method == "POST":
        if 'file' in request.FILES :
            message = ""
            maquette_excel_file = request.FILES.getlist('file')
            for file_cache_tmp in maquette_excel_file:
                name = str(file_cache_tmp)
                name_part = name.split('_')
                if len(name_part) == 3:
                    year_part = name_part[2].split('-')
                    if len(year_part) == 2:
                        annee_selectionnee = int(year_part[0])
                        annee_selectionnee = AnneeUniversitaire.objects.get(annee=annee_selectionnee)
                        message += f"{annee_selectionnee}; " 
                        try:
                            load_maquette(file_cache_tmp, annee_selectionnee)
                        except ValueError as ve:
                            messages.error(request, str(ve))
            
            message_array = message.split(';')
            if len(message_array) == 2:
                message = f"La maquette de l'année {message_array[0]}  a été chargé !"
            else :
                message = f"La maquette des années {message}  à été chargé !"
                
            messages.success(request, message)
        else:
            messages.info(request, "Vous devez séléctionner un fichier ! ")
        return redirect('maquette:data')
    
    annee_universitaire = request.GET.get("annee_universitaire")
    annee_universitaire = get_object_or_404(AnneeUniversitaire, pk=annee_universitaire)
    file_name = 'maquette_general_[annee].xlsx'
    file_path = 'media/excel_templates/'+file_name
    file_name = f'maquette_general_{annee_universitaire}.xlsx'
    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type="application/force-download")
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(file_name))
        return response

@login_required(login_url=settings.LOGIN_URL)
def upload_matieres(request):
    if request.method == "POST":
        if 'file' in request.FILES :
            message = ""
            matieres_excel_file = request.FILES.getlist('file')
            for file_cache_tmp in matieres_excel_file:
                name = str(file_cache_tmp)
                annee_str = name.split('_')[-1]
                annee_str = annee_str.split('-')[0]
                annee = AnneeUniversitaire.objects.get(annee=annee_str)
                try:
                    load_matieres_by_year(file_cache_tmp, annee)
                except DataError as de:
                    messages.error(request, str(de))
                    return redirect('maquette:data')
                except IntegrityError as ie:
                    messages.error(request, str(ie))
                    return redirect('maquette:data')
                except Exception as e:
                    print(e)
                    return redirect('maquette:data')
                    
            message = f"{annee}; "
            message_array = message.split(';')
            if len(message_array) == 2:
                message = f"Les matières de l'annéé {message_array[0]} on été chargé !"
            else :
                message = f"La maquette des années {message} on été chargé !"
                
            messages.success(request, message)
        else:
            messages.info(request, "Vous devez séléctionner un fichier ! ")
        
        return redirect('maquette:data')
        
    annees = AnneeUniversitaire.objects.all()
    file_name = pre_load_ue_matiere_template_data_by_year(annees)
    file_path = 'media/excel_templates/'+file_name
    with open(file_name, 'rb') as file:
        response = HttpResponse(file.read(), content_type="application/force-download")
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(file_name))
        return response
