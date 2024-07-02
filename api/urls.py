from django.urls import path
from api.views.etudiant_api_views import create_etudiant, delete_etudiant, detail_etudiant,list_etudiant, update_etudiant

urlpatterns = [
    path("etudiants/", list_etudiant),
    path("etudiant/create/<int:pk>/", create_etudiant),
    path("etudiant/update/<int:pk>/", update_etudiant),
    path("etudiant/delete/<int:pk>/", delete_etudiant),
    path("etudiant/detail/<int:pk>/", detail_etudiant),
]