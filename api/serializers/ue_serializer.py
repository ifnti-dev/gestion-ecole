import django.db
from rest_framework import serializers
from main.models import Ue


class UeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ue
        fields = '__all__'