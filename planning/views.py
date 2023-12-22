import json
from django.core.serializers import serialize
import datetime 
from django.http import JsonResponse
from django.http import HttpResponse
import re
from django.core.serializers import serialize
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
            
            plannings=Planning.objects.filter(semestre=semestre,matiere=matiere['pk'])
            temps_x=0
            for planning in plannings:
                temps_x+=(planning.date_et_heure_fin - planning.date_et_heure_debut).total_seconds()/3600
            matiere['temps_plannifier']=temps_x                         

        planification[str(ue)].append({'matieres': matieres})
        planification_json = json.dumps(planification)

    return render(request, 'generer_planning.html', {'planification_json': planification_json,'semestre':semestre,'ues':ues})

def details(request,planningId):
    planning = Planning.objects.filter(id=planningId).first()
    return render(request, 'details_planning.html', {'planning': planning})


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
        data = json.loads(request.body.decode('utf-8'))
        semaine = data.get('semaine')
        semestre = data.get('semestre')
        events = data.get('events')
        semestre=Semestre.objects.filter(id=semestre).first()

        print('Semaine:', semaine)
        print('Événements:', events)
        for event in events:
            title = event.get('title')
            cleaned_title = re.sub(r'\s*\([^)]*\)$', '', title)
            print(cleaned_title)
            print(title)
            matiere = Matiere.objects.filter(libelle=cleaned_title).first()
            professeur = matiere.enseignant  # Remplacez cela par le champ approprié
            
            planning = Planning(
                intitule=title,
                semaine=semaine,
                semestre=semestre,
                matiere=matiere,
                date_heure_debut=event.get('start'),
                date_heure_fin=event.get('end'),
                professeur=professeur,
                precision='aucune'
            )

            # Sauvegardez l'objet Planning en base de données
            planning.save()
            serialized_planning = serialize('json', [planning])

        return JsonResponse({'status': 'OK','data':serialized_planning})

        # Vous pouvez renvoyer une réponse JSON si nécessaire
        return JsonResponse({'status': 'OK'})