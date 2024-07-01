from django.urls import path
from api.views.etudiant.etudiant_api_views import etudiant_list

urlpatterns = [
    path("etudiant/", etudiant_list)
]