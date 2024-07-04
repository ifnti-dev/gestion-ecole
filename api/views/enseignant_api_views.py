from api.serializers import enseignant_serializer
from django.http import JsonResponse
from rest_framework import status 
from rest_framework.decorators import api_view


@api_view(["GET"])
def list_enseignant(request):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def create_enseignant(request):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["PUT"])
def update_enseignant(request,pk):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["DELETE"])
def delete_enseignant(request,pk):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def detail_enseignant(request,pk):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def get_certificat_travail_enseignant(requeste):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################################################################
@api_view(["GET"])
def list_informations_enseignants(request):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def enregistrer_informations(request):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(["GET"])
def enseignant_inactif(request):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def importer_les_enseignants(request):
        return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


