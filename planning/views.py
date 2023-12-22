import json
from django.core.serializers import serialize
import datetime 
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from main.models import Enseignant, Matiere, Etudiant ,AnneeUniversitaire , Semestre
from cahier_de_texte.models import Seance
from planning.models import Planning
from django.contrib.auth import authenticate, login , get_user_model

import datetime

from collections import defaultdict

def index(request):
    return render(request, 'planning.html')

def save_a_planning():
    
    return

def new_planning(request,semestreId):
    semestreId=semestreId
    annee = AnneeUniversitaire.static_get_current_annee_universitaire().annee
    semestre = Semestre.objects.filter(courant=True, pk__contains=annee,id=semestreId).first()
    print(semestre)
    planification = defaultdict(list)
    ues = semestre.get_all_ues()

    for ue in ues:
        print(ue)
        matieres_json = serialize('json', ue.matiere_set.all())
        matieres = json.loads(matieres_json)
        for matiere in matieres :
            seances=Seance.objects.filter(semestre=semestre,matiere=matiere['pk'])
            temps=0
            for seance in seances:
                temps+=(seance.date_et_heure_fin - seance.date_et_heure_debut).total_seconds()/3600
            matiere['temps_effectuer']=temps
            print(matiere)
            
            plannings=Planning.objects.filter(semestre=semestre,matiere=matiere['pk'])
            temps_x=0
            for planning in plannings:
                temps_x+=(planning.date_et_heure_fin - planning.date_et_heure_debut).total_seconds()/3600
            matiere['temps_plannifier']=temps_x
                 
            print(matiere)

        planification[str(ue)].append({'matieres': matieres})
        planification_json = json.dumps(planification)

    return render(request, 'generer_planning.html', {'planification_json': planification_json,'semestre':semestre,'ues':ues})


def getMatieresEtudiant(etudiant):
    annee=AnneeUniversitaire.static_get_current_annee_universitaire().annee
    semestre=etudiant.semestres.filter(courant=True,pk__contains=annee)
    ues=semestre[0].get_all_ues()
    matieres=set()
    for ue in ues :
        matieres.update(ue.matiere_set.all())         
    return matieres

def save(request):
    if request.method == 'POST':
        # Retrieve all the events from the calendar
        events = request.POST.getlist('events')

        # Process the events and save them to the database
        for event in events:
            # Extract the event data from the submitted form
            intitule = event['intitule']
            semaine = event['semaine']
            semestre = event['semestre']
            date_heure_debut = event['date_heure_debut']
            date_heure_fin = event['date_heure_fin']
            matiere = event['matiere']
            precision = event['precision']
            professeur = event['professeur']

            # Create a Planning object and save it to the database
            planning = Planning(
                intitule=intitule,
                semaine=semaine,
                semestre=semestre,
                date_heure_debut=date_heure_debut,
                date_heure_fin=date_heure_fin,
                matiere=matiere,
                precision=precision,
                professeur=professeur
            )
            planning.save()

        # Redirect to the planning list page
        return redirect('planning-list')

    else:
        return render(request, 'planning/save.html')
