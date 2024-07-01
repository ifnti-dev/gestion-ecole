from django.urls import path
from api.views.etudiant_api_views import create_etudiant, delete_etudiant, detail_etudiant,etudiant_list, update_etudiant

urlpatterns = [
    path("etudiants/", etudiant_list),
    path("etudiant/create/<int:id>/", create_etudiant),
    path("etudiant/update/<int:id>/", update_etudiant),
    path("etudiant/delete/<int:id>/", delete_etudiant),
    path("etudiant/detail/<int:id>/", detail_etudiant),
]