import django.db
from rest_framework import serializers
from main.models import Matiere

class MatiereSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matiere
        fields = '__all__'