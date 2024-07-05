from rest_framework import serializers
from main.models import Conge

class CongeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Conge
        fields=("nature","autre_nature",
                "date_et_heure_debut","date_et_heure_fin",
                "personnel","motif_refus","valider",
                "nombre_de_jours_de_conge","annee_universitaire",
                )