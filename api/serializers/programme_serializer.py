import django.db
from rest_framework import serializers
from main.models import Programme

class ProgrammeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programme
        fields = '__all__'