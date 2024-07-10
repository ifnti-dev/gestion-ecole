from api.serializers.etudiant_serializer import UeSerializer
from main.models import Ue
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status

@api_view(['GET'])
def list_ue(request):
    # if request.method == 'GET':
    #     listes_ues = Ue.objects.all()
    #     ues_serializer = UeSerializer(listes_ues, many=True)
    #     return JsonResponse(ues_serializer.data)
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_ue(request):
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def update_ue(request, pk):
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_ue(request, pk):
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def detail_ue(request, pk):
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

































