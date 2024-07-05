from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework import status 
from rest_framework.decorators import api_view
from main.models import Enseignant
from api.serializers.enseignant_serializer import EnseignantSerializer
@api_view(["GET"])
def list_enseignant(request):
    """Affiche la liste des enseignants
    """
    enseignants=Enseignant.objects.all()
    print("liste",enseignants)
    serializer=EnseignantSerializer(enseignants,many=True)
    return Response(serializer.data,status=status.HTTP_200_OK)


@api_view(["POST"])
def create_enseignant(request):
    """view to create enseignant
    """
    try:
        serializer=EnseignantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(status=status.HTTP_201_CREATED)
    except:
        return Response(serializer.errors,status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PUT"])
def update_enseignant(request,pk):
    
    try:
        enseignant=get_object_or_404(Enseignant,pk=pk)
        serializer=EnseignantSerializer(enseignant,data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(status=status.HTTP_201_CREATED)
    except Enseignant.DoesNotExist:
        return Response(data={},status=status.HTTP_400_BAD_REQUEST)

@api_view(["DELETE"])
def delete_enseignant(request,pk):
    try:
        enseignant=get_object_or_404(Enseignant,pk=pk)
        enseignant.delete()
        return Response(status=status.HTTP_200_OK)
    except Enseignant.DoesNotExist:
        return Response(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def detail_enseignant(request,pk):
    """function view to detail enseignant"""
    try:
        enseignant=get_object_or_404(Enseignant,pk=pk)
        serializer=EnseignantSerializer(enseignant)
        return Response(serializer.data,status=status.HTTP_200_OK)
    except Enseignant.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
def get_certificat_travail_enseignant(requeste):
    return Response(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################################################################
@api_view(["GET"])
def list_informations_enseignants(request):
    return Response(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def enregistrer_informations(request):
    return Response(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(["GET"])
def enseignant_inactif(request):
    return Response(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def importer_les_enseignants(request):
        return Response(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


