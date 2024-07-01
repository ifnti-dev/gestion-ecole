from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from main.models import Etudiant
from api.serializers.etudiant_serializer import EtudiantSerializer
from rest_framework import status 

@csrf_exempt
def etudiant_list(request):
    # if request.method == 'GET':
    #     etudiants = Etudiant.objects.all()
    #     serializer = EtudiantSerializer(etudiants, many=True)
    #     return JsonResponse(serializer.data, safe=False)
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
def create_etudiant(request):
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
def detail_etudiant(request,pk):
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
def update_etudiant(request,pk):
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
def delete_etudiant(request,pk):
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
def get_niveauEtudiant(request,etudiant):
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
def enregistrer_seance(request):
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)