from django.urls import path
from . import views

app_name = 'maquette'

urlpatterns = [
    path('<int:id_annee_selectionnee>/', views.generate_maquette, name=''),
    path('data/', views.data, name='data'),
    path('correspondances/', views.correspondances, name="correspondances"),
    path('correspondance/<int:id>/delete', views.delete_correspondance, name="correspondance_delete"),
    path('programmes/', views.programmes, name='programmes'),
    path('add_programme/', views.add_programme, name='add_programme'),
    path('edit_programme/<int:id>/', views.edit_programme, name='edit_programme'),
    path('delete_programme/<int:id>/', views.delete_programme, name='delete_programme'),
    path('domaines/', views.domaines, name='domaines'),
    path('add_domaine/', views.add_domaine, name='add_domaine'),
    path('edit_domaine/<int:id>/', views.edit_domaine, name='edit_domaine'),
    path('delete_domaine/<int:id>', views.delete_domaine, name='delete_domaine'),
    path('parcours/<int:id_domaine>/', views.parcours, name='parcours'),
    path('add_parcours/<int:id_domaine>/', views.add_parcours, name='add_parcours'),
    path('edit_parcours/<int:id>', views.edit_parcours, name='edit_parcours'),
    path('delete_parcours/<int:id>/', views.delete_parcours, name='delete_parcours'),
    path('notes/ues/template/', views.generate_note_template, name='note_template'),
    path('number/<int:number>/', views.number, name="number")
    # path('semestres_by_parcours/<int:id_parcours>', views.semestres_by_parcours, name='semestres_by_parcours'),
]
