import datetime
from django.http import JsonResponse
from requests import Response
from rest_framework import status 
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from api.serializers.conges_serializer import CongeSerializer
from main.models import Conge
from main.pdfMaker import generate_pdf

@api_view(['GET'])
def formulaire_demande_conges(request,pk):
    try:
        conge = get_object_or_404(Conge, pk=pk) 
        role = conge.personnel.getrole().capitalize()
        if conge.valider == 'Actif':
            conge.valider = "Congés accordé"
            conge.motif_refus = "none"
        elif conge.valider == 'Inactif':
            conge.valider = "Congés refusé"

        date_debut_formatted = datetime.strptime(str(conge.date_et_heure_debut), "%Y-%m-%d").strftime("%d %B %Y")
        date_fin_formatted = datetime.strptime(str(conge.date_et_heure_debut), "%Y-%m-%d").strftime("%d %B %Y")

        context = {
            "conge": conge,
            "role" : role,
            "date_debut_formatted":date_debut_formatted,
            "date_fin_formatted":date_fin_formatted,

        }
        latex_input = 'formulaire_de_demande_de_conges'
        latex_ouput = 'generated_formulaire_de_demande_de_conges'
        pdf_file = 'pdf_formulaire_de_demande_de_conges'

        # génération du pdf
        generate_pdf(context, latex_input, latex_ouput, pdf_file)
         # visualisation du pdf dans le navigateur
        with open('media/pdf/' + str(pdf_file) + '.pdf', 'rb') as f:
            pdf_preview = f.read()
            response = Response(pdf_preview, content_type='application/pdf',status=status.HTTP_200_OK)
            response['Content-Disposition'] = 'inline;filename=pdf_file.pdf'
            return response

    except Conge.DoesNotExist:
        return Response({"error": "Congé non trouvé"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def imprimer_demande_conge(request):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def accorder_conge(request):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def list_conge(request):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
def create_conge(request):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def update_conge(request, id):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def demandes_validees(request, id):
    return JsonResponse(data={},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

