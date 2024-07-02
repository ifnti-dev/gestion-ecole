from rest_framework import serializers
from main.models import Personnel
class PersonnelSerializer(serializers.ModelSerializer):
    class Meta:
        model=Personnel
        fields='__all__'