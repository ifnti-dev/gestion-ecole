from main.models import Ue
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse
from rest_framework import status


def list_ue(request):
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def create_ue(request):
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def update_ue(request, pk):
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def delete_ue(request, pk):
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def detail_ue(request, pk):
    return JsonResponse(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

