from django.urls import path
from . import views

app_name = 'planning'

urlpatterns = [
    path('', views.index, name='planning'),
    path('new/<str:semestreId>', views.new_planning, name='creer_planning'),

]