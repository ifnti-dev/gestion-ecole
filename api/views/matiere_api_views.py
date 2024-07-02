#from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
#from main.models import Matiere
#from api.serializers.matiere_serializer import MatiereSerializer
from rest_framework import status 
from rest_framework.decorators import api_view

#@csrf_exempt
@api_view(['GET'])
def list_matiere(request):
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#@csrf_exempt
@api_view(['GET'])
def create_matiere(request):
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
#@csrf_exempt
@api_view(['PUT'])
def update_matiere(request, pk):
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 

#@csrf_exempt
@api_view(['DELETE'])
def delete_matiere(request, pk):
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
#@csrf_exempt
@api_view(['GET'])
def detail_matiere(request, pk):
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 

