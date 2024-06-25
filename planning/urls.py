from django.urls import path
from . import views

app_name = 'planning'

urlpatterns = [
    path('', views.index, name='planning'),
    path('new/', views.nouveau_planning, name='creer_planning'),
    path('check/', views.verifier, name='verification'),
    path('seance/<str:seanceId>', views.seance, name='details'),
    path('enregistreme_seance/', views.enregistrer_seance, name='enregistrer_seance'),
    path('seance/<int:seance_id>/retirer/', views.retirer_seance, name='retirer_seance'),
    path('seance/<int:seance_id>/valider/', views.valider_seance, name='valider_seance'),
    path('summary/<str:semestreId>',views.resume,name='resume'),
    path('seance/<int:seance_id>/invalider/', views.invalider_seance, name='invalider_seance'),
    path('save/', views.sauvegarder, name='sauvegarder'),

    path('modifier/', views.modifier, name='modifier'),

    path('details/<str:planningId>', views.details, name='afficher'),
    path('imprimer/<int:planningId>', views.imprimer, name='imprimer'),
    path('delete/<str:planningId>', views.effacer, name='supprimer'),
    path('edit/<str:planningId>',views.ajouter_cours,name='ajouter_cours')

]