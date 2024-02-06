from main.models import *
import os
from django import forms
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from main.resources import EtudiantResource
from tablib import Dataset
from django.shortcuts import render, HttpResponse
from tablib import Dataset
from django.contrib import messages

# Cette vue permet d'importer les données etudiants via un fichier xlsx
def importer_data(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            messages.error(request, "Vous devez selectionner un fichier")
            return redirect('import_data:importer_les_donnees')
        # Assurez-vous d'importer votre ressource EtudiantResource
        etudiants_resource = EtudiantResource()
        dataset = Dataset()
        etudiant = request.FILES['file']

        # try:
        imported_data = dataset.load(etudiant.read(), format='xlsx')
        for data in imported_data:
            etudiant = Etudiant(
                anneeentree=data[0],
               # id=data[1],
                nom=data[2],
                prenom=data[3],
                datenaissance=data[4],
                lieunaissance=data[5],
                sexe=data[6],
                anneebac2=data[7],
                contact=data[28],
                email=data[29],
                adresse=data[30],
                is_active=data[31],
                user=data[32],
                photo_passport=data[33],
                id=data[34],              
                profil=data[35],

            )
            etudiant.save()

            # Trouvez l'année universitaire en cours
            annee_universitaire_courante = AnneeUniversitaire.objects.get(
                annee_courante=True)

            # Attachez l'étudiant au Semestre 1 (S1) de l'année universitaire en cours
            semestre_s1 = annee_universitaire_courante.semestre_set.get(
                libelle='S1')
            etudiant.semestres.add(semestre_s1)

            semestres_data = data[36:]
            for semestre_data in semestres_data:
                try:
                    semestre = Semestre.objects.get(libelle=semestre_data)
                    etudiant.semestres.add(semestre)
                except Semestre.DoesNotExist:
                    # Gérer cette situation si le semestre n'existe pas
                    print(f"Le semestre '{semestre_data}' n'existe pas.")
            return render(request, 'etudiants/message_erreur.html', {'message': "Données importées avec succès."})

        # except Exception as e:
         #   return render(request, 'etudiants/message_erreur.html', {'message': "Erreur lors de l'importation du fichier Excel."})

    return render(request, 'etudiants/importer.html')
