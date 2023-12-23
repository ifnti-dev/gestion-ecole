from django.urls import path
from . import views

app_name = 'planning'

urlpatterns = [
    path('', views.index2, name='planning'),
    path('new/<str:semestreId>', views.new_planning, name='creer_planning'),
    path('save/', views.save, name='save'),
    path('details/<str:planningId>', views.details, name='afficher'),
    path('print/<str:planningId>', views.print, name='imprimer'),
    path('delete/<str:planningId>', views.delete, name='supprimer'),
    path('update/<str:planningId>',views.update,name='modifier')

]