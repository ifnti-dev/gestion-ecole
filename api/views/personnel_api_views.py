from main.models import Personnel
from api.serializers.personnel_serializer import PersonnelSerializer
from django.http import JsonResponse
from rest_framework import status 
from rest_framework.decorators import api_view


@api_view(['GET'])
def list_personnel(request):
    """
        function to get the personnels
    """
    return JsonResponse(data={"message": "ok"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_personnel(request):
    """
    fucntion api to create a new personnel
    """
    print("ok")
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_personnel(request,pk):
    """
        function to delete a personnel 
    """
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
def update_personnel(request,pk):
    """
        fucntion update personnel 
    """
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def detail_personnel(request,pk):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL)


@api_view(['POST'])
def form_demander_conge(request):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def imprimer_demande_conge(request):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def accorder_conge(request):
    return Response(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)