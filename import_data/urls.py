
from django.urls import path
from import_data import views

name = "import_data"

urlpatterns = [
  path('notes/', views.load_excel_file, name="notes"),
    path('importer_les_donnees/', views.importer_data,
         name='importer_les_donnees'), 
]