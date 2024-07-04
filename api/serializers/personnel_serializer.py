from rest_framework import serializers
from django.contrib.auth.models import Group
from main.models import Personnel

class PersonnelSerializer(serializers.ModelSerializer):
    class Meta:
        model=Personnel
        fields=(
            "nom","prenom","datenaissance","sexe",
            "lieunaissance","contact","email","adresse",
            "prefecture","carte_identity","nationalite","salaireBrut",
            "nbreJrsCongesRestant","nbreJrsConsomme","qualification_professionnel",
            "nombre_de_personnes_en_charge","nif",
            "numero_cnss", #"dernierdiplome",
            
            )