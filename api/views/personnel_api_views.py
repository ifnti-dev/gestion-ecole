from main.models import Personnel
from ..serializers.personnel_serializer import PersonnelSerializer
from django.http import JsonResponse
from rest_framework import status 
from rest_framework.decorators import api_view


# @api_view()
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
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def delete_personnel(request,id):
    """
        function to delete a personnel by id
    """
    return JsonResponse(data={"id":id},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def update_personnel(request,id):
    """
        fucntion update personnel by id
    """
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def form_demander_conge(request):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def imprimer_demande_conge(request):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def accorder_conge(request):
    return Response(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)