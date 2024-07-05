import datetime

from django.shortcuts import get_object_or_404
from main.models import Conge, Personnel
from api.serializers.personnel_serializer import PersonnelSerializer
from django.http import JsonResponse
from rest_framework import status 
from rest_framework.decorators import api_view

######today
from django.contrib.auth.models import Group
from rest_framework.response import Response

from main.pdfMaker import generate_pdf
@api_view(['GET'])
def list_personnel(request):
    """
        function to get the personnels
    """ 
    personnels=Personnel.objects.all()
    serializer=PersonnelSerializer(personnels,many=True)
    
    return Response(serializer.data,status=status.HTTP_200_OK)

@api_view(['POST'])
def create_personnel(request):
    """
    view api to create a new personnel
    """
    try:
        serializer=PersonnelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            return Response(serializer.data,status=status.HTTP_201_CREATED)
    except:
          return Response(serializer.data,status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_personnel(request,pk):
    """
        view to delete a personnel 
    """
    try:
       personnel=Personnel.objects.get(pk=pk)
       personnel.delete()
       return Response(status=status.HTTP_200_OK)
    except Personnel.DoesNotExist:
        Response(status=status.HTTP_404_NOT_FOUND)
   

@api_view(['PUT'])
def update_personnel(request,pk):
    """
        view to update personnel 
    """
    try:

        personnel=Personnel.objects.get(pk=pk)
        serializer=PersonnelSerializer(personnel,data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data,status=status.HTTP_200_OK)
    except:
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['GET'])
def detail_personnel(request,pk):
    """
    view to detail personnel
    """
    try:
        personnel=Personnel.objects.get(pk=pk)
        serializer=PersonnelSerializer(personnel)
        return Response(serializer.data,status=status.HTTP_200_OK)

    except:
        return Response(status=status.HTTP_404_NOT_FOUND)



