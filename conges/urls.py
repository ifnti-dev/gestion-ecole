from django.urls import path
from . import views

app_name = 'conges'

urlpatterns = [

                             #### Frais ####
    path('liste_conges/<int:id_annee_selectionnee>/', views.liste_conges, name='liste_conges'),
    path('liste_mes_conges/<int:id_annee_selectionnee>/', views.liste_mes_conges, name='liste_mes_conges'),
    path('demander_conges/', views.demander_conges, name='demander_conges'),
    path('modifier_demande_conge/<int:id>/', views.demander_conges, name='modifier_demande_conge'),

    path('demandes_validees/<int:id_annee_selectionnee>', views.demandes_validees, name='demandes_validees'),
    path('demandes_en_attentes/<int:id_annee_selectionnee>', views.demandes_en_attentes, name='demandes_en_attentes'),
    path('demandes_rejettees/<int:id_annee_selectionnee>', views.demandes_rejettees, name='demandes_rejettees'),
    path('valider_conges/<int:id>/', views.valider_conges, name='valider_conges'),
    path('refuser_conge/<int:id>/', views.refuser_conge, name='refuser_conge'),

]
