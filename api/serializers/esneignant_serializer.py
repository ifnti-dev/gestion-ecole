from rest_framework import serializers
from main.models import Enseignant

class Enseignant(serializers.ModelSerializer):
    class Meta:
        model=Enseignant
        fields='__all__'