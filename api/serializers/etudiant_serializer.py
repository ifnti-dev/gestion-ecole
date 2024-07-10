import django.db
from rest_framework import serializers
from main.models import Etudiant, Ue

class EtudiantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etudiant
        fields = '__all__'

class UeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ue
        fields = '__all__'