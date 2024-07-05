from django.http import JsonResponse
from rest_framework import status 
from rest_framework.decorators import api_view



@api_view(["GET"])
def get_semestres(request):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["PUT"])
def cloturer_semestre(request,pk):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["PUT"])
def reactiver_semestre(request,pk):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def historique_semestre(request):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def ajout_semestre_etudiant(niveau, promotion, annees):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)