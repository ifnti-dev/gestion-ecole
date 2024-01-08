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
from planning.models import Planning , SeancePlannifier
from django.contrib.auth import authenticate, login , get_user_model

import datetime

from collections import defaultdict


from operator import itemgetter
from itertools import groupby

def group_plannings_by_semester(plannings):
    # Grouper par semestre
    plannings_by_semester = {}
    for planning in plannings:
        semester_id = planning.semestre.id
        if semester_id not in plannings_by_semester:
            plannings_by_semester[semester_id] = []
        plannings_by_semester[semester_id].append(planning)
    return plannings_by_semester

def group_plannings_by_week(plannings):
    # Grouper par semaine
    plannings_by_week = {}
    for planning in plannings:
        week_number = planning.date_heure_debut.strftime("%U")
        if week_number not in plannings_by_week:
            plannings_by_week[week_number] = []
        plannings_by_week[week_number].append(planning)
    return plannings_by_week

def sort_plannings_by_date(plannings):
    
    return  sorted(plannings, key=lambda x: x.date_heure_debut)


def assign_week_number(plannings):
    # Ajouter l'attribut 'semaine'
    for i, planning in enumerate(plannings, start=1):
        planning.semaine = i
    return plannings


def index454(request):
    # Récupérer tous les plannings
    all_plannings = Planning.objects.all()


    # Étape 1 : Grouper par semestre
    plannings_by_semester = group_plannings_by_semester(all_plannings)


    for semester, plannings in plannings_by_semester.items():
        plannings_by_week = group_plannings_by_week(plannings)


        for week_number, week_plannings in plannings_by_week.items():
            sorted_week_plannings = sort_plannings_by_date(week_plannings)

            # Étape 4 : Ajouter un attribut 'semaine'
            plannings_by_week[week_number] = assign_week_number(sorted_week_plannings)

    # Maintenant, vous avez vos plannings organisés par semestre, semaine et triés par date
    print(plannings_by_semester)
    return render(request, 'planning_list.html', {'plannings_by_semester': plannings_by_semester})



def index2(request):
    all_plannings = Planning.objects.all()
    plannings_by_semester = {}
    for planning in all_plannings:
        semestre = planning.semestre
        if semestre in plannings_by_semester:
            plannings_by_semester[semestre].append(planning)
        else:
            plannings_by_semester[semestre] = [planning]


    return render(request, 'planning_list.html', {'plannings_by_semester': plannings_by_semester,'plannings':all_plannings})



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
            
            # plannings=Planning.objects.filter(semestre=semestre,matiere=matiere['pk'])
            temps_x=0
            # for planning in plannings:
            #     temps_x+=(planning.date_et_heure_fin - planning.date_et_heure_debut).total_seconds()/3600
            matiere['temps_plannifier']=temps_x                         

        planification[str(ue)].append({'matieres': matieres})
        planification_json = json.dumps(planification)

    return render(request, 'generer_planning.html', {'planification_json': planification_json,'semestre':semestre,'ues':ues})


def datetime_serializer(obj):
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')
    raise TypeError("Type not serializable")

import datetime
def details(request,planningId):
    planning = Planning.objects.filter(id=planningId).first()
    seances=SeancePlannifier.objects.filter(planning=planning)
    print(seances )
    event_data = [{'title': seance.intitule, 'start': seance.date_heure_debut , 'end':seance.date_heure_fin ,'url': '/planning/seance/' + str(seance.id) + ''} for seance in seances]
    event_data = json.dumps(event_data, default=datetime_serializer)
            
    return render(request, 'planning.html', {'event_data': event_data,'planning':planning})


def getMatieresEtudiant(etudiant):
    annee=AnneeUniversitaire.static_get_current_annee_universitaire().annee
    semestre=etudiant.semestres.filter(courant=True,pk__contains=annee)
    ues=semestre[0].get_all_ues()
    matieres=set()
    for ue in ues :
        matieres.update(ue.matiere_set.all())         
    return matieres


import datetime
import pytz
def save(request):
    if request.method == 'POST':
        # Retrieve all the events from the calendar
        data = json.loads(request.body.decode('utf-8'))
        semaine = data.get('semaine')
        semestre = data.get('semestre')
        events = data.get('events')
        semestre=Semestre.objects.filter(id=semestre).first()

        print( semaine)
        print(events)
        planning = Planning(
                semaine=semaine,
                semestre=semestre,
                # intervalle=(datetime.datetime.fromtimestamp(
                #     max(datetime.datetime.fromtimestamp(event.get('start'), tz=pytz.timezone('Europe/Paris')) for event in events) -
                #     datetime.datetime.fromtimestamp(min(datetime.datetime.fromtimestamp(event.get('start'), tz=pytz.timezone('Europe/Paris')) for event in events))
                # ),)
                intervalle="zap d'abord"
        )
        planning.save()
        for event in events:
            title = event.get('title')
            cleaned_title = re.sub(r'\s*\([^)]*\)$', '', title)
            print(cleaned_title)
            print(title)
            matiere = Matiere.objects.filter(libelle=cleaned_title).first()
            professeur = matiere.enseignant  # Remplacez cela par le champ approprié
            
            seance = SeancePlannifier(
                intitule=title,
                matiere=matiere,
                date_heure_debut=event.get('start'),
                date_heure_fin=event.get('end'),
                professeur=professeur,
                planning=planning,
                precision='aucune'
            )

            # Sauvegardez l'objet Planning en base de données
            seance.save()
        

        return render(request,'planning_list.html')
    



def update(request,planningId):
    return HttpResponse("En devellopement")

def seance(request,seanceId):
    seance=SeancePlannifier.objects.filter(id=seanceId).first()
    return render(request,'details_planning.html',{'seance':seance})

def print(request,planningId):
    return HttpResponse("En devellopement")

def delete(request,planningId):
    planning=Planning.objects.filter(id=planningId)
    planning.delete()
    return  render(request,'planning_list.html')

def enregistrer_seance(request, seance_id):
    # Logique pour enregistrer la séance
    return redirect('seance_detail', seance_id=seance_id)

def retirer_seance(request, seance_id):
    # Logique pour retirer la séance
    return redirect('seance_detail', seance_id=seance_id)
