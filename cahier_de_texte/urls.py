from django.urls import path
from . import views

app_name = 'cahier_de_texte'

urlpatterns = [
    path('', views.cahier_de_text, name='cahier_de_text'),
    path('enregistrer_seance/', views.enregistrer_seance, name='enregistrer_seance'),
    path('modifier_seance/<int:seance_id>/', views.modifier_seance, name='modifier_seance'),
    path('supprimer_seance/<int:seance_id>/', views.supprimer_seance, name='supprimer_seance'),
    path('liste_seance/', views.liste_seance, name='liste_seance'),
    path('liste_seance_etudiant/', views.liste_seance_etudiant, name='liste_seance_etudiant'),
    path('info_seance/<int:seance_id>/', views.info_seance, name='info_seance'),
    path('valider_seance/<int:seance_id>/', views.valider_seance, name='valider_seance'),
    path('changer_delegue/', views.changer_delegue, name='changer_delegue'),
    path('imprimer/', views.imprimer, name='imprimer'),
    path('commenter/', views.commenter, name='commenter'),
    path('changer_secretaire/',views.changer_secretaire,name='changer_secretaire'),
    path('gestion_classe',views.gestion_classe,name='gestion_classe'),
    path('signature',views.signature_prof,name='signature'),
]
