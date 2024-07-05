from rest_framework import serializers
from main.models import Enseignant

class EnseignantSerializer(serializers.ModelSerializer):
    class Meta:
        model=Enseignant
        fields=(
            "type","specialite",
            "personnel",
        )