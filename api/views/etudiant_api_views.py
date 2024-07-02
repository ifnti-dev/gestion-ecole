from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from main.models import Etudiant
from api.serializers.etudiant_serializer import EtudiantSerializer
from rest_framework import status 
from rest_framework.decorators import api_view

@api_view()
def list_etudiant(request):
    return Response(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view()
def create_etudiant(request,pk):
    return Response(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view()
def detail_etudiant(request,pk):
    return Response(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view()
def update_etudiant(request,pk):
    return Response(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view()
def delete_etudiant(request,pk):
    return Response(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view()
def get_niveauEtudiant(request,etudiant):
    return Response(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view()
def enregistrer_seance(request):
    return Response(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view()
def modifier_seance(request):
    return Response(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view()
def supprimer_seance(request, seance_id):
    return Response(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view()
def changer_secretaire(request):
    return Response(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view()
def changer_delegue(request):
    return Response(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view()
def gestion_classe(request):
    return Response(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view()
def info_seance(request, seance_id):
    return Response(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view()
def valider_seance(request,seance_id):
    return Response(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view()
def signature_prof(request):
    return Response(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view()
def cahier_de_text(request):
    return Response(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view()
def liste_seance(request):
    return Response(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view()   
def liste_seance_etudiant(request):
    return Response(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view()    
def imprimer(request):
    return Response(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view()    
def carte_etudiant(request,id):
    return Response(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)