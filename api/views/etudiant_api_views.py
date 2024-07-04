from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from main.models import Etudiant
from api.serializers.etudiant_serializer import EtudiantSerializer
from rest_framework import status 
from rest_framework.decorators import api_view

@csrf_exempt
def etudiant_list(request):
    # if request.method == 'GET':
    #     etudiants = Etudiant.objects.all()
    #     serializer = EtudiantSerializer(etudiants, many=True)
    #     return JsonResponse(serializer.data, safe=False)
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def importer_data_etudiants(request):
    """_Cette vue permet d'importer les données etudiants via un fichier xlsx
    """
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
