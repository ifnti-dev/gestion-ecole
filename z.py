
@login_required(login_url=settings.LOGIN_URL)
def nouveau_planning(request):
    if request.user.groups.all().first().name not in ['directeur_des_etudes','secretaire']:
        return render(request, 'errors_pages/403.html')
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
                    temps+=(seance.date_et_heure_fin - seance.date_et_heure_debut).total_seconds()
                hours, remainder = divmod(temps, 3600)
                minutes, _ = divmod(remainder, 60)
                matiere['temps_effectuer']=str(int(hours))+'h '+str(int(minutes))+'min' 
                
                planning=Planning.objects.filter(semestre=semestre)
                for plan in planning :

                    plannings=SeancePlannifier.objects.filter(planning=plan ,matiere=matiere['pk'])
                    temps_x=0
                    for planning in plannings:
                        temps_x+=(planning.date_heure_fin - planning.date_heure_debut).total_seconds()
                    hours_x, remainder = divmod(temps_x, 3600)
                    minutes_x, _ = divmod(remainder, 60)
                    matiere['temps_plannifier']=str(int(hours_x))+'h '+str(int(minutes_x))+'min'                       

            planification[str(ue)].append({'matieres': matieres})
            print('plan : ',planification)
            planification_json = json.dumps(planification)
        

        return render(request, 'generer_planning.html', {'planification_json': planification_json,'semestre':semestre,'semaine':semaine,'datedebut':datedebut,'datefin':datefin,'intervalle':intervalle,'ues':ues})
    

