from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from main.pdfMaker import generate_pdf
from main.models import AnneeUniversitaire, Programme, Semestre, Ue, Domaine, Parcours
from .forms import GenerateMaquetteForm, ProgrammeFormSet, DomaineForm, ParcoursForm, ProgrammeForm


def programmes(request, id_annee_selectionnee):
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
    
