from api.serializers.etudiant_serializer import UeSerializer
from main.models import Ue
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status

@api_view(['GET'])
def list_ue(request):
    """
        fonction d'affichage des ues
    """
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_ue(request):
    """
        fonction de création des ues
    """
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def update_ue(request, pk):
    """
        fonction de mise à jour des ues
    """
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_ue(request, pk):
    """
        fonction de suppression des ues
    """
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def detail_ue(request, pk):
    """
        fonction de details d'une  ues
    """
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

































