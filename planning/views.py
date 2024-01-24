import json
from django.core.serializers import serialize
import datetime 
from django.http import JsonResponse
from django.http import HttpResponse
from main.pdfMaker import generate_pdf
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
        return JsonResponse({"datedebut": str(plan.datedebut),"datefin": str(plan.datefin),"semaine": str(plan.semaine),"semestre": str(plan.semestre)})
        


def nouveau_planning(request):
    if request.method == 'POST':
        semestreId=request.POST.get("semestre")
        semaine=request.POST.get("semaine")

        intervalle = request.POST.get("intervalle")
        # Divise la chaîne en deux parties en utilisant 'to' comme délimiteur
        dates = intervalle.split('to')
        # Récupère la date avant 'to' et la formate
        datedebut = dates[0].strip()  # Supprime les espaces inutiles autour de la date

        #datedebut =  + datedebut[:4]  # Change le format de aaaa-mm-jj à jj-mm-aaaa
        # Récupère la date après 'to' et la formate
        datefin = dates[1].strip()  # Supprime les espaces inutiles autour de la date
        #datefin =   # Change le format de aaaa-mm-jj à jj-mm-aaaa
        intervalle=datedebut[-2:] + '/' + datedebut[5:7] + ' au ' + datefin[-2:] + '/' + datefin[5:7] + '/' + datefin[:4]

        annee = AnneeUniversitaire.static_get_current_annee_universitaire().annee
        semestre = Semestre.objects.filter(courant=True, pk__contains=annee,id=semestreId).first()
        planification = defaultdict(list)
        
        ues = semestre.get_all_ues()
        
        for ue in ues:
            print('plan1')
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

                    plannings=SeancePlannifier.objects.filter(planning=plan ,matiere=matiere['pk'])
                    temps_x=0
                    for planning in plannings:
                        temps_x+=(planning.date_heure_fin - planning.date_heure_debut).total_seconds()/3600

                    matiere['temps_plannifier']=temps_x                         

            planification[str(ue)].append({'matieres': matieres})
            print('plan : ',planification)
            planification_json = json.dumps(planification)
        

        return render(request, 'generer_planning.html', {'planification_json': planification_json,'semestre':semestre,'semaine':semaine,'datedebut':datedebut,'datefin':datefin,'intervalle':intervalle,'ues':ues})



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

        intervalle = data.get('intervalle')

        events = data.get('events')
        semestre=Semestre.objects.filter(id=semestre).first()

        print( semaine)
        print(events)
        planning = Planning(
                semaine=semaine,
                semestre=semestre,
                datedebut=datedebut,

                datefin=datefin,
                intervalle=intervalle

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
    
def resume(request,semestreId):
    semestre=Semestre.objects.filter(id=semestreId).first()
    liste_absence={}
    planning=Planning.objects.filter(semestre=semestre)
    plannings=set()
    for plan in planning:
        plannings.add(SeancePlannifier.objects.filter(planning=plan))

    seances= Seance.objects.filter(semestre=semestre)
    for seance in seances :
        if len(seance.eleves_presents) > 0 :
            for eleve in seance.eleves_presents :
                liste_absence[eleve.nom +' '+eleve.prenom] = 'Matiere : '+seance.matiere.libelle +' Date et Heure : '+seance.date_et_heure_debut +' à '+seance.date_et_heure_fin

    #faire une boucle sur la liste d'absence et recenser le nombre d'absence par eleves present dans la liste 
    #recuperer le nombre de fois qu'une matiere a ete plannifier et le nombre de fois qu'elle a été enregistrer comme realiser
    #recuperer les date et heure des seance plannifier mais non enregistrer (facultatif)
    #recuperer le nombre d'heure prevues et effectuer par matieres
    #recuperer le nombre d'heure effectuer par enseignant (suite logique de la partie plus haut)
     
    return HttpResponse('en devellopement')
        

def modifier(request):
    if request.method == 'POST':
        # Retrieve all the events from the calendar
        data = json.loads(request.body.decode('utf-8'))
        events = data.get('events')
        plan = data.get('planningId')
        planning=Planning.objects.filter(id=plan).first()
        
        for event in events:
            title = event.get('title')
            matiere = Matiere.objects.filter(libelle=title).first()
            professeur = matiere.enseignant  # Remplacez cela par le champ approprié
            old_seance=SeancePlannifier.objects.filter(
                intitule=title,
                matiere=matiere,
                date_heure_debut=event.get('start'),
                date_heure_fin=event.get('end'),
                professeur=professeur,
                planning=planning,
                precision='aucune').first()
            if old_seance :
                next
            else :
                seance = SeancePlannifier(
                    intitule=title,
                    matiere=matiere,
                    date_heure_debut=event.get('start'),
                    date_heure_fin=event.get('end'),
                    professeur=professeur,
                    planning=planning,
                    precision='aucune'
                )
                seance.save()
            # Sauvegardez l'objet Planning en base de données
            
        
        return JsonResponse({'status':"reussite"})

    



def ajouter_cours(request,planningId):
    planningg = Planning.objects.filter(id=planningId).first()
    seances=SeancePlannifier.objects.filter(planning=planningg)
    event_data = [{'title': seance.intitule, 'start': seance.date_heure_debut , 'end':seance.date_heure_fin ,'url': '/planning/seance/' + str(seance.id) + ''} for seance in seances]
    event_data = json.dumps(event_data, default=datetime_serializer)
    semestre = planningg.semestre
    print(semestre)
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
                plannings=SeancePlannifier.objects.filter(planning=plan ,matiere=matiere['pk'])
                temps_x=0
                for planning in plannings:
                    temps_x+=(planning.date_heure_fin - planning.date_heure_debut).total_seconds()/3600
                matiere['temps_plannifier']=temps_x                         

        planification[str(ue)].append({'matieres': matieres})
        planification_json = json.dumps(planification)
    
    return render(request, 'update_planning.html', {'planification_json': planification_json,'event_data': event_data,'planning':planningg,'ues':ues})



def seance(request,seanceId):
    seance=SeancePlannifier.objects.filter(id=seanceId).first()
    return render(request,'details_planning.html',{'seance':seance})


def french_day(day,):
    french_correspondance_days = {'Monday':'Lundi','Tuesday' :'Mardi','Wednesday' :'Mercredi','Thursday' :'Jeudi','Friday' :'Vendredi','Saturday' :'Samedi'}
    return french_correspondance_days[day]



def imprimer(request,planningId):
    # if request.user.groups.all().first().name not in ['directeur_des_etudes']:
    #     return render(request, 'errors_pages/403.html')
    
    planns = Planning.objects.filter(id=planningId).first()
    days =[]
    timeslots=['']
    tenues=[ 'Veste', 'Tricot' , 'Veste' , 'Tricot' ,'Bigarré' , 'Bigarré']
    if planns.semestre.libelle == 'S1' or 'S2' :
        niveau='L1 '+ planns.semestre.libelle + ' '+str(planns.semestre.annee_universitaire)
    elif  planns.semestre.libelle == 'S3' or 'S4' :
        niveau='L2 '+ planns.semestre.libelle + ' '+str(planns.semestre.annee_universitaire)
    elif  planns.semestre.libelle == 'S5' or 'S6' :
        niveau='L3 '+ planns.semestre.libelle + ' '+str(planns.semestre.annee_universitaire)
    
    print(niveau)

    plannings=SeancePlannifier.objects.filter(planning=planns)
    for planning in plannings :
        jour_n=(planns.semaine-1)*5 + planning.date_heure_debut.weekday() +1
        jour_n=str(jour_n)
        valeur_jour= str(planning.date_heure_debut.day)
        if len(valeur_jour) == 1 :
            valeur_jour='0'+valeur_jour
        valeur_mois=str(planning.date_heure_debut.month)
        if len(valeur_mois) == 1 :
            valeur_mois='0'+valeur_mois        
        jour = french_day(planning.date_heure_debut.strftime("%A"))

        day = jour +' '+valeur_jour+'/'+valeur_mois+' - J'+jour_n 
        
        timeshot= str(planning.date_heure_debut.hour)+'h'+str(planning.date_heure_debut.minute)

        planning.day = day
        planning.timeshot = timeshot
        planning.save()
        if day not in days:
            days.append(day)
        if timeshot not in timeslots:
            timeslots.append(timeshot)

#
    schedule = {}


    # Populate the schedule dictionary with empty sub-dictionaries for each time slot
    for time in timeslots:
        schedule[time] = {}

    # Populate the schedule with planning information
    for plan in plannings:
        time_slot = plan.timeshot  # Replace with your actual attribute for timeslot
        day = plan.day  # Replace with your actual attribute for day

        # Check if the time slot exists in the schedule dictionary
        if time_slot in schedule:
            # Check if the day exists in the sub-dictionary for the given time slot
            if day in schedule[time_slot]:
                # Append the planning information to the existing list for the day
                schedule[time_slot][day].append({
                    "intitule": plan.intitule,
                    "professeur": plan.professeur.nom if plan.professeur else "No Professor"
                })
            else:
                # Create a new list for the day and append the planning information
                schedule[time_slot][day] = [{
                    "intitule": plan.intitule,
                    "professeur": plan.professeur.nom if plan.professeur else "No Professor"
                }]
        else:
            # Handle the case where the time slot is not in the schedule (if needed)
            pass

    # Print the resulting schedule
    for time_slot, days_data in schedule.items():
        print(f"Time Slot: {time_slot}")
        
        for day, planning_info_list in days_data.items():
            print(f"  Day: {day}")
            
            for planning_info in planning_info_list:
                print(f"    Intitule: {planning_info['intitule']}, Professeur: {planning_info['professeur']}")



    context = {'planning': schedule,'niveau':niveau,'days':days,'taille':22.5/len(days),'tenues':tenues}          
                    
    latex_input = 'planning_week'
    latex_ouput = 'planning_week_'+str(planns.semaine)+'_'+str(planns.semestre.libelle)+'_'+str(planns.semestre.annee_universitaire)
    pdf_file = 'planning_week_'+str(planns.semaine)+'_'+str(planns.semestre.libelle)+'_'+str(planns.semestre.annee_universitaire)

    # génération du pdf
    generate_pdf(context, latex_input, latex_ouput, pdf_file)

    # visualisation du pdf dans le navigateur
    with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
        pdf_preview = f.read()
        response = HttpResponse(pdf_preview, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        return response









    # days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
    # schedule = [{} for _ in range(len(days))]
    # timeslots = ['7h', '8h30', '8h45', '10h15', '10h30', '12h']

    # for i, day in enumerate(days):
    #     for time in timeslots:
    #         schedule[i][time] = ' '  # or you can initialize with an empty string

    # schedule[0]['7h'] = 'Étude'
    # schedule[0]['8h30'] = 'Django'
    # # fill in the rest of the schedule with the remaining information

    # # print the schedule
    # for i, day in enumerate(days):
    #     print(day)
    #     for time in timeslots:
    #         print(time, schedule[i][time])
    #     print('')



    # context = {'planning': plannings}


    # latex_input = 'planning_week'
    # latex_ouput = 'planning_week_'+str(plan.semaine)+str(plan.semestre)
    # pdf_file ='planning_week_'+str(plan.semaine)+str(plan.semestre)

    # # génération du pdf
    # generate_pdf(context, latex_input, latex_ouput, pdf_file)

    # # visualisation du pdf dans le navigateur
    # with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
    #     pdf_preview = f.read()
    #     response = HttpResponse(pdf_preview, content_type='application/pdf')
    #     response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
        # return response
    return HttpResponse('check')
    


def delete(request,planningId):
    planning=Planning.objects.filter(id=planningId).first()
    seance = SeancePlannifier.objects.filter(planning=planning)
    for se in seance :
        se.delete()

    planning.delete()
    return  render(request,'planning_list.html')

def enregistrer_seance(request, seance_id):
    return redirect('seance_detail', seance_id=seance_id)

def retirer_seance(request, seance_id):
    return redirect('seance_detail', seance_id=seance_id)
