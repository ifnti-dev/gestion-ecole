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
from datetime import timedelta

from collections import defaultdict





def index(request):
    all_plannings = Planning.objects.all()
    semestres=Semestre.objects.filter(courant=True)
    plannings_by_semester = {}
    for planning in all_plannings:
        semestre = planning.semestre
        if semestre in plannings_by_semester:
            plannings_by_semester[semestre].append(planning)
        else:
            plannings_by_semester[semestre] = [planning]


    return render(request, 'planning_list.html', {'plannings_by_semester': plannings_by_semester,'semestres':semestres,'plannings':all_plannings})



def verifier(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        semaine = data.get('semaine')
        semestreId = data.get('semestre')
        annee = AnneeUniversitaire.static_get_current_annee_universitaire().annee
        semestre = Semestre.objects.filter(courant=True, pk__contains=annee,id=semestreId).first()
        plan = Planning.objects.filter(semestre=semestre, semaine=semaine).first()
        if plan is None:
            return JsonResponse({"status": "reussite"})
        return JsonResponse({"plan": plan})
        

    

def nouveau_planning(request):
    if request.method == 'POST':
        semestreId=request.POST.get("semestre")
        semaine=request.POST.get("semaine")
        intervalle=request.POST.get("intervalle")
        intervalle = request.POST.get("intervalle")
        # Divise la chaîne en deux parties en utilisant 'to' comme délimiteur
        dates = intervalle.split('to')
        # Récupère la date avant 'to' et la formate
        datedebut = dates[0].strip()  # Supprime les espaces inutiles autour de la date
        datedebut = datedebut[-2:] + '-' + datedebut[5:7] + '-' + datedebut[:4]  # Change le format de aaaa-mm-jj à jj-mm-aaaa
        # Récupère la date après 'to' et la formate
        datefin = dates[1].strip()  # Supprime les espaces inutiles autour de la date
        datefin = datefin[-2:] + '-' + datefin[5:7] + '-' + datefin[:4]  # Change le format de aaaa-mm-jj à jj-mm-aaaa
        annee = AnneeUniversitaire.static_get_current_annee_universitaire().annee
        semestre = Semestre.objects.filter(courant=True, pk__contains=annee,id=semestreId).first()
        planification = defaultdict(list)
        ues = semestre.get_all_ues()

        for ue in ues:
            matieres_json = serialize('json', ue.matiere_set.all())
            matieres = json.loads(matieres_json)
            for matiere in matieres :
                seances=Seance.objects.filter(semestre=semestre,matiere=matiere['pk'])
                temps=0
                for seance in seances:
                    temps+=(seance.date_et_heure_fin - seance.date_et_heure_debut).total_seconds()/3600
                matiere['temps_effectuer']=temps
                
                planning=Planning.objects.filter(semestre=semestre)
                for plan in planning :
                    plannings=SeancePlannifier.objects.filter(planning=plan ,matiere=matiere)
                    temps_x=0
                    for planning in plannings:
                        temps_x+=(planning.date_et_heure_fin - planning.date_et_heure_debut).total_seconds()/3600
                    matiere['temps_plannifier']=temps_x                         

            planification[str(ue)].append({'matieres': matieres})
            planification_json = json.dumps(planification)
        
        return render(request, 'generer_planning.html', {'planification_json': planification_json,'semestre':semestre,'semaine':semaine,'datedebut':datedebut,'datefin':datefin,'ues':ues})


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


def sauvegarder(request):
    if request.method == 'POST':
        # Retrieve all the events from the calendar
        data = json.loads(request.body.decode('utf-8'))
        semaine = data.get('semaine')
        semestre = data.get('semestre')
        datedebut = data.get('datedebut')
        datefin = data.get('datefin')
        events = data.get('events')
        semestre=Semestre.objects.filter(id=semestre).first()

        print( semaine)
        print(events)
        planning = Planning(
                semaine=semaine,
                semestre=semestre,
                datedebut=datedebut,
                datefin=datefin
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
        
        return JsonResponse({'status':"reussite"})
        
    



def update(request,planningId):
    return HttpResponse("En devellopement")

def seance(request,seanceId):
    seance=SeancePlannifier.objects.filter(id=seanceId).first()
    return render(request,'details_planning.html',{'seance':seance})

def imprimer(request,planningId):
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
